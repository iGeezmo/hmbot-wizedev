#!/usr/bin/env python3
"""Parse public Telegram preview posts into unverified GitHub candidates.

This script is intentionally discovery-only. It never scores or recommends a
repository and never treats Telegram copy as evidence. Downstream scouting must
validate the repository, release activity, license, security posture, pricing
and project fit against primary sources.

Examples:
    python scripts/parse_githubradar.py --pages 3 --limit 100
    python scripts/parse_githubradar.py --html /tmp/githubradar.html --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

DEFAULT_CHANNEL = "GitHubRadar"
DEFAULT_TIMEOUT_SECONDS = 20.0
USER_AGENT = (
    "Mozilla/5.0 (compatible; hmbot-wizedev-githubradar-parser/1.0; "
    "+https://github.com/iGeezmo/hmbot-wizedev)"
)

_RESERVED_GITHUB_ROOTS = {
    "about",
    "apps",
    "collections",
    "contact",
    "customer-stories",
    "enterprise",
    "events",
    "explore",
    "features",
    "issues",
    "login",
    "marketplace",
    "new",
    "notifications",
    "orgs",
    "pricing",
    "pulls",
    "search",
    "security",
    "settings",
    "site",
    "sponsors",
    "topics",
    "trending",
}


@dataclass(slots=True)
class TelegramPost:
    source: str
    post_id: int
    published_at: str | None
    text: str
    repository_urls: list[str] = field(default_factory=list)
    post_url: str | None = None
    verification_status: str = "unverified_discovery"


class TelegramPreviewParser(HTMLParser):
    """Minimal parser for Telegram public channel preview HTML."""

    def __init__(self, channel: str) -> None:
        super().__init__(convert_charrefs=True)
        self.channel = channel
        self.posts: list[TelegramPost] = []
        self._current: dict[str, object] | None = None
        self._post_div_depth = 0
        self._text_div_depth: int | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = {key: value or "" for key, value in attrs}

        if self._current is None:
            data_post = attributes.get("data-post")
            classes = set(attributes.get("class", "").split())
            if (
                tag == "div"
                and data_post
                and "tgme_widget_message" in classes
            ):
                post_id = _parse_post_id(data_post)
                if post_id is None:
                    return
                self._current = {
                    "post_id": post_id,
                    "published_at": None,
                    "text_parts": [],
                    "links": [],
                }
                self._post_div_depth = 1
            return

        if tag == "div":
            self._post_div_depth += 1
            classes = set(attributes.get("class", "").split())
            if "tgme_widget_message_text" in classes:
                self._text_div_depth = self._post_div_depth

        if tag == "a":
            href = attributes.get("href")
            if href:
                links = self._current["links"]
                assert isinstance(links, list)
                links.append(href)

        if tag == "time" and attributes.get("datetime"):
            self._current["published_at"] = attributes["datetime"]

        if self._text_div_depth is not None and tag in {"br", "p", "li"}:
            parts = self._current["text_parts"]
            assert isinstance(parts, list)
            parts.append("\n")

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._current is None or self._text_div_depth is None:
            return
        parts = self._current["text_parts"]
        assert isinstance(parts, list)
        parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._current is None or tag != "div":
            return

        if self._text_div_depth == self._post_div_depth:
            self._text_div_depth = None

        self._post_div_depth -= 1
        if self._post_div_depth > 0:
            return

        post_id = int(self._current["post_id"])
        text_parts = self._current["text_parts"]
        links = self._current["links"]
        assert isinstance(text_parts, list)
        assert isinstance(links, list)

        text = _normalise_text("".join(str(part) for part in text_parts))
        repositories = sorted(
            {
                normalised
                for link in links
                if (normalised := normalise_github_repository_url(str(link)))
            }
        )

        self.posts.append(
            TelegramPost(
                source=f"telegram:@{self.channel}",
                post_id=post_id,
                published_at=_normalise_datetime(
                    str(self._current.get("published_at") or "")
                ),
                text=text,
                repository_urls=repositories,
                post_url=f"https://t.me/{quote(self.channel)}/{post_id}",
            )
        )

        self._current = None
        self._post_div_depth = 0
        self._text_div_depth = None


def _parse_post_id(data_post: str) -> int | None:
    try:
        return int(data_post.rsplit("/", 1)[-1])
    except (TypeError, ValueError):
        return None


def _normalise_datetime(value: str) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.isoformat()


def _normalise_text(value: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def normalise_github_repository_url(raw_url: str) -> str | None:
    """Return a canonical owner/repository URL or None for non-repository links."""

    cleaned = raw_url.strip().rstrip(".,;:!?)]}\"")
    parsed = urlparse(cleaned)
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None

    segments = [unquote(segment) for segment in parsed.path.split("/") if segment]
    if len(segments) < 2:
        return None

    owner, repository = segments[0], segments[1]
    if owner.lower() in _RESERVED_GITHUB_ROOTS:
        return None
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository:
        return None
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", owner):
        return None
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", repository):
        return None

    return f"https://github.com/{owner}/{repository}"


def fetch_preview_html(url: str, timeout_seconds: float) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ru,en;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"Telegram preview returned HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not fetch Telegram preview: {exc.reason}") from exc


def parse_html(html: str, channel: str) -> list[TelegramPost]:
    parser = TelegramPreviewParser(channel=channel)
    parser.feed(html)
    parser.close()
    return parser.posts


def collect_channel_posts(
    channel: str,
    pages: int,
    limit: int,
    timeout_seconds: float,
    pause_seconds: float,
) -> list[TelegramPost]:
    collected: dict[int, TelegramPost] = {}
    before: int | None = None

    for page_number in range(pages):
        base = f"https://t.me/s/{quote(channel)}"
        url = base if before is None else f"{base}?before={before}"
        html = fetch_preview_html(url, timeout_seconds=timeout_seconds)
        posts = parse_html(html, channel=channel)
        if not posts:
            break

        new_count = 0
        for post in posts:
            if post.post_id not in collected:
                collected[post.post_id] = post
                new_count += 1
        if new_count == 0:
            break

        before = min(post.post_id for post in posts)
        if len(collected) >= limit:
            break
        if page_number + 1 < pages and pause_seconds > 0:
            time.sleep(pause_seconds)

    ordered = sorted(collected.values(), key=lambda item: item.post_id, reverse=True)
    return ordered[:limit]


def serialise_posts(
    posts: Sequence[TelegramPost],
    output_format: str,
    include_without_repository: bool,
) -> str:
    filtered = [
        post
        for post in posts
        if include_without_repository or post.repository_urls
    ]
    records = [asdict(post) for post in filtered]
    if output_format == "json":
        return json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    return "".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in records
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract unverified GitHub repository candidates from a public "
            "Telegram channel preview."
        )
    )
    parser.add_argument("--channel", default=DEFAULT_CHANNEL)
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--pause", type=float, default=0.5)
    parser.add_argument("--html", type=Path, help="Parse an existing HTML file instead")
    parser.add_argument("--output", type=Path, help="Write output to a file")
    parser.add_argument("--format", choices=("json", "jsonl"), default="jsonl")
    parser.add_argument(
        "--include-without-repository",
        action="store_true",
        help="Include channel posts that contain no GitHub repository link",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    if args.pages < 1 or args.limit < 1:
        print("--pages and --limit must be positive", file=sys.stderr)
        return 2

    try:
        if args.html:
            html = args.html.read_text(encoding="utf-8")
            posts = parse_html(html, channel=args.channel)
        else:
            posts = collect_channel_posts(
                channel=args.channel,
                pages=args.pages,
                limit=args.limit,
                timeout_seconds=args.timeout,
                pause_seconds=args.pause,
            )
        payload = serialise_posts(
            posts,
            output_format=args.format,
            include_without_repository=args.include_without_repository,
        )
    except (OSError, RuntimeError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
