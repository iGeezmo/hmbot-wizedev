---
title: "Ежедневный прикладной ИИ-дайджест"
type: doc
created: 2026-08-29
updated: 2026-09-03
managed: true
mirror:
  canonical_repository: "iGeezmo/0dai"
  canonical_path: "docs/ai-digest.md"
---

# Ежедневный прикладной ИИ-дайджест

Публичное зеркало накопительного прикладного ИИ-дайджеста для `hmbot-wizedev`.

Новые выпуски хранятся как отдельные файлы в `docs/ai-digest-entries/` и автоматически собираются в этот документ. Полный исторический архив до начала зеркала остаётся в каноническом приватном документе `iGeezmo/0dai/docs/ai-digest.md`.

<!-- DAILY_ENTRIES -->

## 2026-09-03

### Вывод дня

После проверки обновлений с последнего сохранённого выпуска порог прошли шесть сигналов. Главная тема — перенос доверия из неявного контекста в явные границы: approval должен быть привязан к конкретному аккаунту и tool identity, self-hosted execution не означает on-prem agent loop, AI-review может стать частью merge policy только с узким scope, а новые модели меняют не только качество, но и API/retention/cost contracts. Отдельного крупного design-only релиза сильнее этих изменений не найдено; для дизайна и маркетинга наиболее практичен новый agentic video-processing path Gemini.

### 1. Codex 0.153.0 привязал remembered MCP approvals к выбранному app account и открыл remote marketplaces в plugin CLI

3 сентября OpenAI выпустила Codex CLI `0.153.0`. Два изменения особенно важны для governance. Во-первых, remembered session approval для app/MCP tool теперь включает `link_id`: одобрение того же connector/tool под аккаунтом A не должно автоматически действовать для аккаунта B или вызова без selector. Во-вторых, `codex plugin` теперь умеет листать, устанавливать и удалять plugins из remote marketplaces; в JSON listing передаются source, version, install policy и auth policy. В соседнем hardening той же release-линии source restrictions применяются к curated Git marketplaces, а remote/local plugin identity обрабатывается отдельно.

**Практическое применение:** approval cache нужно ключевать как минимум по `executor + server/app + tool + selected account/link + capability/policy epoch`, а не по имени tool. Для remote marketplace полезно сохранять source provenance, resolved plugin identity/version и policy decision в receipt, но не credentials. Такой контракт особенно важен для control planes, где один агент может работать с несколькими Gmail/GitHub/CRM/account links.

**Риск и ограничения:** Codex-native remembered approval остаётся executor-owned state и не является бизнес-авторизацией приложения. Remote marketplace расширяет supply-chain surface: remote catalog может измениться, install policy может разрешать больше, чем ожидает внешний governance layer. Fast release cadence требует exact pin и canary.

**Сильный контраргумент:** самый простой безопасный путь — вообще отключить remembered approvals и remote marketplaces, использовать только локально pinned plugins и собственный authorization broker. Для high-risk workflows это сильная альтернатива; новая capability полезна там, где multi-account UX и catalog sharing действительно снижают операционную стоимость.

**Кому полезно:** builders coding-agent platforms, MCP/app integrations, AppSec, enterprise developer platforms и multi-account automation.

