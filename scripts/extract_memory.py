#!/usr/bin/env python3
"""
Memory extraction по паттерну Odysseus (src/memory.py).

Три стратегии:
1. Bullet extraction — парсит "- ..." и "1. ..." из ответов ассистента
2. Inline commands — распознаёт "remember: X", "save: X", "note: X", "memorize: X"
3. Structured facts — детектит "X is Y", "X = Y", "X: Y" в сообщениях пользователя

Использование:
  echo "remember: любимое мороженое фисташка" | python3 extract_memory.py
  python3 extract_memory.py --from-chat /path/to/chat.json
  python3 extract_memory.py --from-file /path/to/transcript.txt
  python3 extract_memory.py --stdin
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Куда сохранять
MEMORY_FILE = Path('/root/.hermes/memory.json')

# Паттерны inline-команд памяти (Odysseus style)
INLINE_PATTERNS = [
    r'^(?:remember|memorize|save|note|store|запомни|сохрани|запиши)[:\-—]?\s+(.+)$',
    r'^(?:remember that|note that|запомни что|сохрани что)[:\-—]?\s+(.+)$',
]

# Паттерн bullet-point в ответах ассистента
BULLET_PATTERN = re.compile(r'^(?:[-*•]|\d+\.)\s+(.+?)\s*$')

# Паттерн для заголовков секций памяти в ассистентских ответах
MEMORY_SECTION_PATTERN = re.compile(
    r'(?:^|\n)##?\s*(?:memory|memories|запомни|важно|заметки|to remember|key facts)',
    re.IGNORECASE | re.MULTILINE
)

# Паттерны structured facts в сообщениях пользователя
FACT_PATTERNS = [
    r'^\s*([A-ZА-Я][\w\s]{2,40})\s+(?:is|=|:)\s+(.+?)\s*$',  # "Project: foo", "X is Y"
    r'^\s*мой\s+(.+?)\s+(?:—|--|-)\s+(.+?)\s*$',  # "мой email — x@y"
    r'^\s*я\s+(?:живу|работаю|использую|использую)\s+(.+?)\s*$',
]

# Минимальная длина значимого fact
MIN_FACT_LEN = 5
MAX_FACT_LEN = 200


def extract_inline_commands(text: str) -> list[dict]:
    """Ищет remember:/save:/memorize: и т.п. в начале строки."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        for pat in INLINE_PATTERNS:
            m = re.match(pat, line, re.IGNORECASE)
            if m:
                fact = m.group(1).strip()
                if MIN_FACT_LEN <= len(fact) <= MAX_FACT_LEN:
                    out.append({
                        'text': fact,
                        'source': 'inline_command',
                        'ts': datetime.now().isoformat(timespec='seconds')
                    })
                break
    return out


def extract_bullets(text: str) -> list[dict]:
    """Парсит bullet-points из текста. Извлекает только если в тексте есть
    секция с заголовком типа 'Memory', 'Запомни', 'Important' — иначе
    слишком много false positives."""
    out = []

    # Ищем секцию памяти
    section_match = MEMORY_SECTION_PATTERN.search(text)
    if not section_match:
        return out

    # Берём текст после заголовка
    after = text[section_match.end():]
    # До следующего заголовка (## или ===) или 2000 символов
    next_section = re.search(r'\n##\s|\n===', after[2000:] if len(after) > 2000 else after)
    chunk = after[:2000 + (next_section.start() if next_section else 0)] if next_section else after[:2000]

    for line in chunk.splitlines():
        line = line.strip()
        m = BULLET_PATTERN.match(line)
        if m:
            fact = m.group(1).strip()
            # Убираем markdown formatting
            fact = re.sub(r'\*\*?(.+?)\*\*?', r'\1', fact)
            fact = re.sub(r'`(.+?)`', r'\1', fact)
            fact = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', fact)
            if MIN_FACT_LEN <= len(fact) <= MAX_FACT_LEN:
                out.append({
                    'text': fact,
                    'source': 'bullet',
                    'ts': datetime.now().isoformat(timespec='seconds')
                })
    return out


def extract_structured_facts(text: str, role: str = 'user') -> list[dict]:
    """Детектит простые факты вида 'X is Y' в сообщениях пользователя."""
    if role != 'user':
        return []
    out = []
    for line in text.splitlines():
        line = line.strip()
        for pat in FACT_PATTERNS:
            m = re.match(pat, line)
            if m:
                fact = line
                if MIN_FACT_LEN <= len(fact) <= MAX_FACT_LEN:
                    out.append({
                        'text': fact,
                        'source': 'structured_fact',
                        'ts': datetime.now().isoformat(timespec='seconds')
                    })
                break
    return out


def extract_from_chat(messages: list[dict]) -> list[dict]:
    """Применяет все три стратегии к списку сообщений чата.
    Каждое сообщение: {role: 'user'|'assistant', content: str}"""
    out = []
    for msg in messages:
        content = msg.get('content', '')
        role = msg.get('role', 'user')
        if role == 'user':
            out.extend(extract_inline_commands(content))
            out.extend(extract_structured_facts(content, role))
        elif role == 'assistant':
            out.extend(extract_bullets(content))
    # Дедуп по тексту
    seen = set()
    unique = []
    for m in out:
        key = m['text'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(m)
    return unique


def load_memory() -> list[dict]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(entries: list[dict], merge: bool = True) -> list[dict]:
    if merge:
        existing = load_memory()
        existing.extend(entries)
        entries = existing
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    return entries


def main():
    parser = argparse.ArgumentParser(description='Memory extraction (Odysseus pattern)')
    parser.add_argument('--from-chat', help='JSON файл с массивом {role, content}')
    parser.add_argument('--from-file', help='Текстовый файл (plaintext transcript)')
    parser.add_argument('--stdin', action='store_true', help='Читать из stdin')
    parser.add_argument('--print-only', action='store_true', help='Не сохранять, только показать')
    parser.add_argument('--role', default='user', help='Роль для stdin (user/assistant)')
    args = parser.parse_args()

    facts = []
    if args.from_chat:
        messages = json.loads(Path(args.from_chat).read_text(encoding='utf-8'))
        facts = extract_from_chat(messages)
    elif args.from_file:
        content = Path(args.from_file).read_text(encoding='utf-8')
        if args.role == 'user':
            facts = extract_inline_commands(content)
            facts.extend(extract_structured_facts(content, args.role))
        else:
            facts = extract_bullets(content)
    elif args.stdin:
        content = sys.stdin.read()
        if args.role == 'user':
            facts = extract_inline_commands(content)
            facts.extend(extract_structured_facts(content, args.role))
        else:
            facts = extract_bullets(content)
    else:
        parser.print_help()
        return

    if not facts:
        print("No facts found.")
        return

    if args.print_only:
        for f in facts:
            print(f"[{f['source']}] {f['text']}")
        return

    saved = save_memory(facts, merge=True)
    print(f"Extracted {len(facts)} fact(s). Total in memory: {len(saved)}")
    for f in facts:
        print(f"  + [{f['source']}] {f['text']}")


if __name__ == '__main__':
    main()
