# hmbot-wizedev

Wize Agency / Hermes bot — research arsenal, scripts, skills.

**Owner:** iGeezmo  
**Stack:** Hermes CLI agent (MiniMax-M3) + MCP matrix  
**Started:** 2026-08-29

## Что внутри

- `skills/deep-research/` — паттерн IterResearch (PLAN → QUERY → SEARCH → EXTRACT → SYNTHESIZE → DECIDE) для глубокого ресёрча
- `scripts/extract_memory.py` — извлечение памяти из чата (bullets, inline commands, structured facts)
- `scripts/tool_policy.py` — классификация инструментов (READ/WRITE/DESTRUCTIVE) + детекция деструктивных shell-паттернов
- `scripts/parse_githubradar.py` — discovery-парсер публичного Telegram-канала `@GitHubRadar`; извлекает кандидаты GitHub без автоматической рекомендации
- `config/digest-sources.yaml` — реестр первичных и discovery-источников с правилами верификации
- `docs/ai-digest.md` — накопительное зеркало прикладного ИИ-дайджеста для использования ботом и сайтом
- `docs/odysseus-analysis-2026-08-29.md` — разбор кода Odysseus (1151 файл, 489k строк)
- `archive/memory-sample.json` — пример наполненной памяти

## ИИ-дайджест

Каноническая исследовательская политика находится в [`iGeezmo/0dai`](https://github.com/iGeezmo/0dai). В этом репозитории хранится delivery-oriented зеркало, чтобы Hermes/Wize-бот мог читать дайджест без зависимости от документационного дерева 0dai.

`GitHubRadar` используется только как источник обнаружения кандидатов. Текст поста, популярность проекта и сам факт публикации не считаются доказательством качества. Перед попаданием в дайджест кандидат должен быть перепроверен по самому репозиторию, официальной документации, releases, лицензии, security surface и текущему project fit.

## История

Создано в ходе сессии 2026-08-29: изучили self-hosted AI workspace Odysseus, извлекли лучшие практики (IterResearch, auto-skill audit, tool policy, memory extraction), реализовали как переиспользуемые артефакты.

## Использование

См. файлы в соответствующих директориях. Skills подключаются в Hermes через `~/.hermes/skills/`.
