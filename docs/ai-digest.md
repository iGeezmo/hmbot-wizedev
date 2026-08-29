---
title: "Ежедневный прикладной ИИ-дайджест"
type: doc
created: 2026-08-29
updated: 2026-08-28
managed: true
mirror:
  canonical_repository: "iGeezmo/0dai"
  canonical_path: "docs/ai-digest.md"
---

# Ежедневный прикладной ИИ-дайджест

Публичное зеркало накопительного прикладного ИИ-дайджеста для `hmbot-wizedev`.

Новые выпуски хранятся как отдельные файлы в `docs/ai-digest-entries/` и автоматически собираются в этот документ. Полный исторический архив до начала зеркала остаётся в каноническом приватном документе `iGeezmo/0dai/docs/ai-digest.md`.

<!-- DAILY_ENTRIES -->

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
