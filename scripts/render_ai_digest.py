#!/usr/bin/env python3
"""Render docs/ai-digest.md from immutable dated entry files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRY_DIR = ROOT / "docs" / "ai-digest-entries"
OUTPUT = ROOT / "docs" / "ai-digest.md"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(message: str) -> None:
    print(f"ai-digest render error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_entries() -> list[tuple[str, str]]:
    if not ENTRY_DIR.is_dir():
        fail(f"missing entry directory: {ENTRY_DIR}")

    entries: list[tuple[str, str]] = []
    seen_dates: set[str] = set()

    for path in sorted(ENTRY_DIR.glob("*.md"), reverse=True):
        date = path.stem
        if date.lower() == "readme":
            continue
        if not DATE_RE.fullmatch(date):
            fail(f"invalid entry filename: {path.name}")
        if date in seen_dates:
            fail(f"duplicate date: {date}")

        text = path.read_text(encoding="utf-8").strip()
        expected_heading = f"## {date}"
        first_line = text.splitlines()[0] if text else ""
        if first_line != expected_heading:
            fail(
                f"{path.name} must start with {expected_heading!r}; "
                f"found {first_line!r}"
            )
        if "<!-- DAILY_ENTRIES -->" in text:
            fail(f"entry must not contain the index marker: {path.name}")

        seen_dates.add(date)
        entries.append((date, text))

    if not entries:
        fail("no dated entries found")
    return entries


def render(entries: list[tuple[str, str]]) -> str:
    latest_date = entries[0][0]
    header = f'''---
title: "Ежедневный прикладной ИИ-дайджест"
type: doc
created: 2026-08-29
updated: {latest_date}
managed: true
mirror:
  canonical_repository: "iGeezmo/0dai"
  canonical_path: "docs/ai-digest.md"
---

# Ежедневный прикладной ИИ-дайджест

Публичное зеркало накопительного прикладного ИИ-дайджеста для `hmbot-wizedev`.

Новые выпуски хранятся как отдельные файлы в `docs/ai-digest-entries/` и автоматически собираются в этот документ. Полный исторический архив до начала зеркала остаётся в каноническом приватном документе `iGeezmo/0dai/docs/ai-digest.md`.

<!-- DAILY_ENTRIES -->
'''
    return header.rstrip() + "\n\n" + "\n\n".join(text for _, text in entries) + "\n"


def main() -> None:
    entries = load_entries()
    content = render(entries)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Rendered {len(entries)} entries to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
