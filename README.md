# hmbot-wizedev

Wize Agency / Hermes bot — research arsenal, scripts, skills.

**Owner:** iGeezmo  
**Stack:** Hermes CLI agent (MiniMax-M3) + MCP matrix  
**Started:** 2026-08-29

## Что внутри

- `skills/deep-research/` — паттерн IterResearch (PLAN → QUERY → SEARCH → EXTRACT → SYNTHESIZE → DECIDE) для глубокого ресёрча
- `scripts/extract_memory.py` — извлечение памяти из чата (bullets, inline commands, structured facts)
- `scripts/tool_policy.py` — классификация инструментов (READ/WRITE/DESTRUCTIVE) + детекция деструктивных shell-паттернов
- `docs/odysseus-analysis-2026-08-29.md` — разбор кода Odysseus (1151 файл, 489k строк)
- `archive/memory-sample.json` — пример наполненной памяти

## История

Создано в ходе сессии 2026-08-29: изучили self-hosted AI workspace Odysseus, извлекли лучшие практики (IterResearch, auto-skill audit, tool policy, memory extraction), реализовали как переиспользуемые артефакты.

## Использование

См. файлы в соответствующих директориях. Skills подключаются в Hermes через `~/.hermes/skills/`.
