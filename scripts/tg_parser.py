#!/usr/bin/env python3
"""
Telegram Channel Parser — для @GitHubRadar и подобных каналов.

Поддерживает 2 стратегии:
1. WEB (default) — парсит публичную страницу https://t.me/s/<channel>
   - Не нужна авторизация
   - Лимит: ~20 последних постов
   - Хорошо для публичных каналов с открытым preview

2. TELETHON — через userbot API
   - Нужны TELEGRAM_API_ID и TELEGRAM_API_HASH
   - Лимит: до 1000 постов за раз
   - Для закрытых каналов (если ты подписан)

Использование:
    python3 tg_parser.py --channel GitHubRadar
    python3 tg_parser.py --channel GitHubRadar --limit 50 --format json
    python3 tg_parser.py --channel GitHubRadar --since 2026-08-20
    python3 tg_parser.py --channel GitHubRadar --mode telethon

Env vars для telethon:
    TELEGRAM_API_ID, TELEGRAM_API_HASH
    (опционально) TELEGRAM_SESSION — путь к .session файлу
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


# === Data ===

@dataclass
class TgMessage:
    id: int
    channel: str
    text: str
    date: str  # ISO 8601
    views: int
    forwards: int
    replies: int
    url: str
    media: list = field(default_factory=list)
    links: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


# === Web parser ===

def parse_web(channel: str, limit: int = 20, since: Optional[str] = None) -> list[TgMessage]:
    """
    Парсит публичную веб-страницу t.me/s/<channel>.
    Возвращает список сообщений (от старых к новым).
    """
    # username нормализация
    channel = channel.lstrip('@')
    url = f"https://t.me/s/{channel}"

    messages = []
    try:
        r = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR fetching {url}: {e}", file=sys.stderr)
        return []

    soup = BeautifulSoup(r.text, 'html.parser')

    # div.tgme_widget_message_wrap оборачивает каждое сообщение
    wraps = soup.find_all('div', class_='tgme_widget_message_wrap')

    for wrap in wraps:
        msg_div = wrap.find('div', class_='tgme_widget_message')
        if not msg_div:
            continue

        # ID
        msg_id_str = msg_div.get('data-post', '')
        msg_id = int(msg_id_str.split('/')[-1]) if msg_id_str else 0

        # Дата
        time_span = wrap.find('time')
        date_iso = time_span.get('datetime') if time_span and time_span.get('datetime') else ''

        # since-фильтр
        if since and date_iso < since:
            continue

        # Текст
        text_div = wrap.find('div', class_='tgme_widget_message_text')
        text = text_div.get_text(separator='\n', strip=True) if text_div else ''

        # Метрики
        views = 0
        views_span = wrap.find('span', class_='tgme_widget_message_views')
        if views_span:
            v = views_span.get_text(strip=True).replace('K', '000').replace('M', '000000')
            try:
                views = int(re.sub(r'[^0-9]', '', v) or 0)
            except ValueError:
                pass

        forwards = 0
        fwd_span = wrap.find('span', class_='tgme_widget_message_forwards')
        if fwd_span:
            try:
                forwards = int(re.sub(r'[^0-9]', '', fwd_span.get_text(strip=True)) or 0)
            except ValueError:
                pass

        replies = 0
        reply_span = wrap.find('span', class_='tgme_widget_message_replies')
        if reply_span:
            try:
                replies = int(re.sub(r'[^0-9]', '', reply_span.get_text(strip=True)) or 0)
            except ValueError:
                pass

        # URL
        post_url = f"https://t.me/{channel}/{msg_id}" if msg_id else url

        # Медиа
        media = []
        if wrap.find('a', class_='tgme_widget_message_photo'):
            media.append('photo')
        if wrap.find('video'):
            media.append('video')

        # Ссылки
        links = re.findall(r'https?://[^\s<>"]+', text)

        messages.append(TgMessage(
            id=msg_id, channel=channel, text=text, date=date_iso,
            views=views, forwards=forwards, replies=replies,
            url=post_url, media=media, links=links
        ))

        if len(messages) >= limit:
            break

    return messages


# === Telethon parser ===

def parse_telethon(channel: str, limit: int = 100, since: Optional[str] = None) -> list[TgMessage]:
    """Через userbot API (нужны креды)."""
    try:
        from telethon.sync import TelegramClient
        from telethon.tl.functions.messages import GetHistoryRequest
    except ImportError:
        print("ERROR: pip install telethon", file=sys.stderr)
        return []

    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    if not api_id or not api_hash:
        print("ERROR: set TELEGRAM_API_ID and TELEGRAM_API_HASH env vars", file=sys.stderr)
        return []

    session = os.getenv('TELEGRAM_SESSION', '/tmp/tg_parser_session')

    client = TelegramClient(session, int(api_id), api_hash)
    client.start()

    channel = channel.lstrip('@')
    messages = []

    try:
        entity = client.get_entity(channel)
    except Exception as e:
        print(f"ERROR: cannot get {channel}: {e}", file=sys.stderr)
        client.disconnect()
        return []

    offset_id = 0
    while len(messages) < limit:
        history = client(GetHistoryRequest(
            peer=entity, limit=min(100, limit - len(messages)),
            offset_date=None, offset_id=offset_id, max_id=0, min_id=0, add_offset=0, hash=0
        ))
        if not history.messages:
            break

        for msg in history.messages:
            if not msg.message:
                continue
            date_iso = msg.date.isoformat() if msg.date else ''
            if since and date_iso < since:
                client.disconnect()
                return messages
            messages.append(TgMessage(
                id=msg.id, channel=channel, text=msg.message, date=date_iso,
                views=getattr(msg, 'views', 0) or 0,
                forwards=getattr(msg, 'forwards', 0) or 0,
                replies=getattr(msg, 'replies', 0) and msg.replies.replies or 0,
                url=f"https://t.me/{channel}/{msg.id}",
                media=['photo'] if msg.photo else (['video'] if msg.video else []),
                links=re.findall(r'https?://[^\s<>"]+', msg.message)
            ))

        offset_id = history.messages[-1].id
        if len(history.messages) < 100:
            break

    client.disconnect()
    return messages


# === Filters / enrichments ===

GITHUB_FULL_RE = re.compile(r'https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?')
GITHUB_SHORT_RE = re.compile(r'(?:^|[\s\n>])([A-Za-z][A-Za-z0-9_.-]{1,39}/[A-Za-z][A-Za-z0-9_.-]{1,99})')
HASHTAG_RE = re.compile(r'#\w+')


def extract_github_repos(messages: list[TgMessage]) -> list[dict]:
    """
    Извлекает GitHub-репозитории (полные URL или короткие user/repo).
    """
    out = []
    for m in messages:
        seen = set()
        # Полные URL
        for link in m.links:
            m_full = GITHUB_FULL_RE.search(link)
            if m_full:
                repo = m_full.group(0)
                if repo not in seen:
                    seen.add(repo)
                    out.append({
                        'repo': repo,
                        'format': 'full',
                        'context': m.text[:200],
                        'tg_message_id': m.id,
                        'tg_url': m.url,
                        'date': m.date,
                    })
        # Короткие user/repo в начале строки (формат GitHubRadar)
        for line in m.text.split('\n'):
            line = line.strip()
            m_short = GITHUB_SHORT_RE.match(line)
            if m_short and not line.startswith('http'):
                user_repo = m_short.group(1)
                if user_repo not in seen:
                    seen.add(user_repo)
                    out.append({
                        'repo': f'github.com/{user_repo}',
                        'format': 'short',
                        'context': m.text[:200],
                        'tg_message_id': m.id,
                        'tg_url': m.url,
                        'date': m.date,
                    })
    return out


def extract_top_topics(messages: list[TgMessage], top_n: int = 10) -> list[tuple[str, int]]:
    """Считает частые hashtags / темы."""
    from collections import Counter
    counter = Counter()
    for m in messages:
        for tag in HASHTAG_RE.findall(m.text):
            counter[tag.lower()] += 1
    return counter.most_common(top_n)


# === Main / CLI ===

def main():
    p = argparse.ArgumentParser(description='Telegram channel parser (GitHubRadar и др.)')
    p.add_argument('--channel', required=True, help='username без @ (например GitHubRadar)')
    p.add_argument('--mode', choices=['web', 'telethon'], default='web')
    p.add_argument('--limit', type=int, default=20, help='макс. сообщений (web: обычно 20)')
    p.add_argument('--since', help='ISO дата, после которой парсить (например 2026-08-20)')
    p.add_argument('--format', choices=['json', 'text', 'md'], default='text')
    p.add_argument('--out', help='путь к файлу (если не указан — stdout)')
    p.add_argument('--github-only', action='store_true', help='только сообщения с GitHub-ссылками')
    p.add_argument('--summary', action='store_true', help='показать сводку (топ-темы, статистика)')
    args = p.parse_args()

    if args.mode == 'telethon':
        messages = parse_telethon(args.channel, args.limit, args.since)
    else:
        messages = parse_web(args.channel, args.limit, args.since)

    if args.github_only:
        messages = [m for m in messages if any(GITHUB_FULL_RE.match(l) for l in m.links) or GITHUB_SHORT_RE.search(m.text)]

    if args.summary:
        gh = extract_github_repos(messages)
        topics = extract_top_topics(messages)
        summary = {
            'channel': args.channel,
            'mode': args.mode,
            'total_messages': len(messages),
            'total_github_links': len(gh),
            'date_range': [m.date for m in messages][-1:] + [m.date for m in messages][:1],
            'top_topics': topics,
            'avg_views': sum(m.views for m in messages) // max(len(messages), 1),
            'github_links_sample': gh[:5],
        }
        output = json.dumps(summary, ensure_ascii=False, indent=2)
    elif args.format == 'json':
        output = json.dumps([m.to_dict() for m in messages], ensure_ascii=False, indent=2)
    elif args.format == 'md':
        lines = [f'# @{args.channel}\n']
        for m in messages:
            lines.append(f'## [{m.date}]({m.url})\n')
            lines.append(f'**Views:** {m.views} | **Forwards:** {m.forwards}\n')
            lines.append(f'\n{m.text}\n\n---\n')
        output = '\n'.join(lines)
    else:
        # text
        lines = []
        for m in messages:
            lines.append(f'[{m.date}] {m.url}')
            lines.append(f'  views={m.views} forwards={m.forwards}')
            if m.media:
                lines.append(f'  media: {",".join(m.media)}')
            # превью текста
            preview = m.text[:300].replace('\n', ' ')
            if len(m.text) > 300:
                preview += '...'
            lines.append(f'  {preview}')
            if m.links:
                lines.append(f'  links: {", ".join(m.links[:3])}')
            lines.append('')
        output = '\n'.join(lines)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(output, encoding='utf-8')
        print(f'Wrote {len(messages)} messages to {args.out}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