Источники: [Codex 0.153.0](https://github.com/openai/codex/releases/tag/rust-v0.153.0), [account-scoped approval commit](https://github.com/openai/codex/commit/2393b5c9208aab4233cf5e9b1c57d1a17425bef6), [remote marketplace CLI commit](https://github.com/openai/codex/commit/6b59cefcbb35951c197a235dc94dbe700f2fbc7c), [marketplace source-policy commit](https://github.com/openai/codex/commit/633ab199cfd724aa78013c006b27a2b3d049fc3b).

### 2. Gemini 3.8 Flash вышел в GA с 1M context и временной ценой $0.75/$3.75 за MTok

2 сентября Google выпустил `gemini-3.8-flash` в GA и пометил модель production-ready. Публичный contract: 1,048,576 input tokens, 65,536 output tokens, thinking levels `low`/`medium`/`high`, function calling, structured outputs, code execution, caching и preview computer use. До 31 декабря 2026 года действует introductory price `$0.75` за 1M input tokens и `$3.75` за 1M output tokens; Google указывает переход на standard pricing с 1 января 2027 года. Заявления Google о лидерстве модели на coding/agent benchmarks являются vendor claims, а не независимым доказательством для конкретной кодовой базы.

**Практическое применение:** добавить модель как отдельный candidate в router для long-horizon coding, tool-heavy agents и дешёвых больших контекстов, но не менять default по одному benchmark. Нужен paired workload test на accepted outcome, tool-loop failures, latency, billed tokens и human correction. В cost models introductory и post-2026 pricing должны быть разными сценариями.

**Риск и ограничения:** миграция с ранних Gemini 3 surfaces не полностью механическая: актуальная guidance требует проверить thinking controls и function-response contract; `minimal` thinking не поддерживается. Большой context создаёт соблазн отправлять больше данных вместо улучшения retrieval. Introductory price — временный экономический режим.

**Сильный контраргумент:** если текущий Sonnet/Codex/Gemini 3.7 маршрут уже даёт стабильный accepted-outcome cost, переход ради более дешёвого list price создаёт regression risk. Правильный baseline — реальная стоимость завершённой задачи, а не цена миллиона токенов.

**Кому полезно:** coding-agent fleets, аналитические pipelines, model routers, SaaS с большим контекстом и AI FinOps.

Источники: [Gemini API release notes](https://ai.google.dev/gemini-api/docs/changelog), [Gemini 3.8 Flash guide](https://ai.google.dev/gemini-api/docs/generate-content/latest-model), [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash).

### 3. Cursor Self-Hosted Machines переносит tool execution в вашу сеть, но не переносит agent loop on-prem

2 сентября Cursor открыл Self-Hosted Machines для Cloud Agents. Worker выполняет tools рядом с внутренними repositories/services и инициирует исходящее HTTPS-соединение; inbound connection от Cursor не требуется. Есть personal `My Machines` и team pools с динамической ёмкостью; team pools требуют Enterprise service-account API key. `stdio` MCP запускается на worker, тогда как hosted HTTP MCP URL по-прежнему достигается Cursor backend.

**Практическое применение:** это хороший вариант для private monorepos, custom build hardware, GPU, macOS/Linux-specific pipelines и internal services, которые трудно безопасно выставлять наружу. Worker следует помещать в отдельный low-privilege execution segment с short-lived credentials, egress policy и disposable workspace.

**Риск и ограничения:** название легко прочитать слишком широко. Это **не on-prem Cursor**: agent orchestration остаётся у Cursor, worker сообщает результаты обратно. Следовательно, code/tool outputs и instruction context всё равно требуют data-flow review. Доступ worker к внутренней сети может увеличить blast radius по сравнению с полностью изолированным managed sandbox.

**Сильный контраргумент:** self-hosted CI runner/ephemeral VM + provider-neutral agent CLI легче формально аудировать и снижает vendor coupling. Cursor self-host оправдан только если Cloud Agent UX, scheduling и cross-device workflow дают измеримое преимущество.

**Кому полезно:** enterprise platform engineering, AppSec, команды с закрытыми репозиториями, нестандартным железом и private network dependencies.

Источники: [Cursor changelog](https://cursor.com/changelog/self-hosted-machines), [Self-Hosted Machines docs](https://cursor.com/help/ai-features/self-hosted-machines), [product article](https://cursor.com/blog/self-hosted-machines).

### 4. GitHub Copilot Code Review теперь может давать approval, который считается required approval

1 сентября GitHub перевёл Copilot approval из advisory signal в потенциально действующий merge-control. Каждый Copilot review содержит approval assessment, но сам assessment не влияет на merge requirements. Если администратор отдельно включает approvals, Copilot может отправить настоящий `APPROVE`, который учитывается repository required-approvals rule. Возможность выключена по умолчанию, управляется на enterprise/org/repository уровнях; repository также может ограничить file paths, которые Copilot вправе approve. Новый commit после approval снимает его так же, как human approval. Функция находится в public preview.

**Практическое применение:** для low-risk generated changes, dependency metadata, docs или узких machine-generated paths можно сделать AI review частью policy и сократить reviewer latency. Рекомендуемый вариант — path allowlist + обязательные deterministic tests + human ownership для auth/payments/migrations/security-sensitive code.

**Риск и ограничения:** модельный review теперь способен удовлетворить реальное merge condition; это уже authority surface, а не просто комментарий. Если path scope слишком широк или required approvals всего один, ошибка Copilot может фактически разблокировать merge. Preview semantics также могут меняться.

**Сильный контраргумент:** AI-review не должен никогда считаться required approval; пусть остаётся advisory. Для критичных production repositories это наиболее консервативный и часто правильный default. Новый режим разумен только для явно классифицированных low-risk changes с независимыми deterministic gates.

**Кому полезно:** engineering management, platform teams, monorepo governance, release automation и AppSec.

Источник: [GitHub Changelog — Copilot code review can now approve pull requests](https://github.blog/changelog/2026-09-01-copilot-code-review-can-now-approve-pull-requests/).

### 5. Claude Fable 5.1 меняет одновременно tool contract, cache economics и data-retention boundary

1 сентября Anthropic выпустила `claude-fable-5-1` для long-running agentic coding, knowledge work и research. Модель имеет 1M context, 128k max output и always-on adaptive thinking. Цена — `$10` input / `$50` output за MTok; cache read снизился до `$0.25`/MTok. Для Fable 5.1 `tool_choice` типов `any` и `tool` не поддерживается и возвращает 400; Anthropic рекомендует strict tool use или structured outputs. Thinking blocks сохраняются только при replay в ту же или более новую модель и имеют дополнительные binding semantics.

Критически важно: Fable 5.1 относится к Covered Models с обязательным **30-дневным retention**, поэтому Zero Data Retention недоступен без отдельного разрешения Anthropic. На Claude API данные удерживает Anthropic; при соответствующих cloud offerings retained data остаётся в среде cloud provider согласно документации платформы.

**Практическое применение:** перед добавлением Fable 5.1 в model router нужны два отдельных gates: API-compatibility test tool loops и data-class policy. Для public/non-sensitive research модель может быть полезным high-end route; для confidential/ZDR workloads модель нельзя выбирать автоматически только потому, что она сильнее на vendor benchmarks.

**Риск и ограничения:** стоимость output высокая; обязательный retention меняет privacy/compliance boundary; старый tool-choice код может ломаться 400. Thinking-block replay осложняет cross-model fallback.

**Сильный контраргумент:** Sonnet 5 либо другой ZDR-compatible provider может дать достаточно качества с существенно меньшей стоимостью и более простой data policy. Fable имеет смысл только там, где измеримый quality gain превышает privacy, cost и migration overhead.

**Кому полезно:** high-end coding/research agents, model routers, regulated platform teams и AI FinOps/privacy engineering.

Источники: [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview), [pricing](https://platform.claude.com/docs/en/about-claude/pricing), [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

### 6. Gemini добавил agentic video understanding: модель сама выбирает, какие части длинного видео читать глубже

1 сентября Google выпустил agentic video understanding для Gemini 3.7 Flash, 3.6 Flash и 3.5 Flash-Lite в Interactions и GenerateContent APIs. В отличие от static processing с заранее выбранной дискретизацией, модель динамически перемещается по timeline и запрашивает transcript, frames или audio только там, где считает это необходимым. Google заявляет до 88% меньший token usage на long-form video; это vendor claim и требует paired validation. Для коротких роликов дополнительный agentic round-trip может быть хуже по latency, поэтому static processing остаётся рациональным вариантом.

**Практическое применение:** research interviews, webinar/podcast analysis, ad/creative QA, lecture analytics и long-form competitive monitoring можно сначала пропускать через agentic navigation, а затем отдельно проверять найденные timestamps/quotes. Это потенциально снижает стоимость многочасовых архивов без принудительного 1-FPS анализа всего материала.

**Риск и ограничения:** selective navigation может пропустить короткий, но важный момент; fast motion и мелкий текст всё равно требуют resolution/frame strategy. Нельзя использовать результат как единственное доказательство в compliance/moderation; для promoted findings нужен timestamped replay или human check.

**Сильный контраргумент:** deterministic preprocessing — transcript + fixed scene detection + embeddings — воспроизводимее и проще аудируется. Для legal/compliance и короткого контента это сильная альтернатива; agentic path особенно интересен, когда архив длинный, вопрос меняется, а полный static ingestion дорог.

**Кому полезно:** marketing/content analytics, user research, education, media monitoring и multimodal product teams.

Источники: [Gemini API release notes](https://ai.google.dev/gemini-api/docs/changelog), [Video understanding guide](https://ai.google.dev/gemini-api/docs/video-understanding).

## GitHub Radar

`@GitHubRadar` использован как discovery-source, а не как evidence. Канал допускает платные размещения, поэтому публикация, просмотры, реакции и stars не влияют на promotion score. Ни один сегодняшний кандидат из discovery-feed не был повышен без независимой проверки первоисточников.

### Репозиторий периода: `openai/codex`

**Release/commits:** текущий stable — `0.153.0`, опубликованный 3 сентября. В release вошли account-scoped app/MCP approvals и remote-marketplace plugin CLI; `main` продолжает меняться после tag, поэтому production baseline должен быть exact tag, а не floating branch.

**Лицензия:** Apache-2.0; коммерческое использование и модификация разрешены в рамках условий лицензии.

**Документация и install surface:** standalone installers для macOS/Linux/Windows, npm `@openai/codex`, Homebrew и release binaries; ChatGPT sign-in или API-key auth. Дополнительная поверхность включает MCP, apps, plugins/marketplaces, app-server, IDE и remote/session capabilities.

**CI/tests:** repository имеет blocking CI, Bazel workflow, `cargo-deny`, post-merge CI, platform/build-specific workflows и многочисленные targeted regression tests. Это сильный maintenance signal, но application-level permission/account fixtures всё равно обязательны.

**Issue activity:** tracker очень активен. Свежие пользовательские reports включают remote-mode project identity, cross-thread delegation и custom-provider connectivity. Эти issues следует считать canary/discovery evidence до воспроизведения на exact version/OS, а не подтверждёнными universal defects.

**Security model:** официальный disclosure идёт через Bugcrowd; runtime boundary состоит из sandbox, approvals, network controls и project trust. `0.153.0` улучшает account identity для remembered approvals, но capability authorization и irreversible business writes по-прежнему должны проверяться приложением/server-side policy.

**Telemetry/data handling:** в repository есть OpenTelemetry/session telemetry и конфигурация `log_user_prompts`. Поэтому telemetry — отдельный outbound data surface: перед rollout нужно проверить exporter, prompt capture, identity metadata и retention. Нельзя автоматически выводить ни «всё отправляется», ни «ничего не отправляется» только из наличия OTel кода.

**Integration cost:** низкий для pinned bounded CLI/`codex exec`; средний для MCP/apps/plugins/session lifecycle; высокий, если Codex session/approval/plugin state становится canonical governance database.

**Reversibility:** высокая при thin adapter, repository-owned policy и внешнем receipt ledger; ниже, если native app-link IDs, marketplace state и session approvals проникают в domain model.

**Known limitations:** очень быстрый release cadence; platform/auth-mode differences; dynamic marketplace supply-chain; multi-account approval semantics требуют canary; local/session telemetry и history требуют retention review.

**Production-readiness — собственная оценка:** **4/5** для pinned `0.153.0` в bounded workflows с external policy/receipts; **3/5** для remote marketplace + multi-account apps до account/provenance fixtures; **2/5** для broad Full Access с dynamic plugins и native session state как единственным audit/authorization source.

**Validation plan — 90 минут:** pin `0.153.0` в disposable repo. Подключить два synthetic app links к одному MCP tool: approve под A, затем вызвать под B и без selector — повторный approval обязателен; вернуть A и проверить только допустимую continuity. Подключить один controlled remote marketplace, выполнить list/install/remove и записать resolved source/version/policy; неразрешённый source должен fail closed внешней policy. После compaction/restart/fork проверить, что remembered approval не пересекает account/policy epoch. Прогнать denied outside-root/network fixtures и synthetic-secret fixture. Проверить local history/OTel sink на fixture secret и выключить prompt capture. Наконец отключить apps/plugins и убедиться, что базовый CLI adapter продолжает работать.

**Красные флаги:** floating `main`/alpha; approval key без account/link identity; remote marketplace без allowlist/provenance/version evidence; Full Access трактуется как достаточный authorization; user prompts/secrets попадают в telemetry без review; GitHub issue принимается за подтверждённый defect без repro; Codex session state становится canonical business ledger.

Репозиторий: https://github.com/openai/codex

### Watchlist

- [`microsoft/agent-host-protocol`](https://github.com/microsoft/agent-host-protocol) — session interoperability между harnesses; дождаться более стабильного protocol contract и отдельно держать authority layer.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — следить за workload identity, discovery и conformance, а не только за заявленной поддержкой revision date.
- [`anthropics/claude-code`](https://github.com/anthropics/claude-code) — быстрые изменения sandbox/credential/session boundaries полезны как cross-executor comparison для governance contracts.

### Topic для разведки

**Approval identity + plugin provenance:** reusable approval должен быть функцией `tool/server + selected account/link + capability snapshot + policy epoch`, а installable agent capability — иметь immutable source/version provenance и явный exit path. Удобный UI cache без этих измерений превращается в скрытую authorization и supply-chain boundary.

## 2026-09-01

### Вывод дня

Порог выпуска прошли три сигнала. Нового frontier-model, design-tool или marketing-AI релиза, который по подтверждённому практическому влиянию превосходил бы их, в первичных источниках не найдено. Главная тема дня — **bounded state in long-running agents**: Codex добавил per-tool ограничения model-visible MCP output и укрепил сохранение approval evidence через compaction; AI Gateway получил identity-scoped spend circuit breakers; Pydantic AI закрыл конкретный false-negative класс eval queries и одновременно уточнил lifecycle durable execution.

### 1. Codex 0.152.0 добавляет per-tool MCP output budgets и сохраняет approval evidence через compaction

**Что изменилось и дата.** OpenAI выпустила Codex CLI `0.152.0` **1 сентября 2026 года**. Для отдельных MCP tools теперь можно задать `output_token_limit`; релиз отдельно заявляет, что truncation применяется согласованно и после resume session. В той же версии automatic approval reviews сохраняют пользовательские инструкции, ответы и действующие authorization decisions через history compaction; resumed threads восстанавливают сохранённый working directory, а metadata updates не должны терять filesystem permissions. Для cloud tasks backend URL теперь проверяется как недоверенный input, redirects отключаются, чтобы не пересылать сохранённые credentials на другой адрес.

**Практическое применение.** В MCP-heavy агенте можно задавать бюджет model-visible output по tool, а не только общий context budget. Например, search/list tools получают ограниченный результат с явным `truncated=true`, тогда как короткие authorization/status tools остаются без агрессивного усечения. Для governed runtime полезен контракт `configured_limit + raw_result_digest/size + delivered_size + truncation_state`, не сохраняя сырой чувствительный payload. Отдельный regression должен проверять `long result -> truncate -> resume -> тот же effective limit` и `approval -> forced compaction -> resume` без потери provenance решения.

**Риск и ограничения.** Truncation — не privacy filter и не authorization. Он способен скрыть отрицательный сигнал, последний элемент списка или часть stack trace и тем самым изменить решение модели. Для security-sensitive tools нужен структурированный summary/status вне усечённого текстового хвоста либо application-side normalization. Сохранение Codex/Guardian authorization через compaction также не делает внутреннее состояние Codex каноническим источником полномочий приложения.

**Сильный контраргумент.** Provider-neutral MCP gateway или application adapter может ограничивать output одинаково для Codex, Claude и других executors и тем самым уменьшить vendor-specific policy. Это более чистая архитектура. Codex `output_token_limit` лучше использовать как defense-in-depth/generated adapter от единого project policy, а не как новый источник истины.

**Кому полезно.** Agent-platform builders, MCP fleets, coding-agent governance, AppSec и FinOps/context-engineering команды.

Источники: [Codex 0.152.0](https://github.com/openai/codex/releases/tag/rust-v0.152.0), [Codex repository](https://github.com/openai/codex).

### 2. Vercel AI Gateway получил per-user dollar budgets поверх key/project/team limits

**Что изменилось и дата.** **31 августа 2026 года** Vercel добавила per-user budgets в AI Gateway. Default budget применяется отдельно к каждому члену команды, custom budget переопределяет его для конкретного пользователя. Spend суммируется по API keys, атрибутированным пользователю, и app tokens; после достижения лимита новые Gateway requests отклоняются до reset или повышения budget. Reset может быть daily, weekly, monthly или disabled, а alerts доступны на 50%, 75% и 100%. User budget не заменяет API-key/project/team budgets: request должен укладываться во все применимые лимиты.

Важное исключение: **BYOK spend не учитывается в per-user budget**. Ключи, созданные до выпуска функции, Vercel оставила атрибутированными team для backward compatibility; production/shared key следует явно относить к team, иначе расход может ошибочно лечь на создателя. CLI-управление user budgets требует Vercel CLI `>=59.6.2`.

**Практическое применение.** Для coding agents, research jobs и других unattended workloads появляется provider-side identity-scoped circuit breaker без схемы «один gateway project на каждого сотрудника». Практичный layered design: `per-run application budget -> user budget -> project/app budget -> team budget`. Shared production workloads должны иметь отдельную service/team attribution, а не использовать человеческий user budget.

**Риск и ограничения.** Финансовый cap не ограничивает capability blast radius: дешёвый destructive call остаётся разрушительным. BYOK способен полностью обойти этот budget layer, а неправильная ownership attribution ключа либо заблокирует не того пользователя, либо исключит расход из ожидаемого лимита. Hard rejection после лимита также является availability event и должен иметь понятный fallback/UX.

**Сильный контраргумент.** Provider-neutral ledger и quotas в собственном control plane лучше работают в multi-cloud и не зависят от Vercel identity model. Верно; Gateway budget рационально использовать как последний server-side предохранитель, а не единственный FinOps contract.

**Кому полезно.** Platform engineering, AI FinOps, команды с AI Gateway, coding-agent fleets и SaaS с несколькими человеческими/служебными AI identities.

Источник: [Vercel — Set per-user budgets on AI Gateway](https://vercel.com/changelog/set-per-user-budgets-on-ai-gateway).

### 3. Pydantic AI 2.37.0 закрывает false-negative в `SpanQuery` и уточняет durable-operation lifecycle

**Что изменилось и дата.** Pydantic AI `v2.37.0`, опубликованный **1 сентября 2026 года** и маркированный релизом за 31 августа, исправляет `SpanQuery`: при pruning теперь сохраняются **все conditions**. Это закрывает конкретный false-negative класс, который ранее делал небезопасным использование определённых pruned span queries как единственного blocking eval/release gate. Релиз также меняет durable execution lifecycle: context-managed models, восстановленные внутри durable operations, корректно управляются как context resources; DBOS теперь отвергает per-run `capabilities=` по аналогии с Temporal; Prefect tool discovery journaled внутри tasks; unmanaged models больше не перестраиваются внутри durable capability operations.

**Практическое применение.** Если `pydantic_evals SpanQuery` используется в CI или quality/security gates, стоит поднять pinned canary до `2.37.0` и повторно прогнать известный fixture с несколькими ancestor/descendant conditions и pruning. Только после воспроизводимого исправления gate можно снова считать блокирующим. Командам, тестирующим новый public durable-backend API из `2.36`, следует повторить crash/resume/provider-lifecycle fixtures: исправления меняют ownership/lifetime model objects внутри durable steps.

**Риск и ограничения.** Исправление одного pruning bug не доказывает логическую полноту всех eval queries. Release/security decision не должен зависеть от одного matcher без known-positive/known-negative fixtures. Durable fixes также не дают exactly-once гарантию внешних side effects: application idempotency и canonical ledger остаются необходимыми.

**Сильный контраргумент.** Если проект не использует `SpanQuery` pruning и не подключает Pydantic durable backends, срочности обновления почти нет. Это targeted correctness release, а не основание мигрировать существующий agent stack на Pydantic AI.

**Кому полезно.** Python agent platforms, evaluation/QA pipelines, durable HITL systems и teams, использующие Pydantic AI как runtime.

Источники: [Pydantic AI v2.37.0](https://github.com/pydantic/pydantic-ai/releases/tag/v2.37.0), [fix PR #7499](https://github.com/pydantic/pydantic-ai/pull/7499), [Pydantic AI repository](https://github.com/pydantic/pydantic-ai).

## GitHub Radar

### Репозиторий периода: `dubinc/dub`

`@GitHubRadar` использован только для discovery. Сам канал прямо сообщает о платных размещениях, поэтому факт публикации, реакции и просмотры не являются evidence. Dub ниже проверен независимо по самому репозиторию, security policy и текущим vendor pages.

**Назначение и текущая активность.** Dub — link-attribution платформа для short links, conversion tracking и affiliate programs. Основной репозиторий активно меняется: 1 сентября в `main` продолжались merge/fix commits, включая Redis failover path и UI fixes. Tagged GitHub Releases отсутствуют, поэтому self-hosting по плавающему `main` не даёт воспроизводимого release contract; для пилота нужен exact commit pin.

**Лицензия и коммерческое использование.** Проект open-core: core лицензирован по **AGPL-3.0**, а Enterprise Edition (`/ee`) имеет отдельную commercial license. Это не permissive MIT/Apache dependency. Коммерческое использование AGPL core возможно при соблюдении условий AGPL; enterprise-функции нельзя автоматически считать частью свободной лицензии.

**Документация и install surface.** README описывает Next.js/TypeScript/Prisma stack и зависимости от Upstash, Tinybird, PlanetScale, NextAuth/BoxyHQ, Stripe, Resend и Vercel; есть отдельный self-hosting guide. Для managed продукта текущая pricing surface включает conversion tracking, event webhooks, API/SDKs, retention tiers и, на partner plans, REST API + MCP Server. Self-host deployment поэтому нельзя считать «одним контейнером без внешней инфраструктуры» без отдельной проверки фактической конфигурации storage/analytics/queues.

**CI/tests и maintenance.** В репозитории есть browser/E2E lanes (`playwright.yaml`, `e2e.yaml`), formatting и deploy workflows. Текущий issue/PR поток активный; на 1 сентября открыты изменения по background jobs, tracking configuration и security review automation. Это сильный maintenance signal, но отсутствие tagged releases повышает стоимость reproducibility и rollback для self-host.

**Security model.** `SECURITY.md` заявляет поддержку security updates для всех версий и private reporting на `security@dub.co` с обещанием acknowledgement в течение 48 часов. При этом attribution platform обрабатывает redirect/conversion/partner data, поэтому application-side consent, data minimization, webhook verification и payout/idempotency остаются отдельными boundaries.

**Telemetry/data handling.** Hosted privacy policy прямо описывает collection/processing personal and usage data и использование service providers. Публичная pricing page задаёт retention как product property: например, Links Business — 3 года, Advanced — 5 лет, Enterprise — unlimited. Поэтому Dub Cloud нельзя трактовать как «privacy-neutral sink». Для self-host custody зависит от выбранной инфраструктуры и конфигурации; наличие self-host option само по себе не устраняет внешние subprocessors.

**Economics.** На текущей публичной pricing page Dub Partners Business стоит `$90/month`, Advanced `$300/month`, Enterprise — custom; Links/analytics limits и retention различаются по tier. Это vendor list pricing, не индивидуальное предложение. Для простой link analytics задачи продукт может оказаться функционально и экономически тяжелее Plausible/UTM + существующего event sink; для affiliate/payout infrastructure сравнение уже другое.

**Integration cost.** Managed Cloud: низкий–средний для links/conversion events, средний для partners/webhooks. Self-host: высокий из-за open-core boundaries и многосервисной operational surface.

**Reversibility.** Средне-высокая, если canonical UTMs, conversion IDs и business outcomes остаются в application DB, а Dub — replaceable attribution sink. Низкая, если partner contracts, payouts, short-link namespace и attribution history становятся единственным vendor-owned source of truth.

**Known limitations.** Нет tagged releases; AGPL + commercial `/ee`; hosted retention зависит от plan; attribution — probabilistic/business logic, а не доказательство causal ROI; self-hosting не означает автоматически минимальную инфраструктуру или нулевой telemetry/egress.

**Production-readiness — собственная оценка:** **4/5 для managed Dub как bounded attribution/partner service после privacy/webhook review; 2.5–3/5 для self-host**, пока нет собственного exact-commit release process, upgrade rehearsal и ясного inventory внешних dependencies.

**Validation plan — 60–90 минут:** создать synthetic workspace/domain и 3 links; отправить только псевдонимный conversion ID; проверить redirect latency, UTM preservation и duplicate conversion behavior; подписать/повторить webhook и убедиться в idempotency; сверить один conversion с текущим analytics sink; проверить export/delete/disable path. Для self-host — pin exact commit, проверить egress/dependencies, Redis outage/failover, backup/restore и юридическую границу AGPL core vs `/ee`.

**Красные флаги:** production на floating `main`; PII/secrets в query parameters; attribution принимается за causal ROI без holdout/validation; webhook без signature/replay/idempotency controls; AGPL core ошибочно описан как permissive; self-host option продаётся внутренне как «zero vendor» без dependency inventory; business events существуют только в Dub и не экспортируются.

Репозиторий: https://github.com/dubinc/dub

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — per-tool MCP output budgets, approval evidence across compaction и cloud-task credential redirects.
- [`pydantic/pydantic-ai`](https://github.com/pydantic/pydantic-ai) — eval-query correctness и durable lifecycle after 2.37.0.
- [`dgtlmoon/changedetection.io`](https://github.com/dgtlmoon/changedetection.io) — self-hostable competitive/content monitoring; оценивать как discovery/monitoring primitive, а не как source of truth.

### Topic для разведки

**Attribution data as agent input:** если AI-агент использует clicks/conversions/affiliate outcomes для marketing decisions, source campaign, consent/data class, attribution window и uncertainty должны оставаться видимыми. `Attributed conversion` не равно `causal lift` и не должно автоматически разрешать перераспределение бюджета без отдельной policy/experiment evidence.

## 2026-08-31

### Вывод дня

Порог выпуска прошли пять сигналов. Нового stable frontier-model или крупного IDE/coding-agent релиза, который по подтверждённому практическому следствию превосходил бы их, в первичных источниках не найдено; prerelease Codex `0.152.x` и обычные patch/minor updates сознательно не включены. Сегодняшняя тема — смена рабочих границ на стыке месяца: GitHub Spark закрывает workbench, завтра из Copilot уходят сразу несколько model IDs, Claude Sonnet 5 сохраняет более низкую постоянную цену, ChatGPT переводит старый DALL·E workflow на Images, а несколько Google identities теперь могут одновременно участвовать в одном разговоре.

### 1. GitHub Spark закрывает текущий workbench 31 августа: код нужно экспортировать, а `llm()` уже требует собственного inference provider

**Что изменилось и дата.** GitHub объявила, что с 4 августа Spark на `github.com` не принимает новых пользователей и не позволяет создавать новые apps; существующие пользователи могут пользоваться workbench только до **31 августа 2026 года**, чтобы экспортировать созданные apps. Уже опубликованные Spark apps продолжат работать после retirement. Отдельно GitHub Models, на котором был построен Spark `llm()`, отключён с 30 июля, поэтому `llm()`-вызовы уже не работают и требуют замены собственным inference provider.

**Практическое применение.** Сегодня последний документированный день для `Spark workbench -> ... -> Create repository`. После экспорта следует зафиксировать build/deploy contract в обычном репозитории, найти `llm()` repository-wide search, вынести model access за application-owned adapter, добавить собственные API credentials/billing и проверить опубликованный app без зависимости от Spark editor. Сам deployed URL не следует считать достаточным backup: GitHub прямо рекомендует экспортировать исходный код, если приложение планируется редактировать дальше.

**Риск и ограничения.** Retirement относится именно к текущему GitHub Spark experience на `github.com`; он не означает отключение Copilot, Codespaces или обычных GitHub repositories. Уже deployed apps без `llm()` могут продолжить работать. Для AI apps перенос inference меняет custody API keys, стоимость, rate limits, data processing и failure semantics — это не механическая замена функции.

**Сильный контраргумент.** Если Spark использовался только как disposable prototype builder, а нужный код уже находится в нормальном repository, отдельной migration-программы не требуется. Нужно лишь отрицательно подтвердить отсутствие неэкспортированных apps и `llm()` dependency.

**Кому полезно.** Rapid prototyping, design/product teams, internal-tool builders и владельцы Spark apps.

Источники: [GitHub Changelog — Spark retirement](https://github.blog/changelog/2026-08-04-upcoming-deprecation-of-github-spark-on-github-com/), [GitHub Community announcement](https://github.com/orgs/community/discussions/203602).

### 2. 1 сентября из GitHub Copilot уходят Gemini 3.1 Pro, четыре Claude 4.x модели и Raptor Mini

**Что изменилось и дата.** GitHub назначила на **1 сентября 2026 года** deprecation сразу для `Gemini 3.1 Pro`, `Claude Opus 4.5`, `Claude Opus 4.6`, `Claude Sonnet 4.5`, `Claude Sonnet 4.6` и `Raptor Mini` во всех Copilot experiences — Chat, inline edits, ask/agent modes и code completions. Рекомендованные замены: Gemini 3.6 Flash, Claude Opus 4.7/4.8/5, Claude Sonnet 5 и MAI-Code-1-Flash. Исключение: Claude Sonnet 4.6 остаётся доступным individual Copilot subscribers на annual plans. Enterprise admins могут отдельно потребовать включить replacement model в model policies.

**Практическое применение.** Сегодня стоит проверить managed settings, hardcoded model selectors, reusable prompt/eval baselines, agent profiles и документацию. Перед заменой default model нужен маленький paired regression: качество accepted result, tool behavior, latency, context handling и фактические AI credits/стоимость. Для Enterprise отдельно проверить, что replacement разрешён policy, иначе nominal migration может завершиться отсутствующим model selector.

**Риск и ограничения.** Copilot deprecation не равна retirement тех же model families в API Anthropic/Google или других providers. Auto-selection может скрыть смену модели, но изменить behavior/cost. Исключение для annual subscribers делает глобальный вывод «Sonnet 4.6 исчезает у всех» неверным.

**Сильный контраргумент.** Если команда использует Copilot Auto и не имеет model-specific prompts/evals, ручная миграция может быть лишней. Но для reproducible coding workflows и enterprise policy важно хотя бы проверить effective model после cutoff.

**Кому полезно.** GitHub Copilot administrators, platform engineering, coding-agent users и команды с model-specific evals.

Источник: [GitHub Changelog — September 1 model deprecations](https://github.blog/changelog/2026-07-31-upcoming-august-2026-model-deprecations-in-github-copilot/).

### 3. Claude Sonnet 5 остаётся на $2/$10 за MTok: запланированного повышения 1 сентября не будет

**Что изменилось и дата.** Anthropic 10 августа сделала вводную цену Claude Sonnet 5 постоянной: `$2` за миллион input tokens и `$10` за миллион output tokens. Ранее было объявлено повышение до `$3/$15` с 1 сентября 2026 года; оно отменено. На 31 августа это перестаёт быть временной скидкой и становится устойчивым входом для model-routing и unit-economics. Anthropic отдельно предупреждает, что новый tokenizer создаёт примерно на 30% больше токенов для того же текста, поэтому реальная экономия относительно Sonnet 4.6 не равна простому отношению `$2/$10` к `$3/$15`.

**Практическое применение.** Пересчитать routing thresholds и budget envelopes для long-context coding/research/marketing-analysis задач по фактическим billed tokens, а не по старому ожиданию сентябрьской цены. Если Sonnet 5 сравнивается с Sonnet 4.6, GPT-5.6 или другими моделями, benchmark должен учитывать total accepted-outcome cost: input/output/cache tokens, retries, human correction и latency. Старые FinOps alerts, в которых с 1 сентября заранее заложено `$3/$15`, стоит исправить сейчас, чтобы не завышать forecast.

**Риск и ограничения.** Это list price Claude Platform; AWS/partner pricing и enterprise agreements могут отличаться. Новый tokenizer меняет объём billable tokens. Более низкая цена не делает Sonnet 5 автоматическим default: migration semantics также отличаются — adaptive thinking включён по умолчанию, manual extended thinking удалён, а нестандартные `temperature/top_p/top_k` возвращают 400.

**Сильный контраргумент.** Если основной расход определяется не token price, а latency, retries, tool calls или стоимостью человеческой проверки, снижение list price может почти не изменить unit economics. Поэтому правильное действие — обновить cost model, а не автоматически переключить весь трафик.

**Кому полезно.** Agent platforms, coding/research pipelines, FinOps, маркетинговая и продуктовая аналитика с длинным контекстом.

Источники: [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview), [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing), [What's new in Claude Sonnet 5](https://platform.claude.com/docs/en/docs/about-claude/models/whats-new-sonnet-5).

### 4. Для официального DALL·E GPT в ChatGPT наступила объявленная дата retirement; новые SOP нужно строить вокруг ChatGPT Images

**Что изменилось и дата.** OpenAI заранее указала **30 августа 2026 года** как дату retirement официального `DALL·E GPT` внутри ChatGPT и направляет пользователей в ChatGPT Images. Пользовательские GPT с включённой capability Image Generation этим изменением не затронуты. На 31 августа дата cutoff уже прошла, но текущая справка всё ещё местами сформулирована в будущем времени и содержит старую строку о доступе к DALL·E GPT, поэтому я не выдаю отсутствие карточки во всех аккаунтах/регионах за независимо подтверждённый факт.

**Практическое применение.** Для дизайн- и marketing-SOP, которые буквально ссылаются на «открой DALL·E GPT», заменить entry point, сохранить нужные старые artifacts и перепроверить recurring creative workflows: prompt templates, aspect ratios, text rendering, brand-color consistency, edit/inpaint behavior, export dimensions и human review. Инструкции лучше описывать capability (`image generation/editing`), а не привязывать к конкретной GPT-карточке.

**Риск и ограничения.** Это retirement **ChatGPT surface**, а не доказательство отключения DALL·E API/model endpoints. Нельзя автоматически переносить вывод на API integrations. ChatGPT Images может давать другое визуальное поведение, поэтому смена интерфейса не означает output parity.

**Сильный контраргумент.** Если команда уже использует ChatGPT Images, API или собственный GPT с Image Generation, operational change почти нулевой. Сигнал важен только там, где DALL·E GPT был закреплён в SOP, обучающих материалах, bookmarks или production-like human workflow.

**Кому полезно.** Дизайн, performance/content marketing, social production, команды с повторяемыми creative SOP.

Источники: [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes), [Images in ChatGPT](https://help.openai.com/en/articles/11084440-images-in-chatgpt).

### 5. ChatGPT теперь подключает несколько Google-аккаунтов одновременно: удобнее cross-account work, но identity provenance становится обязательным

**Что изменилось и дата.** 28 августа OpenAI добавила multiple connected accounts для Gmail, Google Calendar и Google Contacts plugins. Поддерживаемые Plus, Pro, Business и Enterprise пользователи могут подключить, например, личный и рабочий Google-аккаунты и использовать их в одном разговоре. Provider authorization по-прежнему не расширяет исходные права Google account и не отменяет workspace restrictions.

**Практическое применение.** Для executive/marketing/analytics operations можно в одном workflow сопоставлять несколько календарей или искать информацию в нескольких inbox без ручного переключения identity. Но для любой автоматизации результат должен хранить provenance: `provider`, `connected_account`, source object ID и effective action permission. Если из нескольких inbox/calendar получается рекомендация или действие, downstream system должен понимать, из какого identity domain пришёл каждый факт.

**Риск и ограничения.** Главное новое рисковое место — не OAuth как таковой, а cross-domain context mixing. Личная переписка может оказаться рядом с рабочим контекстом; Memory и conversation context способны увеличить срок жизни производных данных. Disconnect останавливает будущий доступ, но не автоматически удаляет существующие chats, saved files или memories. Для Google apps нужно отдельно проверять запрашиваемые OAuth scopes и workspace/admin controls.

**Сильный контраргумент.** Для регулируемых сред, клиентских аккаунтов или строгого разделения ролей две отдельные сессии/workspaces безопаснее и проще аудируются. Multiple-account mode следует включать там, где стоимость постоянного переключения действительно велика и provenance можно сохранить, а не как новый default.

**Кому полезно.** Маркетинговые и аналитические команды, founders/executives, account managers, operations и research workflows с несколькими Google identities.

Источники: [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes), [Connecting and managing app accounts](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt), [Google app data controls](https://help.openai.com/en/articles/10408842-google-app-data-controls-faq).

## GitHub Radar

### Репозиторий периода: `plausible/analytics`

`@GitHubRadar` был просмотрен как discovery-feed, включая коммерческие размещения; сегодняшнее продвижение Plausible не опирается на текст Telegram-постов. Все выводы ниже перепроверены по самому репозиторию и официальной документации Plausible.

**Назначение и текущий статус.** `plausible/analytics` — активно поддерживаемая privacy-first web analytics платформа. Основное приложение Plausible Community Edition распространяется под **AGPL-3.0+**; browser tracker отдельно имеет MIT-лицензию. Managed Cloud и self-hosted CE — существенно разные продукты: Cloud развивается непрерывно, а CE выпускается как long-term release примерно дважды в год и не содержит части premium-функций.

**Release/commits.** Последний опубликованный CE release — `v3.2.1` от 15 мая 2026 года. Это security-only release, который устранил `CVE-2026-8467 / GHSA-55hg-8qxv-qj4p`: в предыдущих `v3.0–v3.2` публично доступный `/storybook` при определённых условиях позволял remote code execution от имени системного пользователя приложения; `v3.2.1` полностью удалил endpoint. `master` при этом активно развивается: в конце августа идут продуктовые и test fixes, включая переработку funnel UI и исправления flaky event/session tests.

**Документация и CI/tests.** Репозиторий содержит Elixir и Node test workflows, image builds, migration validation, Terraform E2E и tracker-specific checks. Security policy явно говорит, что security fixes добавляются только в latest major.minor и не backportятся. Для production self-host это означает: pin reviewed current image/version и иметь собственный upgrade cadence; плавающий `latest` удобен поставщику, но хуже для воспроизводимого deployment.

**Security model.** Cloud и CE не являются одинаковым security boundary. В Cloud инфраструктурой, backup и security занимается Plausible; CE требует собственной эксплуатации PostgreSQL/ClickHouse, reverse proxy, patching, backups и incident response. Недавний RCE в старых CE versions — конкретное доказательство того, что self-hosting не следует выбирать только ради слова «privacy».

**Data handling / telemetry.** По данным Plausible, hosted service не использует cookies, localStorage или persistent cross-site identifiers. Для подсчёта daily unique visitor входящие IP и User-Agent используются в `hash(daily_salt + domain + IP + UA)`; raw IP/UA не сохраняются, salt удаляется каждые 24 часа. Vendor также заявляет, что visitor data Cloud обрабатываются только в ЕС на европейской инфраструктуре. Это vendor claims и DPA/data-policy evidence, а не независимый аудит сегодняшнего выпуска. Для self-host данные находятся в выбранной собственной инфраструктуре.

**Install surface.** Самый лёгкий путь — Cloud tracker или Events API. CE заметно тяжелее: application + PostgreSQL + ClickHouse и полный operational ownership. Для интеграции в существующий продукт выгоднее держать provider adapter и event schema в приложении, а Plausible использовать как сменяемый sink/dashboard.

**Pricing/economics.** На текущей публичной pricing page при до 10k monthly pageviews указаны Starter `$9/mo`, Growth `$14/mo`, Business `$19/mo`; Business добавляет custom properties, Stats API, ecommerce revenue attribution, funnels/user journeys и consolidated view. Usage считается по pageviews + custom events. Enterprise добавляет raw event exports и другие возможности. Цены являются текущими публичными vendor prices, не контрактным предложением.

**Issue/maintenance surface.** Репозиторий активен и получает регулярные commits. Это лучше dormant OSS, но Cloud/CE feature parity намеренно отсутствует: marketing funnels, revenue goals, SSO и Sites API относятся к premium Cloud, поэтому self-host CE нельзя считать бесплатной эквивалентной заменой Cloud.

**Integration cost.** Низкий для Cloud event adapter; средний для полноценных funnels/custom properties и historical comparison; высокий для CE, поскольку появляется отдельный Elixir/Postgres/ClickHouse production stack.

**Reversibility.** Хорошая при application-owned event schema: агрегированные stats экспортируются через CSV/Stats API; self-host даёт прямой доступ к ClickHouse. Lock-in повышается, если бизнес-метрики определяются только внутри Plausible UI без репозитория с event taxonomy.

**Known limitations.** Privacy-friendly не означает «юридическая квалификация автоматически решена»; именно владелец сайта отвечает за lawful basis/notices/safeguards. CE lagging release cadence и AGPL требуют отдельного review. Unique-visitor метод намеренно daily-scoped и не предназначен для долгоживущей user-level product analytics.

**Production-readiness — собственная оценка:** **4/5 для Managed Cloud как сменяемого privacy-oriented analytics sink; 3/5 для pinned CE `>=3.2.1` при зрелой ops-команде; 1/5 для старых CE `v3.0–v3.2` с доступным `/storybook`.**

**Validation plan — 90 минут:**

1. Создать trial site без production credentials и с synthetic traffic.
2. Отправить allowlisted `page_view`, CTA и conversion events без email, brief text, user ID и precise location.
3. Проверить network/storage: отсутствие cookies/localStorage и состав отправляемых properties.
4. Построить один funnel и сравнить counts с существующим event sink на небольшом shadow sample.
5. Отключить Plausible endpoint и подтвердить, что сайт и lead flow продолжают работать non-blocking.
6. Экспортировать агрегированные данные и удалить test site, подтверждая exit path.
7. Если рассматривается CE, отдельно развернуть exact `v3.2.1+`, проверить отсутствие `/storybook`, backup/restore и upgrade procedure; не использовать старые `v3` tags.

**Красные флаги:** CE ниже `v3.2.1`; `latest` без reviewed digest/pin; отправка email/CRM brief/user IDs в custom properties; отказ от собственного event taxonomy; предположение «cookie-free = compliance решена»; выбор CE ради экономии без ClickHouse/Postgres/backup/patching ownership; raw analytics становится единственным источником business truth.

Репозиторий: https://github.com/plausible/analytics

Первичные источники: [README](https://github.com/plausible/analytics/blob/master/README.md), [v3.2.1 security release](https://github.com/plausible/analytics/releases/tag/v3.2.1), [Security policy](https://github.com/plausible/analytics/blob/master/SECURITY.md), [Data policy](https://plausible.io/data-policy), [Pricing](https://plausible.io/#pricing), [Export](https://plausible.io/docs/export-stats).

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — следующий stable после `0.151.0`; prerelease `0.152.x` не продвигается до подтверждённого stable capability delta.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — workload identity/progressive discovery только после нормативного spec/SEP и cross-client conformance evidence.
- [`plausible/community-edition`](https://github.com/plausible/community-edition) — следить за следующим CE LTR, security floor и разрывом возможностей Cloud/CE, если появится реальная self-host requirement.

### Topic для разведки

**Identity provenance across AI-connected apps and analytics sinks.** Когда один agent conversation одновременно использует несколько Google identities, внешние tools и downstream analytics, каждое полученное утверждение и каждое действие должны иметь source account, permission snapshot и data-class provenance. Удобство объединённого контекста не должно превращаться в неявное объединение trust domains.

## 2026-08-30

### Вывод дня

Порог выпуска прошли три сигнала. Сегодняшний практический сдвиг — не новый frontier-model, а ужесточение причинной модели агентных систем: результат MCP-инструмента теперь может быть преобразован расширением до попадания в модель, permission state должен инвалидировать старые approvals, а durable execution получает публичный backend-контракт вместо привязки к одному workflow engine. Отдельного свежего model/design/marketing релиза, который по проверенному влиянию превосходил бы эти изменения, не найдено.

### 1. Codex 0.151.0 делает extension layer частью доверенной цепочки MCP и закрывает stale-authorization классы

29 августа OpenAI выпустила Codex CLI `0.151.0`. Наиболее значимое изменение: extensions теперь могут **инспектировать или заменять результат MCP tool call до того, как его увидит модель**. В том же релизе появился конфигурируемый grace period для optional MCP discovery и улучшено объединение repository plugin catalogs. Security/reliability fixes сохраняют restored permission profiles между TUI turns, не позволяют `/cd` ослабить sandbox, делают tool availability и reasoning model-aware при switch/fallback, учитывают nested-subagent token usage в бюджете root goal и не дают stale Guardian classification авторизовать действие после изменения permission state.

**Практическое применение:** audit trail больше не должен записывать только `tool -> result`. Для governed MCP path нужен минимум `raw_result_digest -> transformer identity/version -> model_visible_result_digest`, плюс effective permission/capability snapshot, на котором было принято решение. Если extension изменяет результат, это отдельная privileged provenance boundary. Root-level cost budget также должен агрегировать вложенных subagents, а смена permission state должна инвалидировать ранее вычисленные approval/classification decisions.

**Риск и ограничения:** сама возможность трансформации не означает, что каждая установка её использует. Неправильная реализация receipts может начать хранить сырой чувствительный MCP payload ради аудита и тем самым ухудшить privacy. Codex развивается быстро; `main` уже ушёл вперёд после tagged release, поэтому production contract следует pin-ить на release и проверять black-box fixtures на целевой OS/configuration.

**Сильный контраргумент:** для bounded `codex exec` без extensions, MCP transforms и native nested agents отдельная архитектурная миграция не нужна. Это верно: достаточен targeted canary и capability-specific version floor. Новую provenance schema стоит активировать только когда transform capability реально включена.

**Кому полезно:** agent-platform builders, MCP/plugin developers, AppSec, FinOps и команды с многоагентным Codex runtime.

Источники: [Codex 0.151.0](https://github.com/openai/codex/releases/tag/rust-v0.151.0), [Codex repository](https://github.com/openai/codex).

### 2. Claude Code 2.1.251 закрывает filesystem TOCTOU и переводит model-switch / managed-setting changes в явные control points

28 августа Anthropic выпустила Claude Code `2.1.251`. Релиз исправляет TOCTOU-класс, при котором `Read`/`Write`/`Edit` могли пройти permission check, а затем последовать по заменённой symlink и прочитать или изменить файл вне одобренного пути. Отдельно закрыты plugin path traversal, чтение workflow `scriptPath` до permission check, обход `Read(...)` deny через symlinked Grep/Glob paths и auto-approval некоторых arithmetic shell assignments.

Одновременно появились `PreModelSwitch` и `PostModelSwitch` hooks; resume hooks получают staleness session и оценку re-cache cost. Server-managed настройки, которые ослабляют sandbox, терминируют TLS, меняют proxy или inject credentials, теперь требуют approval. То же относится к чувствительным `ANTHROPIC_CUSTOM_HEADERS` из managed/project settings. Browser actions в Claude in Chrome теперь проходят через Claude Code permission checks. Релиз также добавляет spend-limit и prompt-cache telemetry surfaces.

**Практическое применение:** в agent-fleet regression suite нужен adversarial symlink-swap fixture, а не только статическая проверка пути до tool call. Model switch/fallback стоит считать сменой execution context: hook может зафиксировать effective policy, tool availability, cost tier и причину switch, но server-side authorization всё равно должна выполняться отдельно. Изменения managed settings, затрагивающие credentials/network/sandbox, должны оставлять approval receipt с прежним и новым effective state.

**Риск и ограничения:** Claude Code — proprietary runtime; release notes не заменяют black-box verification. Исправление конкретных path/symlink случаев не превращает локальный agent process в полную isolation boundary. В issue tracker уже появился воспроизводимый UI regression `2.1.251`, поэтому глобальный `latest` без canary остаётся плохой политикой даже когда релиз содержит важные security fixes.

**Сильный контраргумент:** disposable VM/container с short-lived credentials, egress controls и protected remote создаёт более сильную boundary, чем patch-level fixes внутри coding agent. Согласен; `2.1.251` следует считать defense-in-depth/version floor для Claude-host workflows, а не заменой внешней изоляции.

**Кому полезно:** platform engineering, AppSec, Claude Code fleets, self-hosted runners и команды с background/remote agent sessions.

Источники: [Claude Code 2.1.251](https://github.com/anthropics/claude-code/releases/tag/v2.1.251), [Claude Code repository](https://github.com/anthropics/claude-code).

### 3. Pydantic AI 2.36.0 открывает публичный backend API для durable execution

29 августа опубликован `pydantic-ai v2.36.0` (release помечен датой 28 августа). Главное изменение — `@durable_operation` для capabilities и **публичный backend API для сторонних durable execution engines**. Ранее основной путь был теснее связан с first-party/co-maintained integrations; теперь framework явно создаёт extension seam для собственного durable backend. В релизе также появились стабильные `InstructionPart.id`, обязательное explicit имя операции для `@durable_operation`, `clai --mcp-config` с tool-call streaming и async iterables для realtime audio.

**Практическое применение:** Python agent platform может оставить typed agent/capability contract в Pydantic AI, но использовать собственный durable scheduler/queue, не превращая Temporal/Prefect/DBOS в обязательную доменную зависимость. Stable instruction/operation IDs полезны для causal replay, reconciliation и receipts. Правильная граница: framework управляет orchestration adapter, а application-owned ledger хранит idempotency key, side-effect state, retry count и бизнес-истину.

**Риск и ограничения:** `public API` не равно зрелому cross-backend semantic standard. Retry, exactly-once illusion, cancellation, approval resume и crash-after-side-effect остаются обязанностью конкретного backend/application. Framework быстро развивается, а telemetry при включённой instrumentation по умолчанию способна включать prompts, completions, tool arguments/results и binary content — privacy-safe deployment требует явных `include_content=False` / `include_binary_content=False` либо собственного OTel policy.

**Сильный контраргумент:** если приложение уже использует один workflow engine и имеет собственную очередь/state machine, прямой Temporal/DBOS/Celery/Postgres-job adapter проще и более переносим. `@durable_operation` полезен только если Pydantic AI уже является реальным agent-runtime слоем либо публичный backend API заметно сокращает bespoke lifecycle code.

**Кому полезно:** Python agent platforms, background research/analytics, durable HITL workflows и команды с собственным scheduler/runtime.

Источники: [Pydantic AI v2.36.0](https://github.com/pydantic/pydantic-ai/releases/tag/v2.36.0), [Pydantic AI documentation](https://pydantic.dev/docs/ai/), [Logfire / OpenTelemetry controls](https://pydantic.dev/docs/ai/integrations/logfire/).

## GitHub Radar

### Репозиторий периода: `pydantic/pydantic-ai`

**Текущий релиз и активность:** latest stable на момент проверки — `v2.36.0`; после release `main` продолжил активно двигаться, включая durable-exec CI work, Google/Gemini transport fixes и AG-UI corrections. Репозиторий имеет сотни открытых Issues и активный PR поток, поэтому это не maintenance-only проект, но быстрый cadence требует exact pinning и project-level canary.

**Лицензия и коммерческое использование:** core repository лицензирован по MIT; коммерческое использование, модификация и распространение разрешены при сохранении copyright/license notice. Hosted model providers, Logfire и внешние durable engines имеют собственные условия и не наследуют MIT автоматически.

**Документация:** публичная документация покрывает typed agents, tools, MCP, realtime, image generation, embeddings и durable execution. `pydantic-ai-harness` вынесен отдельно, что позволяет не тянуть coding-agent filesystem/shell surface в обычный runtime.

**CI/tests:** репозиторий имеет крупный `ci.yml`, latest-version canary, harness compatibility, provider health и отдельные durable-execution test lanes; свежие commits продолжают улучшать Temporal/durable CI. Это хороший maintenance signal, но собственная suite не доказывает idempotency конкретного application side effect.

**Issue activity:** issue/PR поток большой и живой. Это полезно для discovery edge cases; одиночный issue не является доказанным universal defect без воспроизведения на exact version/provider.

**Security model:** typed arguments/output validation не является authorization или sandbox. Tool function остаётся реальной application capability. Проект использует GitHub Security Advisories; в августе был опубликован advisory по DNS-rebinding для local web UI, что отдельно подчёркивает: developer UI и local agent process нужно считать privileged surface.

**Telemetry/data handling:** Pydantic AI instrumentation основана на OpenTelemetry и может отправляться в Logfire либо другой OTel backend. Content capture при instrumentation по умолчанию включает prompts/completions/tool arguments/results, а binary capture — двоичные payloads; для privacy-sensitive workloads это нужно явно выключать или фильтровать до exporter. Без настроенной instrumentation само наличие core SDK не означает обязательный hosted telemetry backend.

**Install surface:** минимально — `pydantic-ai` или slim/provider-specific installation; durable engines и realtime/providers подключаются extras. Чем меньше extras и capability bundles, тем уже credential/dependency surface.

**Integration cost:** низкий для bounded typed Agent adapter; средний для tools/MCP и одного durable backend; высокий, если `RunState`, framework operation IDs или provider-specific objects становятся доменной моделью приложения.

**Reversibility:** высокая при application-owned state/interfaces и thin adapter; заметно ниже, если Pydantic durable state становится единственной историей side effects/retries.

**Известные ограничения:** быстрый 2.x cadence; provider parity неполна; новая public durable backend seam ещё требует cross-backend production evidence; tool schema validation не ограничивает side effects; local UI и telemetry должны проходить отдельный security/privacy review.

**Production-readiness — собственная оценка:** **4/5** для pinned core agents с узкими tools, application authorization и reviewed telemetry; **3/5** для нового third-party durable backend API до crash/replay/idempotency canary на выбранном engine.

**Validation plan — 90 минут:**

1. Pin `pydantic-ai==2.36.0` в disposable Python 3.12 environment.
2. Реализовать минимальный in-memory test backend с явно именованной `@durable_operation` и application-owned idempotency key.
3. Прогнать success, crash-after-side-effect-before-ack, retry и resume; внешний side effect должен фиксироваться один раз.
4. Проверить, что stable instruction/operation IDs сохраняют causal mapping через resume.
5. Сравнить semantics с direct Temporal либо простым project-owned queue adapter; framework не должен становиться единственной БД workflow state.
6. Включить локальный OTLP sink с `include_content=False` и synthetic secret; secret не должен попадать в spans. Без instrumentation не должно появиться неожиданного telemetry egress.
7. Удалить adapter и подтвердить, что domain records не требуют миграции.

**Красные флаги:** floating `main/latest`; `@durable_operation` ошибочно считается exactly-once гарантией; raw prompts/tool results уходят в telemetry; broad shell/network tools; framework state — единственный audit ledger; local `to_web` используется как публичная production admin surface; provider/extras устанавливаются без необходимости.

Репозиторий: https://github.com/pydantic/pydantic-ai

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — provenance transformed MCP results, invalidation stale Guardian decisions и root-level subagent budgets.
- [`anthropics/claude-code`](https://github.com/anthropics/claude-code) — filesystem TOCTOU, managed-settings approvals и model-switch hooks.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — workload identity и progressive discovery; принимать в production только после нормативных SEP/spec, а не по roadmap.

### Topic для разведки

**Causal provenance across transformed tool results and durable resume:** система должна доказуемо отвечать, что вернул tool, кто и как преобразовал результат, какой permission/capability snapshot действовал, был ли side effect уже committed до retry/resume и какой payload фактически увидела модель.

### Discovery note — `@GitHubRadar`

Публичный канал `https://t.me/GitHubRadar` используется только как discovery feed. В сегодняшнем просмотре не найден кандидат, который после primary-source revalidation превосходил бы три сигнала выше или прошёл project-specific promotion gate. Сам факт публикации, stars и рекламное размещение не повышают score.

## 2026-08-29

### Вывод дня

Порог выпуска прошли четыре сигнала. Самый важный — не новый model benchmark, а подтверждённый компромисс hosted developer compute: инцидент JetBrains Cadence показывает, что облачный coding/runtime слой нужно считать credential-bearing supply-chain infrastructure. В продуктовой части Google одновременно вывел в GA специализированные video и speech surfaces, а в Google Cloud появились enforceable spend caps для API/agent workloads. Нового frontier coding model или IDE-релиза, который сегодня менял бы архитектуру сильнее этих событий, в проверенных первичных источниках не найдено.

### 1. JetBrains подтвердил эксплуатацию Cadence через CVE-2026-63077 и экспозицию credentials/source data

28 августа JetBrains обновил отчёт об инциденте Cadence и подтвердил, что `api.cadence.jetbrains.com` был уязвим к критическому TeamCity `CVE-2026-63077` и успешно эксплуатировался. Подтверждённый период активности — 8–24 августа 2026 года. По данным JetBrains, злоумышленники получили доступ к персональным данным, полной резервной копии Cadence за 2024 год, нескольким AWS IAM credentials, данным в S3 и потенциально к исходному коду, синхронизированному из PyCharm. JetBrains прямо рекомендует считать скомпрометированными все credentials/secrets, которые хранились или были доступны Cadence executions, и отдельно признаёт, что сервер должен был быть пропатчен, но не был.

**Практическое применение:** hosted coding agents, cloud dev environments и удалённые runners следует проектировать так, чтобы компрометация control plane не автоматически означала компрометацию долгоживущих production credentials. Минимальный контракт: short-lived workload identity, task/repo-scoped tokens, отдельный secret inventory, быстрая revocation, отсутствие долговечных секретов в backups/logs, protected branches и независимый audit внешних side effects. Если Cadence использовался, это уже incident-response задача: revoke/rotate, проверить SCM/IAM/registries/webhooks/SSH/signing keys и commits за affected window.

**Риск и ограничения:** подтверждённый scope относится к Cadence и указанному серверу; из этого нельзя делать вывод о компрометации всех JetBrains IDE, TeamCity Cloud или любого hosted coding agent. Масштаб доступа к клиентским storage buckets ещё расследуется.

**Сильный контраргумент:** инцидент не является аргументом отказаться от hosted agents вообще. Disposable runners, минимальные privileges, OIDC/short-lived credentials и независимая authorization boundary существенно ограничивают ущерб; self-hosting без patch discipline может быть не безопаснее.

**Кому полезно:** AppSec, platform/DevOps, владельцам coding-agent fleets, CI/CD, package/release automation и компаниям с облачными developer workspaces.

Источники: [JetBrains Cadence incident, updated 2026-08-28](https://blog.jetbrains.com/pycharm/2026/08/cadence-security-incident-august-2026/), [CVE-2026-63077 advisory](https://blog.jetbrains.com/teamcity/2026/07/cve-2026-63077/), [active-exploitation guidance](https://blog.jetbrains.com/teamcity/2026/08/cve-2026-63077-update/).

### 2. Gemini Omni Flash 1.1 вышел в GA: video workflow теперь включает continuation, first/last-frame interpolation и 4K output

27 августа Gemini API выпустил `gemini-omni-1.1-flash` в GA. Модель поддерживает продолжение существующего видео через `extend`, генерацию перехода между первым и последним кадрами через `image_to_video` с двумя изображениями и явный `resolution` control: `360p`, `720p`, `1080p`, `4k`. Google отдельно указывает, что 1080p и 4K получаются через upscaling. Preview endpoint `gemini-omni-flash-preview` объявлен к deprecation 30 сентября 2026 года.

**Практическое применение:** marketing/design pipelines могут разделить workflow на `draft → review → extend/interpolate → final export`, а не генерировать каждый ролик целиком заново. Для миграции с preview нужен paired replay на реальных брендовых задачах: motion continuity, text/logo fidelity, aspect/resolution, safety refusals, latency и фактическая стоимость. В asset metadata полезно хранить исходную resolution и факт upscale, чтобы 4K export не выдавался за native 4K generation.

**Риск и ограничения:** GA не гарантирует deterministic visual continuity или brand fidelity. Upscaled 4K — не то же самое, что нативная генерация в 4K. Rights, moderation, data retention и regional availability остаются отдельными продуктово-юридическими границами и не унифицируются одним model ID.

**Сильный контраргумент:** специализированный video provider или native Veo workflow может давать больше provider-specific controls. Omni имеет смысл как production default только после собственного quality/cost benchmark; одна унифицированная API surface сама по себе не доказывает лучшую экономику.

**Кому полезно:** дизайну, performance/content marketing, creative automation, ecommerce/media pipelines и разработчикам мультимедийных продуктов.

Источник: [Gemini API release notes — 2026-08-27](https://ai.google.dev/gemini-api/docs/changelog).

### 3. Gemini 3.5 Transcribe и Transcribe Live вышли в GA как отдельные speech-to-text surfaces

26 августа Google выпустил `gemini-3.5-transcribe` и `gemini-3.5-transcribe-live` в GA. Batch/non-streaming модель поддерживает utterance-level language detection для 85+ языков, speaker diarization, word-level timestamps и vocabulary biasing до 1 000 терминов. Live-вариант работает по двунаправленному WebSocket, выдаёт interim/final events и поддерживает несколько VAD strategies. Формулировки Google о высокой точности и низкой задержке являются vendor claims; независимый benchmark в сегодняшнем выпуске не использован.

**Практическое применение:** интервью, customer research, call/support analytics, meeting intelligence и voice UI теперь можно строить без отдельной модели для diarization/timestamps. Для аналитики правильный pipeline — `audio → immutable transcript segments → speaker/time evidence → отдельная extraction/classification stage`, а не прямое превращение вероятностного transcript в CRM action. Custom vocabulary особенно полезен для брендов, фамилий, продуктовых терминов и отраслевого жаргона.

**Риск и ограничения:** transcript остаётся вероятностным; имена, цифры, юридические формулировки и смешанная речь требуют confidence-aware или human review. Audio/voice почти всегда содержит PII, поэтому consent, retention, access control и redaction должны проектироваться до отправки provider. Live WebSocket добавляет reconnect, ordering, duplicate/interim-event и session-lifecycle edge cases.

**Сильный контраргумент:** для конфиденциального аудио локальная/self-hosted transcription может быть рациональнее даже при худшей средней точности. Если realtime latency не нужна, batch path проще и лучше воспроизводится, чем Live API.

**Кому полезно:** маркетинговым исследованиям, продуктовой аналитике, contact centers, accessibility, voice products и meeting/call automation.

Источник: [Gemini API release notes — 2026-08-26](https://ai.google.dev/gemini-api/docs/changelog).

### 4. Google Cloud добавил enforceable spend caps для Gemini API и agent workloads

26 августа Google Cloud представил расширенные FinOps controls для agent workloads. Самое практически важное — spend-cap budgets: для одного project + eligible service можно задать месячный предел; при достижении лимита новые API calls блокируются, а уже выполняющиеся requests завершаются. Текущая документация перечисляет среди eligible services Gemini API, Gemini Enterprise Agent Platform, Cloud Run и Cloud Run functions. Alerts отправляются на 50%, 80% и 100%; после срабатывания cap usage восстанавливается только после ручного lift. Google отдельно предупреждает, что enforcement не мгновенный и возможен небольшой overage из-за задержки cost accounting.

Параллельно Google заявляет Flexible Savings Plans со скидкой 10% при годовом и 20% при трёхлетнем spend commitment. Deferred-execution pricing с экономией «до половины inference cost» обозначен только как **coming soon** и не должен считаться доступной production capability.

**Практическое применение:** cost budget становится частью runtime contract, а не только dashboard после факта. Для experiment/agent projects можно комбинировать provider-side hard cap с application-level per-run budget, tool-call limits и kill criteria. В production стоит разделять проекты/сервисы так, чтобы исчерпание исследовательского бюджета не остановило критический пользовательский traffic.

**Риск и ограничения:** cap считается по gross/estimated costs и ограничен одним project и одним eligible service; multi-project/org budgets этим механизмом не закрываются. Cap способен остановить сервис и требует ручного восстановления, которое может занять до часа. Финансовая граница также ничего не говорит о capability blast radius: дешёвый destructive tool call остаётся опасным.

**Сильный контраргумент:** provider-neutral FinOps и собственные quotas лучше сохраняют multi-cloud portability. Это верно; Google-native spend cap полезен как последний server-side circuit breaker, но не должен становиться единственным cost-control или availability mechanism.

**Кому полезно:** FinOps, platform engineering, AI product owners, background analytics, marketing automation и команды с long-running agents.

Источники: [Google Cloud FinOps for agents — 2026-08-26](https://cloud.google.com/blog/products/ai-machine-learning/flexible-billing-and-cost-controls-for-agents-on-google-cloud), [Spend Cap documentation](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps).

## GitHub Radar

### Репозиторий периода: `herdrdev/herdr`

**Что это:** Apache-2.0 Rust runtime для долгоживущих coding-agent sessions. Herdr держит panes и agents в background server, поддерживает detach/reattach, named sessions, SSH remote attach, read-only terminal observers и writable controllers, а также распознаёт несколько coding agents. Latest stable на момент проверки — `v0.8.2` от 19 августа; `master` продолжает активно меняться, поэтому production следует pin-ить на release, а не на ветку.

**Maintenance и release activity:** после `v0.8.2` в `master` продолжаются ежедневные fixes вокруг terminal input, worktree trust, agent detection, hooks и release automation. Это хороший сигнал живого сопровождения и одновременно признак pre-1.0 churn.

**License:** Apache-2.0.

**Documentation/install surface:** standalone binary/runtime; документированы source build, installer/package-manager paths, persistent sessions и SSH remote attach. Remote attach использует обычную OpenSSH authentication; при отсутствии подходящего remote binary интерактивный клиент может предложить установку в `~/.local/bin/herdr`, а non-interactive flow fail-closed вместо тихой модификации хоста. Для custom builds есть `HERDR_REMOTE_BINARY`.

**CI/tests:** CI запускается на Ubuntu, macOS и Windows, использует pinned GitHub Actions, Rust format/clippy/nextest и platform-specific smoke. Windows path включает отдельные ConPTY package/installer probes и негативный test, который проверяет отказ от tampered local bundle.

**Issue activity:** tracker активен. Свежие reports затрагивают Git discovery/restore blocking, Windows keybindings, agent detection после launcher/runtime changes и lifecycle authority после transient foreground takeover. Это **user issue reports**, а не подтверждённые universal defects, но именно эти классы нужно включить в integration canary.

**Security model:** Herdr — terminal/session runtime, а не sandbox и не authorization layer. Agent processes выполняются с effective privileges пользователя/host. Remote trust опирается на SSH; writable controller, plugins и agent hooks являются privileged surfaces. Отдельный conventional root или `.github/SECURITY.md` при проверке не найден — это process-documentation gap, а не доказательство отсутствия private vulnerability handling.

**Telemetry/data handling:** в целевом поиске source/docs не обнаружена явная first-party remote analytics/telemetry surface. Это не доказательство её полного отсутствия. Herdr хранит и передаёт terminal/session state; фактический model/source egress определяется запускаемыми агентами и remote/SSH topology.

**Integration cost:** низкий для disposable local pilot, средний для adapter вокруг нескольких agent CLIs и remote sessions, высокий если Herdr session/plugin state начинает становиться canonical orchestration state.

**Reversibility:** высокая, если Herdr остаётся replaceable terminal/runtime backend и project/task/policy receipts находятся вне него. Ниже, если workflow начинает зависеть от Herdr-specific pane/session IDs, hook semantics и plugin state.

**Production-readiness — собственная оценка: 78/100.** При pinned release, disposable/low-privilege hosts и внешней policy boundary Herdr уже выглядит пригодным для pilot/controlled developer use. Для unattended high-authority agent fleet без отдельного sandbox, short-lived credentials и application-owned governance — рано.

**Validation plan — 60–90 минут:**

1. Pin `v0.8.2` в disposable repo/VM и проверить artifact provenance.
2. Запустить Claude/Codex (или два реально используемых CLI) в отдельных panes; проверить `idle/working/blocked` detection.
3. Выполнить detach/reattach и restart/restore; убедиться, что prompt/tool action не дублируется после восстановления.
4. Подключиться через SSH к disposable host без production secrets; проверить non-interactive failure path и expected binary selection.
5. Сравнить read-only observer и writable controller; observer не должен получать input/takeover authority.
6. Воспроизвести один relevant fresh issue fixture: Git-worktree create timeout либо detection после текущего agent launcher.
7. Полностью удалить Herdr adapter/runtime и подтвердить, что repository state и canonical orchestration ledger не требуют миграции.

**Красные флаги:** floating `master`/preview; agent runtime получает production credentials просто потому, что находится в pane; Herdr session state объявляется authorization truth; plugins/controllers подключаются без allowlist; remote install происходит без provenance verification; отсутствие собственных regression fixtures на используемых версиях Claude/Codex; open restore/detection reports игнорируются как «только UI».

Репозиторий: [herdrdev/herdr](https://github.com/herdrdev/herdr), [v0.8.2](https://github.com/herdrdev/herdr/releases/tag/v0.8.2), [CI](https://github.com/herdrdev/herdr/blob/master/.github/workflows/ci.yml), [remote/persistence docs](https://github.com/herdrdev/herdr/blob/master/docs/versions/0.8.2/website/src/content/docs/persistence-remote.mdx).

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — task/session lifecycle, sandbox/permission semantics и App Server evolution; проверять только tagged releases и current docs.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — progressive discovery/workload identity после появления нормативных SEP/spec, а не по roadmap claims.
- [`github/gh-aw`](https://github.com/github/gh-aw) — separation model reasoning → deterministic safe-output writer и event-driven PR loops.

### Topic для разведки

**Runtime/session layer vs governance layer:** terminal/session persistence, tool capability transport и право на irreversible side effect — три разные границы. Runtime может пережить disconnect и переносить agent state, но canonical authority, idempotency и audit receipt должны оставаться application-owned.

### Discovery-source note

Публичный preview `@GitHubRadar` просмотрен как untrusted discovery feed. В видимом срезе были полезные general-purpose OSS candidates, но ни один не прошёл сегодняшний AI-specific promotion gate. Сам канал прямо сообщает о платных размещениях, поэтому публикация в нём не считается evidence и не повышает score; все promoted findings по-прежнему требуют первичной проверки репозитория и официальной документации.

## 2026-08-28

### Вывод дня

Порог выпуска прошли четыре сигнала: VS Code вынес agent sessions в отдельный host/protocol, Codex добавил task-to-task coordination и interrupt hooks, Cursor разрешил prototype-first development без repository, а ChatGPT Work получил event-triggered tasks из Gmail, Slack и GitHub. Главная тема — session protocol, capability protocol и authority protocol окончательно расходятся в самостоятельные архитектурные слои.

### 1. VS Code представил Agent Host и открытый Agent Host Protocol

26 августа Microsoft представила Agent Host — отдельный процесс, владеющий долгоживущими agent sessions, — и Agent Host Protocol (AHP) для подключения clients. Session может переживать закрытие folder/editor, синхронизироваться между несколькими clients, работать локально или remote и поддерживать разные harnesses, включая Copilot и Claude, без унификации их внутреннего agent loop.

AHP стандартизирует client-facing session/state/control surface: host является authoritative session state, clients получают snapshot и упорядоченные actions, могут наблюдать progress, approve tool calls, cancel work и предоставлять client-side tools.

**Практическое применение:** строить собственный dashboard, browser/mobile companion или control console поверх одной live session, не интегрируясь отдельно с каждым harness SDK.

**Риск и ограничения:** host становится высокодоверенной state/control boundary. Multi-client approve/cancel/tool contribution требует отдельной actor/authority model. Protocol pre-1.0 и допускает breaking changes.

**Сильный контраргумент:** для одного пользователя, одной IDE и одного harness собственный session API проще. AHP оправдан при реальном cross-client roaming или harness portability.

**Кому полезно:** IDE/agent-platform builders, remote coding, multi-agent governance и custom consoles.

Источники: [Introducing the Agent Host](https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture), [Agent Host concepts](https://code.visualstudio.com/docs/agents/concepts/agent-host), [AHP repository](https://github.com/microsoft/agent-host-protocol).

### 2. Codex 0.150.0 добавил взаимодействие task↔task и Interrupt hooks

26 августа Codex CLI `0.150.0` добавил упоминание tasks через `@`, чтение/создание/message exchange между Codex tasks и `Interrupt` hooks для command или MCP handler при прерывании top-level turn. Релиз также усилил project trust, persistence managed deny-read rules, credential redaction и несколько sandbox/MCP paths.

**Практическое применение:** использовать executor-native task graph для bounded coordination, а Interrupt hook — для cleanup, checkpoint или audit notification. Каждое message/interrupt side effect связывать с application-owned causal receipt и idempotency key.

**Риск и ограничения:** cancel/retry/reconnect способны повторно вызвать handler; task-to-task messaging расширяет causal graph и осложняет actor provenance.

**Сильный контраргумент:** внешний queue/state machine переносимее. Для bounded `codex exec` новые surfaces вообще не нужны.

**Кому полезно:** coding-agent fleets, CI remediation и orchestrators.

Источник: [Codex 0.150.0](https://github.com/openai/codex/releases/tag/rust-v0.150.0).

### 3. Cursor Cloud Agents могут начинать продукт без repository

27 августа Cursor добавил режим Start from scratch: prompt запускает Cloud Agent без подключённого GitHub/SCM, в фоне создаётся временный Origin repo, live environment port-forwardится в browser, а готовый результат можно сохранить как private/internal Origin repository и при наличии Vercel опубликовать по live URL.

**Практическое применение:** быстрые landing pages, маркетинговые эксперименты, internal dashboards, analytics mini-tools и disposable prototypes до formal repository bootstrap.

**Риск и ограничения:** governance появляется после кода: до создания normal repo могут отсутствовать привычные branch protection, CI и repository-owned policies. Путь усиливает coupling Cursor Origin + Cloud Agents + Vercel; live preview расширяет network/data surface.

**Сильный контраргумент:** repo-first GitHub workflow остаётся лучше для production SDLC. Новый путь разумен как prototype-first, а не новый default.

**Кому полезно:** design, marketing, product и rapid-prototyping developers.

Источник: [Cursor — Start from scratch, without a repo](https://cursor.com/changelog/start-from-scratch).

### 4. ChatGPT Work получил event-triggered tasks из Gmail, Slack и GitHub

25 августа Scheduled Tasks в ChatGPT Work получили webhook triggers для новых Gmail messages, Slack channel messages и GitHub pull request activity. Eligible users могут создавать event-driven task на web/mobile; действия, требующие approval, приостанавливаются до проверки. Shared task использует собственные app permissions получателя, а не credentials автора.

**Практическое применение:** semantic triage клиентских писем, Slack feedback, PR changes и подготовка аналитических/маркетинговых next steps без постоянного polling.

**Риск и ограничения:** connector event является untrusted prompt input. `Event occurred` не означает `action authorized`; близкие события могут быть объединены, а permissions зависят от connected app конкретного исполнителя.

**Сильный контраргумент:** для детерминированных процессов обычный webhook worker/GitHub Actions проще и лучше тестируется. Work оправдан при необходимости языкового понимания и неопределённости.

**Кому полезно:** marketing ops, support, analytics, engineering management и PR triage.

Источники: [ChatGPT release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes), [Scheduled tasks in ChatGPT](https://help.openai.com/en/articles/10291617-tasks-in-chatgpt), [Enterprise/Edu release notes](https://help.openai.com/en/articles/10128477-chatgpt-enterprise-edu-release-notes).

## GitHub Radar

### Репозиторий периода: `microsoft/agent-host-protocol`

- **Лицензия:** MIT.
- **Зрелость:** pre-1.0 protocol с SDK для нескольких языков; spec и SDK versions развиваются независимо.
- **CI/tests:** schema/type tests и generation/validation нескольких client packages; сильнее типичного spec-only repository.
- **Security model:** transport auth недостаточен; approve/cancel/client tools требуют application actor/authority checks.
- **Telemetry/data handling:** сам protocol переносит session/chat/terminal/changeset state; retention и telemetry определяются host, harness и client.
- **Install surface:** TypeScript/Rust/Go/Kotlin/Swift/.NET clients и standalone VS Code host; remote WebSocket/tunnels создают отдельную attack surface.
- **Integration cost:** средний для read-only viewer, высокий если host заменяет собственный task/governance ledger.
- **Reversibility:** высокая при projection adapter, низкая если AHP SessionState становится domain model.
- **Production-readiness:** 3/5 для bounded VS Code-host interoperability; 2/5 как canonical authorization/governance layer до 1.0.

**Validation plan — 60–90 минут:** pin released spec/client; поднять disposable `code agent host`; подключить два clients; проверить disconnect/reconnect snapshot/replay без duplicate side effect; approve/cancel actor authority; исчезновение client-contributed tool; localhost token и negative remote/tunnel connection; удалить adapter без migration.

**Красные флаги:** `main` как contract, host state = authorization truth, approval без actor provenance, remote tunnel без trust review, task ledger заменён AHP state, stale client tool остаётся доступным.

Репозиторий: https://github.com/microsoft/agent-host-protocol

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — executor-native tasks/hooks и causal state.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — discovery/workload identity.
- [`github/gh-aw`](https://github.com/github/gh-aw) — separation untrusted reasoning и deterministic writer.

### Topic для разведки

**Session protocol ≠ capability protocol ≠ authority protocol:** AHP синхронизирует session state, MCP переносит capabilities, а право на irreversible action и audit receipt должно оставаться application-owned.

## 2026-08-25

### Вывод дня

Порог выпуска прошли три сигнала: deprecation inbound MCP surface Codex, general availability enterprise-managed authorization для Figma MCP и появление event-driven completion для batch AI jobs в Vercel AI SDK. Общая тема — перенос orchestration и identity из ad hoc интеграций в явные lifecycle contracts.

### 1. OpenAI депрекейтит `codex mcp-server` в пользу App Server

24 августа OpenAI пометила команду `codex mcp-server` deprecated. Для programmatic integration рекомендуется Codex App Server; для использования Codex из Claude Code — официальный Codex plugin. Это не означает отказ Codex от MCP client functionality: deprecated именно режим, в котором Codex сам выставлялся наружу как MCP server.

**Практическое применение:** найти inbound integrations, завязанные на `codex mcp-server`, и мигрировать их через contract tests на session creation, cancellation, approvals, auth propagation, streaming/event ordering и reconnect recovery. Canonical jobs/receipts следует оставить application-owned.

**Риск и ограничения:** deprecation пока не равна shutdown date. App Server имеет более широкую surface, поэтому механическая замена команды способна незаметно изменить trust boundary.

**Сильный контраргумент:** пользователям `codex exec`, IDE, обычного CLI и Codex как MCP client отдельный migration project не нужен.

**Кому полезно:** agent-platform builders, IDE integrations и orchestration/control-plane teams.

Источник: [Codex changelog](https://developers.openai.com/codex/changelog).

### 2. Enterprise-managed authorization для Figma MCP стала GA

24 августа Figma сообщила, что admins Organization/Enterprise могут централизованно управлять Figma MCP connection к AI agents через identity provider, уменьшая индивидуальный OAuth onboarding и повторные consent prompts. Доступ к конкретным файлам по-прежнему определяется существующими правами пользователя; централизованная аутентификация не должна трактоваться как дополнительная file authorization.

**Практическое применение:** формализовать identity lane `individual_oauth | enterprise_managed`, централизовать provisioning/revocation и сохранять IdP/client/actor provenance в audit receipt.

**Риск и ограничения:** аутентификация не разрешает write operation автоматически. Ошибка IdP/configuration увеличивает correlated blast radius, а первоначальная provider/client matrix ограничена.

**Сильный контраргумент:** для небольшой команды individual OAuth дешевле и менее связан с одним enterprise IdP. EMA оправдана только при реальной стоимости onboarding/offboarding.

**Кому полезно:** enterprise design/platform teams, IAM/AppSec и крупные Figma MCP deployments.

Источник: [Figma release notes — Enterprise-managed authorization for MCP](https://www.figma.com/release-notes/).

### 3. Vercel AI SDK добавил webhook completion для batch generation

25 августа `ai@7.0.79` добавил `webhookUrl` в experimental batch-generation API. Через AI Gateway callback передаётся в async job metadata; direct OpenAI и Anthropic batch providers не обязаны поддерживать эту Gateway-specific опцию и должны сообщать unsupported warning.

**Практическое применение:** перейти от постоянного polling к event-driven pipeline `submit → persist job → release worker → callback → validate → continue` для bulk classification, enrichment, evals и массовой генерации.

**Риск и ограничения:** API experimental, callback — privileged external input. Нужны idempotency, replay protection, state validation, authentication и fallback reconciliation. `job completed` не означает `side effect authorized`.

**Сильный контраргумент:** при небольшом объёме batch jobs polling проще, прозрачнее и provider-neutral. Gateway webhook оправдан только при измеримом orchestration overhead.

**Кому полезно:** marketing automation, analytics pipelines, bulk content/enrichment и eval infrastructure.

Источник: [Vercel AI SDK `ai@7.0.79`](https://github.com/vercel/ai/releases/tag/ai%407.0.79).

## GitHub Radar

### Репозиторий периода: `vercel/ai`

- **Лицензия:** Apache-2.0 для core repository.
- **Зрелость:** очень активный monorepo с provider, workflow, MCP, telemetry и UI packages; rapid cadence требует exact pinning.
- **CI/tests:** специализированные workflows для core/provider changes, releases и changesets; provider abstraction всё равно нуждается в application contract tests.
- **Security model:** disclosure через Vercel security process; SDK не является authorization layer, а Gateway — отдельный hosted data/control plane.
- **Telemetry/data handling:** direct-provider и Gateway routes имеют разные retention/residency boundaries; provider abstraction не равна data-policy abstraction.
- **Integration cost:** низкий для basic generation, средний для batch webhook, высокий если Gateway становится canonical routing/job/compliance state.
- **Reversibility:** высокая при application-owned model/job interface и polling fallback; низкая при зависимости от Gateway-only metadata.
- **Production-readiness:** 4/5 для pinned core/direct providers; 3/5 для experimental batch webhook до callback canary.

**Validation plan — 60–90 минут:** pin exact versions; submit synthetic batch; persist immutable correlation ID; повторить callback дважды; смоделировать delayed/out-of-order callback и failure; проверить polling recovery; подтвердить expected warning у direct providers; отключить Gateway feature flag.

**Красные флаги:** публичный callback без проверки, callback сам публикует/удаляет, experimental API считается cross-provider stable, Gateway job store — единственная запись, ZDR Gateway автоматически переносится на upstream provider.

Репозиторий: https://github.com/vercel/ai

### Watchlist

- [`openai/codex`](https://github.com/openai/codex) — переход inbound integrations к App Server.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — workload identity и progressive discovery после появления normative SEP/spec.
- [`pydantic/pydantic-ai`](https://github.com/pydantic/pydantic-ai) — state/tool security и provider compatibility.

### Topic для разведки

**Async AI callbacks как privileged external input:** authentication, replay, idempotency, causal provenance и независимая authorization side effects.

## 2026-08-24

### Вывод дня

Порог выпуска прошли четыре сигнала: Google ADK for TypeScript 2.0 сменил модель workflow/state, GitHub Agentic Workflows усилил separation между untrusted reasoning и permissioned writer, Copilot перенёс coding-agent intake в Slack/Teams, а Figma добавила layout semantics, которые ещё не отражены в публичном API contract.

### 1. Google ADK for TypeScript 2.0 изменил workflow и resume semantics

20 августа Google выпустила `@google/adk 2.0.0`. Agent стал workflow node, прежний `LLMAgentWrapper` удалён, а `BaseAgent` получил workflow/state свойства. Template agents продолжают работать, но отмечены deprecated; graph workflows и часть новой node-модели остаются experimental. Для dynamic child, способного прерываться или запрашивать пользователя, требуется явная resume policy, иначе parent может восстановиться некорректно.

**Практическое применение:** миграцию 1.x→2.0 проводить как contract-test project: custom `BaseAgent` subclasses, interruption/serialize/resume, parallel HITL/credential responses, OpenAPI path security и late-event/state ordering.

**Риск и ограничения:** major version не означает зрелость experimental graph workflow. Новые inherited fields могут конфликтовать с custom subclasses, а implicit resume assumptions — терять causal state.

**Сильный контраргумент:** для простого `LlmAgent` без dynamic workflow и durable resume миграция может не давать немедленной продуктовой выгоды.

**Кому полезно:** TypeScript agent platforms, HITL/realtime и resumable workflows.

Источники: [Google ADK for TypeScript](https://github.com/google/adk-js), [releases](https://github.com/google/adk-js/releases), [documentation](https://google.github.io/adk-docs/).

### 2. GitHub Agentic Workflows усилил model→safe-output boundary

В pre-release линии `github/gh-aw` появилась возможность продолжать agent work по PR/review comments, сохраняя write execution за отдельным Safe Outputs layer. Агент получает read context и формирует structured proposal, а permissioned writer выполняет разрешённое изменение независимо от model job credentials.

**Практическое применение:** workflow «доведи PR до green после review» без выдачи model process прямого write token; review comments сохраняются как provenance-bearing input, а writer повторно валидирует scope.

**Риск и ограничения:** PR/review comments становятся prompt-injection surface. Safe Outputs ограничивает запись, но не делает reasoning доверенным. Линия остаётся pre-release.

**Сильный контраргумент:** обычный GitHub Actions workflow + одноразовый coding agent проще и зрелее; long-lived steering нужен только при измеримой цене восстановления контекста.

**Кому полезно:** GitHub-centric DevEx, agentic CI и code-review automation.

Источник: [github/gh-aw releases](https://github.com/github/gh-aw/releases).

### 3. Copilot coding agent стал intake surface в Slack и Microsoft Teams

21 августа GitHub открыл public preview agent sessions из Slack и Microsoft Teams. Упоминание `@GitHub` в channel/thread/DM позволяет передать conversation context Copilot cloud agent, который исследует repository, выполняет изменения в cloud sandbox и открывает PR. Участники conversation могут добавлять контекст, steering или остановить session; repository permissions и дополнительные approval rules продолжают применяться.

**Практическое применение:** быстро превращать product/marketing/analytics discussion в traceable technical task, сохраняя GitHub PR как review boundary.

**Риск и ограничения:** chat content — untrusted prompt input. Shared steering усложняет causal ownership, а membership в conversation не должна заменять GitHub authorization.

**Сильный контраргумент:** GitHub Issue/PR как единственная точка постановки задачи проще аудируется. Chat-to-agent полезен только там, где языковой контекст и стоимость formal issue действительно являются bottleneck.

**Кому полезно:** engineering, product, marketing ops, analytics и internal automation.

Источники: [Copilot in Slack](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/), [Copilot in Microsoft Teams](https://github.blog/changelog/2026-08-21-shared-agentic-work-with-github-copilot-in-microsoft-teams/).

### 4. Figma добавила Auto Layout `Around` и `Evenly`, а публичный API ещё показывает только `SPACE_BETWEEN`

21 августа Figma добавила два новых режима automatic spacing: `Around` и `Evenly`, соответствующие CSS `space-around` и `space-evenly`; прежний режим переименован в `Between`. На момент проверки публичные Plugin/REST types для `primaryAxisAlignItems` продолжали документировать только `MIN | MAX | CENTER | SPACE_BETWEEN`.

**Практическое применение:** design-to-code и Figma automation должны сохранять неизвестную native semantic как `unknown/raw` и fail closed для write, пока конкретный backend не подтвердит representation.

**Риск и ограничения:** документация может отставать от editor/runtime. Это не доказывает, что ни один Figma API не способен читать или писать новые значения.

**Сильный контраргумент:** для ручной работы дизайнеров архитектурного изменения не требуется; проблема существенна только при обещании semantic round-trip fidelity.

**Кому полезно:** design systems, Figma MCP/plugin tooling и design-to-code.

Источники: [Figma release notes](https://www.figma.com/release-notes/), [Plugin API `primaryAxisAlignItems`](https://developers.figma.com/docs/plugins/api/properties/nodes-primaryaxisalignitems/), [REST node types](https://developers.figma.com/docs/rest-api/file-node-types/).

## GitHub Radar

### Репозиторий периода: `google/adk-js`

- **Лицензия:** Apache-2.0.
- **Зрелость:** официальный Google SDK; major `2.0.0` меняет core state/workflow contract, а `main` продолжает развиваться.
- **CI/tests:** cross-platform package/release validation; необходимы собственные black-box fixtures для resume, HITL binding и provider integrations.
- **Security model:** framework предоставляет workflow/tool/HITL primitives, но authorization остаётся application concern.
- **Telemetry/data handling:** OTel/integrations зависят от configuration; отсутствие exporter config не следует путать с универсальным data-policy promise.
- **Integration cost:** низкий для нового bounded agent, высокий для custom `BaseAgent` и durable 1.x workflows.
- **Reversibility:** высокая при application-owned state/authz; низкая при использовании experimental graph как единственной domain representation.
- **Production-readiness:** 4/5 для pinned core/LlmAgent; 2.5/5 для experimental workflow graph как canonical engine.

**Validation plan — 60–90 минут:** pin package/lockfile; compile custom subclasses; проверить interruption/resume с positive/negative `rerunOnResume`; два параллельных confirmation requests; malicious OpenAPI path params; contentless tool-call stream; OTel no-egress и synthetic-secret tests.

**Красные флаги:** floating `main`, experimental graph объявлен stable engine, implicit resume semantics, broad code-execution tools с inherited credentials, dev UI в production.

Репозиторий: https://github.com/google/adk-js

### Watchlist

- [`github/gh-aw`](https://github.com/github/gh-aw) — безопасное разделение model reasoning и write executor.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — agent/workload identity.
- [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) — checkpoint/replay/authorization binding.

### Topic для разведки

**Checkpoint/resume semantics + authorization binding:** восстановление causal state и привязка approval/credential response к конкретному invocation должны тестироваться как разные контракты.

## 2026-08-23

### Вывод дня

Порог выпуска прошли три сигнала: новый roadmap MCP с progressive discovery и agent identity, превращение Cursor Cloud Agents в event-driven workers и запуск Cursor Origin как отдельного git forge. Общая тема — рост независимых control planes вокруг agent runtime, source control и workload identity.

### 1. MCP roadmap связал progressive tool discovery и agent/workload identity

22 августа Core Maintainers MCP опубликовали обновлённый roadmap. Среди приоритетов — agentic messaging, унификация HTTP transport, agent identity/security, улучшение primitives и SDK DX. Roadmap отдельно признаёт стоимость больших tool catalogs и предлагает progressive discovery: небольшой начальный capability surface и загрузка полных tool definitions только по мере уточнения задачи. Для agent identity обсуждаются DPoP, Workload Identity Federation, ID-JAG и RFC 8693 token exchange.

**Практическое применение:** уже сейчас разделить три решения: capability обнаружена, actor аутентифицирован, действие авторизовано. Для крупных MCP-каталогов измерять tool-schema context и selection quality до разработки собственного discovery layer.

**Риск и ограничения:** roadmap не является выпущенным wire contract. Преждевременная реализация будущих полей и token flows создаст proprietary semantics и последующую миграцию.

**Сильный контраргумент:** современные клиенты уже могут группировать tools, кешировать каталоги и включать их по сценарию; protocol-level discovery может не дать достаточной дополнительной ценности.

**Кому полезно:** MCP client/server builders, agent platforms, governance и продукты с десятками или сотнями tools.

Источники: [The New MCP Roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/), [MCP roadmap](https://modelcontextprotocol.io/development/roadmap), [current MCP specification](https://modelcontextprotocol.io/specification/2026-07-28).

### 2. Cursor Cloud Agents получили subscriptions и долгоживущие goals

19 августа Cursor добавил subscriptions: Cloud Agent может следить за PR, Slack thread или timer и возобновлять работу после события. Созданный агентом PR автоматически становится источником последующих CI/review events. Появились custom modes, `/goal`, более плавное steering и subagents в отдельных виртуальных машинах.

**Практическое применение:** bounded workflow «доведи PR до green, но не merge», длительные migration/test lanes и автоматическая реакция на bot feedback без повторной загрузки контекста человеком.

**Риск и ограничения:** долгоживущий agent с repo write, network, MCP и credentials является service identity с расширенной временной поверхностью атаки. Conversation/session state нельзя делать единственным workflow ledger.

**Сильный контраргумент:** GitHub Actions + queue worker + one-shot coding agent дают более детерминированный и vendor-neutral lifecycle. Subscriptions оправданы только если сохранение conversation context действительно снижает cycle time.

**Кому полезно:** platform/dev teams, CI remediation, migrations и autonomous QA.

Источник: [Cursor — Cloud Agents and Cursor Harness Improvements](https://cursor.com/changelog/08-19-26).

### 3. Cursor Origin стал отдельной source-control платформой

17 августа Cursor начал rollout Origin Code Hosting в early beta для платных планов. Платформа включает repositories, pull requests, code browsing/search и GitHub synchronization. Для синхронизированных repositories GitHub остаётся source of truth; pushes идут обратно в GitHub, а PR-комментарии синхронизируются двусторонне. Native Origin repositories, напротив, делают Cursor отдельным git authority.

**Практическое применение:** mirror-only pilot может сократить путь `cloud agent → code → PR`, сохранив GitHub каноническим remote.

**Риск и ограничения:** early beta, дополнительная копия исходников, новый permissions/data-processing boundary и высокий vendor lock-in при переходе от mirror к native Origin repository.

**Сильный контраргумент:** GitHub-centric команде Origin может не дать достаточного incremental value. Cursor review и agents способны работать без переноса canonical source control.

**Кому полезно:** команды, где Cursor уже является основным cloud-agent environment.

Источник: [Cursor — Origin Code Hosting](https://cursor.com/changelog/origin-code-hosting).

## GitHub Radar

### Репозиторий периода: `modelcontextprotocol/modelcontextprotocol`

- **Лицензия:** repository находится в переходе к Apache-2.0 для новых code/spec contributions; часть документации и исторических материалов имеет отдельные условия. Лицензию нужно проверять по конкретному файлу/каталогу.
- **Зрелость:** normative revision `2026-07-28`; roadmap от 22 августа описывает будущие направления, а не готовые protocol methods.
- **CI/tests:** schema generation/validation, documentation checks и SEP/release workflows; runtime correctness проверяется в отдельных SDK repositories и conformance suites.
- **Security model:** stdio transport не является sandbox; authorization, consent, reduced privileges и tool-side idempotency остаются обязанностью integration layer.
- **Telemetry/data handling:** протокол сам не задаёт универсальную telemetry/retention policy; это свойство конкретного client/server/host.
- **Integration cost:** умеренный для pinned current revision; неопределённый для future progressive-discovery/agent-identity proposals.
- **Reversibility:** высокая при adapter/capability negotiation, низкая при хранении domain state в ещё не утверждённых constructs.
- **Production-readiness:** 4/5 для `2026-07-28` с official SDK и внешним authz; 2/5 для roadmap-only features.

**Validation plan — 60–90 минут:** pin current revision; проверить stateless reconnect и `server/discover`; прогнать auth negative fixtures; измерить tool-schema tokens для полного и локально отфильтрованного каталога; подтвердить, что discovery result не предоставляет permission.

**Красные флаги:** roadmap используется как spec, `main` вместо revision, stdio принимается за sandbox, discovery смешивается с authorization, long-lived pasted keys для agent identity.

Репозиторий: https://github.com/modelcontextprotocol/modelcontextprotocol

### Watchlist

- [`ards-project/ard-spec`](https://github.com/ards-project/ard-spec) — federated discovery proposal для MCP/A2A/skills/API; пока proposal, не production standard.
- [`openai/codex`](https://github.com/openai/codex) — task/session lifecycle и authority provenance.
- [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) — persistence/replay/MCP lifecycle semantics.

### Topic для разведки

**Capability discovery + workload identity как независимые от authorization слои:** tool найден, actor аутентифицирован и действие разрешено — три разных доказательства.

## 2026-08-22

### Вывод дня

Порог выпуска прошли три сигнала: исправление реального двойного биллинга и нескольких lifecycle/security boundaries в Claude Code, scoped-retirement моделей Codex по типу авторизации и выход GitHub Spec Kit 1.0 с нетипичным контрактом стабильности. Отдельного модельного или дизайн-релиза сопоставимого практического веса не найдено.

### 1. Claude Code 2.1.239 исправил двойной биллинг через Bedrock proxy и несколько ошибок состояния

21 августа Anthropic выпустила Claude Code `2.1.239`. При работе с Amazon Bedrock через proxy, удалявший `Content-Type`, клиент мог повторять streaming-запрос в non-streaming режиме и тем самым создавать второй оплачиваемый API-вызов. Релиз также обновил cost accounting для US-only inference и исправил несколько lifecycle-проблем: повтор действий после queued prompt + Esc, потерю plan mode после idle restart, permanently failed remote MCP после временного `5xx`, случайное подтверждение permission prompt фокус-кликом и попадание password-style input в history/yank.

**Практическое применение:** для Bedrock за корпоративным proxy провести canary и сравнить billed requests до/после; для cloud sessions добавить fixtures на restart/reconnect/cancel; для data-residency workloads пересчитать budget gates.

**Риск и ограничения:** release notes подтверждают исправленный класс ошибки, но не доказывают корректность конкретного AWS-счёта или отсутствие сходных races в других переходах состояния.

**Сильный контраргумент:** командам без Bedrock proxy, US-only residency и cloud sessions не нужен экстренный fleet-wide upgrade; рациональнее capability-specific minimum version.

**Кому полезно:** platform engineering, FinOps, AppSec и команды с remote/cloud coding sessions.

Источник: [Claude Code 2.1.239](https://github.com/anthropics/claude-code/releases/tag/v2.1.239).

### 2. GPT-5.4 и GPT-5.4 mini уходят только из ChatGPT-auth Codex

OpenAI уточнила, что 31 августа 2026 года GPT-5.4 и GPT-5.4 mini перестанут быть доступны в Codex при входе через ChatGPT account. Рекомендуемые замены — GPT-5.6 Terra и GPT-5.6 Luna. OpenAI API и Codex с собственным API key это изменение не затрагивает.

**Практическое применение:** model registry должен учитывать не только model ID, но и `runtime + auth mode + provider lane`. Workspace defaults, saved settings и automations для ChatGPT-auth Codex необходимо мигрировать отдельно от API/BYOK workloads.

**Риск и ограничения:** глобальное удаление GPT-5.4* из общего каталога сломает API-use cases, которые продолжают поддерживаться.

**Сильный контраргумент:** если инфраструктура использует исключительно API key, немедленная миграция не нужна; достаточно scoped warning и отдельного lifecycle metadata.

**Кому полезно:** Codex administrators, model routers, FinOps и платформы с несколькими auth lanes.

Источники: [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan), [ChatGPT rate card](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu).

### 3. GitHub Spec Kit 1.0 не обещает классическую SemVer-стабильность

21 августа GitHub выпустил `spec-kit v1.0.0`, а вскоре — `v1.0.1`. Команда прямо объяснила, что `1.0` не следует интерпретировать как замороженную форму или отсутствие будущих breaking changes. `1.0.1` добавил материалы по brownfield adoption и исправил несколько workflow/manifest defects.

**Практическое применение:** Spec Kit можно тестировать как pinned specification-driven workflow для bounded feature work, но generated constitution/spec/plan/tasks не должны автоматически становиться вторым источником истины рядом с существующим roadmap и governance layer.

**Риск и ограничения:** высокая скорость изменений, community catalogs и executable workflows создают supply-chain и precedence surface. Номер `1.0` здесь не отменяет необходимости pinning и regression fixtures.

**Сильный контраргумент:** agent-assisted migration действительно снижает цену breaking change. Но способность агента адаптировать файлы не равна воспроизводимому governance contract.

**Кому полезно:** DevEx, engineering leads и команды со specification-driven development.

Источники: [Spec Kit v1.0.0](https://github.com/github/spec-kit/releases/tag/v1.0.0), [Spec Kit v1.0.1](https://github.com/github/spec-kit/releases/tag/v1.0.1), [integration reference](https://github.github.com/spec-kit/reference/integrations.html).

## GitHub Radar

### Репозиторий периода: `github/spec-kit`

- **Лицензия:** MIT.
- **Зрелость:** активный официальный проект GitHub; `v1.0.1` является первым исправляющим релизом после major, а `main` продолжает двигаться дальше.
- **CI/tests:** pytest/workflow validation и автоматизация релизов; этого недостаточно, чтобы считать generated governance artifacts безопасными без project-specific fixtures.
- **Security surface:** integrations, extensions, presets, catalogs и scripts/hooks; core не является sandbox или authorization layer.
- **Integration cost:** низкий для disposable/new project, средний для brownfield, высокий при наличии собственного canonical spec/task/governance layer.
- **Reversibility:** высокая, пока Spec Kit — removable producer; низкая, если его artifacts становятся единственной project memory.
- **Production-readiness:** 3/5 для pinned bounded workflow; 2/5 для parallel agents и unreviewed community catalogs.

**Validation plan — 60–90 минут:** pin `v1.0.1`; пройти один brownfield cycle; проверить полный diff generated artifacts; повторить `converge`; смоделировать два параллельных feature-init; удалить инструмент и подтвердить, что проект остаётся понятным без его runtime state.

**Красные флаги:** floating `main`, классическое ожидание SemVer stability, community catalog без review, competing source of truth, generated output как authorization evidence.

Репозиторий: https://github.com/github/spec-kit

### Watchlist

- [`github/gh-aw`](https://github.com/github/gh-aw) — separation model reasoning и permissioned write execution.
- [`anthropics/claude-code`](https://github.com/anthropics/claude-code) — быстрые изменения trust/state/cost boundaries.
- [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) — persistence, replay и guardrail semantics.

### Topic для разведки

**Supply-chain provenance для agent workflow packs, catalogs и executable helpers:** один canonical governance layer, pinning, capability diff и обратимый импорт важнее числа поддерживаемых integrations.

## 2026-08-21

### Вывод дня

Порог выпуска прошли три сигнала. Отдельного свежего frontier-model, design-tool или marketing-AI релиза, который в проверенных первоисточниках менял бы архитектуру, безопасность, стоимость или workflow сильнее них, не найдено. Общая тема дня — причинное состояние долгоживущих agent sessions: permissions должны переживать resume/fork без дрейфа, чувствительные tool outputs не должны возвращаться в replay/persistence, а динамические credential helpers следует считать исполняемым privileged code, а не обычной строкой конфигурации.

### 1. Codex 0.149.0 сделал локальные/удалённые agent tasks first-class и исправил permission drift при resume/fork

20 августа OpenAI выпустила Codex `0.149.0`. В релизе появились интерактивный `codex agents` dashboard для поиска, запуска, открытия, переименования и остановки tasks; `codex queue` для отправки сообщений существующим локальным или remote sessions; расширенный `codex doctor`. Одновременно исправлено поведение resumed/forked threads: теперь они восстанавливают активный permission profile вместо тихого fallback к текущим defaults. Queued messages также надёжно будят idle sessions. Релиз включает заметный security-hardening cluster вокруг environment policies, child-process auth, MCP OAuth/header isolation, project trust, sandbox capabilities, PowerShell command lowering, marketplace identity и protected paths.

**Практическое применение:** permission profile нужно хранить как причинное свойство session/thread, а не вычислять заново из «текущей конфигурации» при resume/fork. Если `codex agents`/`queue` используются из внешнего control plane, их task/session IDs следует считать executor-owned state и связывать с собственным receipt, но не делать каноническим orchestration ledger. Для upgrade нужен black-box fixture: старт под restrictive profile A → изменить default на B → resume/fork → убедиться, что effective profile остаётся A без явного override.

**Риск и ограничения:** native task/queue surface быстро развивается и увеличивает vendor-specific state, который может стать параллельным источником истины. Новый dashboard не превращает permission UI в authorization; broad credentials, network и writable roots по-прежнему задают реальный blast radius. Main уже продолжил меняться после релиза, поэтому floating branch неприемлема как production contract.

**Сильный контраргумент:** если команда не использует resume/fork, native agents dashboard и queue, обязательный переход на `0.149.0` может быть ненужным churn. Верно: разумнее capability-specific floor и contract fixture, а не глобальное требование последней версии.

**Кому полезно:** platform engineering, coding-agent fleets, AppSec и multi-agent orchestration.

Источники: [Codex 0.149.0](https://github.com/openai/codex/releases/tag/rust-v0.149.0), [Codex repository](https://github.com/openai/codex).

### 2. OpenAI Agents SDK 0.22.0 ужесточил границу replay/persistence для заблокированных tool outputs

19 августа опубликован `openai-agents-python v0.22.0`. Релиз редактирует terminal function-tool output, отклонённый output guardrail, из replayable и persisted SDK state; non-streaming Responses с terminal status `failed` или `incomplete` теперь завершаются `ModelBehaviorError`; usage accounting изолируется между независимыми `RunState` checkpoints при сохранении nested-agent aggregation; tracing уважает model-data logging redaction. Кроме того, конфигурация `OpenAIProvider` с explicit `openai_client` больше не принимает конфликтующие `organization`/`project` параметры как молчаливо игнорируемые.

**Практическое применение:** для stateful/HITL agents добавить regression chain `tool output → output guardrail reject → persist/replay` и требовать отсутствия sensitive payload в persisted SDK state, сохраняя отдельно структурные audit facts: tool identity, policy result, digest/hash, timestamp и side-effect status. Отдельно проверить `failed`/`incomplete` response как fail-closed exception path и отсутствие cross-checkpoint usage contamination.

**Риск и ограничения:** redaction SDK-owned state не очищает application logs, custom trace processors, tool-side storage и уже совершённые side effects. Новые exceptions могут сломать код, который раньше трактовал `failed`/`incomplete` как обычный возвращённый объект. Удаление payload также уменьшает forensic detail, если приложение не сохраняет безопасные структурные evidence.

**Сильный контраргумент:** application-owned state machine и собственный append-only ledger дают более переносимую и контролируемую модель, чем SDK semantics. Это сильный аргумент; SDK hardening следует использовать как дополнительную boundary, а не как замену собственной авторизации и аудита.

**Кому полезно:** Python agent platforms, systems с approvals/checkpoints, privacy-sensitive agents и команды с persistent/replayable state.

Источник: [OpenAI Agents SDK v0.22.0](https://github.com/openai/openai-agents-python/releases/tag/v0.22.0).

### 3. Claude Code 2.1.238 добавил dynamic credential helpers для plugin marketplaces и MCP

20 августа Anthropic выпустила Claude Code `2.1.238`. Plugin marketplaces получили `headersHelper`: команда может выпускать HTTP headers, например short-lived token, для catalog и same-origin archive fetches. Catalog helper запускается только при install/update после показа команды; CLI спрашивает `[y/N]`, если не передан `-y`. Self-hosted runner получил отдельные `--proxy-authorization-command`/`--proxy-authorization-file` для свежего `Proxy-Authorization` на каждое соединение. Одновременно project `.mcp.json`/agent-file helpers стали требовать принятого folder trust, а helpers из project/plugin/agent scopes запускаются без inherited credential environment variables. Remote Control session, запускаемая через `claude remote-control`, больше не наследует session-scoped env vars launcher shell.

**Практическое применение:** `headersHelper` и proxy authorization command нужно моделировать как **исполняемый credential source**. Политика должна фиксировать source scope, command hash/provenance, host scope и факт trust; repo-controlled helper лучше запрещать по умолчанию, а managed helper использовать только там, где short-lived tokens реально уменьшают secret exposure. В receipts нельзя сохранять выпущенный header/token — только source, hash, target origin, exit status и TTL/issuer metadata, если они доступны безопасно.

**Риск и ограничения:** helper является командой, выполняемой во время install/update; компрометация plugin/project source превращается в supply-chain execution path. `-y` убирает интерактивный install prompt. Same-origin ограничение защищает destination scope, но не доказывает честность самой helper command; proxy-auth helper добавляет ещё один privileged executable path.

**Сильный контраргумент:** static managed headers или внешний OIDC/workload broker проще аудировать и переносить между clients. Dynamic helper оправдан не как default, а только для rotating/short-lived credentials, где снижение времени жизни секрета перевешивает дополнительную execution surface.

**Кому полезно:** enterprise plugin marketplaces, MCP fleets, self-hosted Claude runners, proxy-auth environments и agent-governance tooling.

Источник: [Claude Code 2.1.238](https://github.com/anthropics/claude-code/releases/tag/v2.1.238).

## GitHub Radar

### Репозиторий периода: `openai/codex`

**Текущий статус и release cadence:** официальный Apache-2.0 coding-agent repository. Stable `0.149.0` опубликован 20 августа; уже 21 августа `main` содержит новые изменения, поэтому production следует pin-ить на reviewed tag и отдельно держать canary against main/next только для compatibility intelligence.

**Документация и install surface:** README предоставляет standalone installer для Unix/Windows, npm package `@openai/codex`, Homebrew и direct release binaries. Surface шире core CLI: app-server, MCP, plugins/apps, SDK и remote/local session features, поэтому минимальная production установка должна включать только требуемые capabilities.

**CI/tests:** repository имеет blocking CI, Bazel, Rust/SDK checks, `cargo-deny`, post-merge и другие специализированные workflows. Это сильный maintenance signal, но не заменяет application-level fixtures для permission, sandbox и конкретной OS.

**Issue activity:** tracker очень активен, а после tagged release `main` продолжает быстро двигаться. Свежие reports следует использовать как canary discovery, а не как подтверждённые current defects без воспроизведения на точной версии и ОС.

**Security model:** официальный `SECURITY.md` направляет vulnerability disclosure через Bugcrowd; deterministic boundary остаётся sandbox + permissions + protected paths/network/credentials. Нативные reviewer/permission surfaces не заменяют server-side authorization, protected remotes или disposable runner.

**Telemetry/data handling:** Codex имеет OpenTelemetry integration для logs/traces/metrics и поддерживает session-level business events; конфигурация может включать account/session metadata и, при явном включении, user prompts. Telemetry следует считать отдельным outbound data surface: проверить effective exporter configuration, `log_user_prompts`, custom span attributes и отсутствие model/source/secrets payload, если они не требуются.

**Integration cost:** низкий для pinned CLI adapter и bounded `codex exec`; средний для session lifecycle, `agents`/`queue`, MCP/plugins и receipt mapping; высокий, если native task/session state становится canonical orchestration authority.

**Reversibility:** высокая при собственных project policy/receipts и тонком adapter; ниже при проникновении native session/task IDs, plugin schemas и app-server state в domain model.

**Известные ограничения:** очень быстрый cadence; сложные platform-specific permission/sandbox semantics; native queue/tasks vendor-specific; telemetry и local session state требуют отдельного retention/privacy review; issue reports надо воспроизводить на точной версии/OS.

**Production-readiness — собственная оценка:** **4/5** для pinned `0.149.0` в bounded interactive/CI workflows с внешними git/policy controls; **3/5** для unattended native `agents`/`queue` orchestration до собственного contract canary; **2/5** если Codex session/task state становится единственным governance/audit source.

**Validation plan — 90 минут:** pin `0.149.0` в disposable repo; запустить bounded task через `codex agents`; отправить message через `codex queue` в idle session; создать restrictive permission profile A, затем изменить default B и проверить resume/fork; прогнать denied outside-root/network fixture и synthetic-secret fixture; выполнить `codex doctor`; проверить local state и telemetry на fixture secret; отключить task/queue/MCP/plugin capabilities и убедиться, что базовый adapter/`codex exec` остаётся работоспособным.

**Красные флаги:** floating `main`; permission UI трактуется как authorization; native queue/task store становится canonical state; broad unsandboxed network/writes; telemetry включается без review; нет black-box fixture на текущей OS/version; security inference делается из issue report без воспроизведения.

Репозиторий: https://github.com/openai/codex

### Watchlist

- [`anthropics/claude-code`](https://github.com/anthropics/claude-code) — dynamic credential helpers, marketplace/MCP trust и self-hosted runner boundaries.
- [`openai/openai-agents-python`](https://github.com/openai/openai-agents-python) — replay/persistence redaction, checkpoint semantics и provider-runtime hardening.
- [`modelcontextprotocol/modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) — следить за cross-client conformance текущей спецификации и extensions, а не только за заявленной поддержкой revision date.

### Topic для разведки

**Permission provenance + executable credential sources:** long-lived agent session должен доказуемо сохранять effective permission state через resume/fork, а любой helper, который mint-ит credentials или headers, должен иметь origin, trust decision, command provenance, target scope и no-secret receipt.
