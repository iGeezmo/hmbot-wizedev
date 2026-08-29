#!/bin/bash
# Парсит @GitHubRadar и складывает JSON-дамп
# Запускается через cron каждые 12 часов

set -e
TS=$(date -u +%Y%m%dT%H%M%SZ)
DUMP_DIR=/root/wize-arsenal/data/tg_dumps
LOG=/root/.hermes/logs/tg_parser.log

mkdir -p "$DUMP_DIR" "$(dirname "$LOG")"

# Парсим последние 50 постов (web mode — без auth)
python3 /root/wize-arsenal/scripts/tg_parser.py \
    --channel GitHubRadar \
    --limit 50 \
    --format json \
    --out "$DUMP_DIR/githubradar-$TS.json" \
    2>> "$LOG"

# Сводка для быстрого чтения
python3 /root/wize-arsenal/scripts/tg_parser.py \
    --channel GitHubRadar \
    --limit 50 \
    --summary \
    > "$DUMP_DIR/githubradar-$TS.summary.json" \
    2>> "$LOG"

# Удаляем дампы старше 30 дней (оставляем свежие)
find "$DUMP_DIR" -name 'githubradar-*.json' -mtime +30 -delete

echo "[$(date -Iseconds)] tg_parser ok: $TS" >> "$LOG"
