# Odysseus: что посмотрели

**Что это:** self-hosted AI workspace (chat + agents + research + docs + email + notes + tasks + calendar). Python + FastAPI, 495 endpoints, 489k строк, 1151 файл, 54 МБ. Лицензия AGPL-3.0.

**Где:** `/root/projects/odysseus/` (клонировано 2026-08-29, dev branch). Запускали на localhost:7000 — backend отвечает, UI работает без Node.

**Стек:** FastAPI + uvicorn, SQLAlchemy, pydantic, httpx, MCP SDK, ChromaDB (RAG), SearXNG (search), CalDAV, mcp_servers/, calendar/email/skills/tasks/notes routes.

## Топ-фичи которые имеет смысл перенять в Hermes

### 1. IterResearch (deep_research.py) ★★★
Паттерн глубокого ресёрча: PLAN → QUERY → SEARCH → EXTRACT → SYNTHESIZE → DECIDE. 8 раундов max, 5 мин timeout, parallel extraction, prior_report carryover для follow-up. У нас сейчас простой web_search — а тут полноценный research с эволюцией отчёта.
- Класс `DeepResearcher` (929 строк)
- Async, self-cancellable, с progress callbacks
- Tracking: queries_used, urls_fetched, providers_used, findings, evolving_report
- Можно сделать `skill: deep_research` в Hermes

### 2. Auto-skill audit & improvement (skills_routes.py) ★★★
LLM-оценка скиллов:
- `_eval_skill_necessity` — нужен ли вообще
- `_eval_skill_retrieval_precision` — насколько хорошо находит нужное
- `_improve_skill_md` — улучшает markdown по verdict
- `_run_skill_test_job` — прогоняет скилл на тестовой задаче
- `slash-catalog` — реестр /-команд
- `import-from-url` — загрузить скилл с любого URL
- `audit-all` + `audit-all/cancel` — аудит всех скиллов

Сейчас наши скиллы — просто markdown без автотестов. Можно добавить audit workflow: раз в неделю LLM проверяет каждый скилл и предлагает улучшения.

### 3. Memory system (memory.py) ★★
- `extract_memory_from_chat` — парсит bullet-points из ответов LLM
- `process_inline_memory_command` — распознаёт "remember: X", "memorize: X", "save: X"
- MemoryVectorStore через ChromaDB для семантического поиска
- `MemoryStoreUnreadable` exception с fallback на legacy migration

### 4. Visual reports (visual_report.py) ★★
Markdown → HTML с TOC, auto-linked URLs, embedded images, тематические стили (`_category_css`). 1933 строки. Превращает research output в красивые отчёты.

### 5. Tool system ★★
- `tool_index.py` — индекс инструментов
- `tool_policy.py` — политика доступа (read-only/write/destructive)
- `tool_approval_scopes.py` — требуется ли одобрение
- `tool_security.py` — URL safety, prompt injection protection
- 30+ tool_implementations

### 6. Provider system (model_routes.py) ★
OpenAI-compatible base_url поддержка любых провайдеров. Curated lists: openai, anthropic, zai, deepseek, groq, mistral, together, fireworks, google, xai, ollama, openrouter. Endpoint rewriting для Docker (host.docker.internal).

### 7. Agent loop (agent_loop.py)
6442 строки. Patterns: domain rules for tools, intent classification, slash-catalog, context message injection, MCP tool expansion. Слишком большой чтобы копировать, но идеи ценные.

## Что не подходит
- Docker required (у нас k8s sandbox без docker socket)
- 8+ ГБ RAM + GPU для нормальной работы
- ChromaDB, SearXNG как отдельные сервисы
- Без LLM-провайдера всё degraded

## Что сделали
- ✅ Склонировали в /root/projects/odysseus
- ✅ Установили requirements.txt
- ✅ Запустили backend (PID был 13184, health 200, version 1.0.3)
- ✅ Остановили (не нужен)
- ⏳ Можно выборочно копировать идеи в Hermes (skill: deep_research, auto-skill-audit)

## Следующие шаги (предложение)
1. Сделать skill `deep_research` по паттерну IterResearch — пригодится для исследований типа mezdunami.ru
2. Добавить в memory extraction из чата (bullet points → memory)
3. Внедрить tool policy (read/write/destructive) в Hermes tools
