---
name: programmatic-adtech
version: 1.1.0
author: hermes
license: MIT
description: Use when researching or building SSP/DSP/RTB ad-tech.
metadata:
  hermes:
    tags: [adtech, ssp, dsp, rtb, vast, github-audit]
    related_skills: [github]
---

# Programmatic ad-tech research & platform building

## When to Use

Use for programmatic ad-tech tasks: explaining or building SSP/DSP/Ad Exchange, OpenRTB, VAST/VPAID video ads, or auditing open-source ad-tech projects on GitHub.

Context: Leonid is planning his own SSP + Ad Exchange (Go-only stack). Colleagues referenced Bidster/Stack (stack.bidster.net) as the demo platform and 'start with VAST/VPAID like AdFox' as the MVP scope.

## lowbid-ssp project (own SSP, in progress)

- Repo `dlgrv/lowbid-ssp` (private, `main`), local `~/aezly/lowbid-ssp` (sibling of `~/aezly/krutilka`). New lowbid repos go under the `dlgrv` account — `sfsef` is a personal account, not an org, so cross-account wiring is limited.
- Approved MVP decisions: no PBS, no auction in MVP — direct campaigns + VAST tag serving first; 3 binaries (`gateway`, `consumer`, `adminctl`); Kafka (franz-go) between gateway and consumer; Postgres for money/state, ClickHouse for events (monthly partitions, TTL 90d, dedup by `bid_id`+event); React+Vite+TS frontend embedded in the Go binary via `go:embed`. prebid/openrtb is a Go library, not a service — protocol types only; PBS enters at phase 2 as a demand source + public `/openrtb2/auction`.
- Auth decision: `gorilla/sessions` + bcrypt hashes in Postgres for MVP; GitHub OAuth (`golang.org/x/oauth2`) as a phase-2 feature flag on top of sessions. Do NOT pull Ory Kratos/Hydra or PocketBase — separate services are overkill for a handful of internal users.
- UI: dark minimal admin modeled on Stack by Bidster; design tokens + extracted CSS bundles live in `docs/design-reference/` (DESIGN.md = token/component/section spec). Frontend stack: shadcn/ui + Tailwind v4, lucide-react icons (never hand-draw), TanStack Table, Recharts, RHF+zod; shadcn-admin as scaffold. Sections MVP: Статистика, Кампании, Зоны, Настройки.
- Code standard: `docs/CODE-STANDARD.md` is binding for every coding task — golangci-lint v2 (depguard layer rules, gocognit ≤15, funlen, sloglint, nolintlint), gofumpt+goimports, DI via constructors, domain layer imports no infra (no sql/http/kafka/redis), wrap errors `%w` + sentinel errors, context first arg, table tests + golden VAST files, `go test -race` in CI. Enforce from the first commit — a linter contour added after code exists produces a red wall nobody wants to fix.
- Docs on disk: `docs/plan-mvp.md` (~700 lines, reviewer-APPROVED), `docs/plan-final.md` (final plan; where it consciously diverges from plan-mvp it carries an explicit 'supersedes plan-mvp §…' note — without such a note plan-mvp wins), `docs/integration-krutilka.md`, `docs/CODE-STANDARD.md`, `docs/design-reference/`. Git conventions + commit gate: `lowbid-git-workflow` skill. Working mode: everything stays local until the user explicitly asks for a commit/push (applies to subagent cycles too — put the no-commit rule in every delegated task's context).
- Week-1 infrastructure is DONE and review-PASSED: compose stack (PG16/Redis/Redpanda/CH24/Prometheus/Grafana/Caddy, base+override, healthchecks), Go skeleton `cmd/{gateway,consumer,adminctl}` + `internal/{domain,app,infra,config,httpx,store}`, migrations 0001 + CH DDL, consumer pipeline (franz-go interfaces, batch 5000/1s, commit strictly after insert), `.golangci.yml` v2, CI, Makefile. Latent fixes already applied (PG_DSN interpolation, graceful-shutdown drain on `context.WithoutCancel`+timeout, consumer restart-redelivery test). Track review findings that are real but non-blocking in a cleanup backlog and burn it down in a later fix round — don't silently drop them.
- Testing requirement (user-set, binding): EVERY layer tested — Go unit (table + golden), integration via testcontainers-go, contract tests vs the krutilka emulator, API httptest, UI component tests (Vitest+Testing Library), Playwright UX use-case scenarios (login fail/success, campaign lifecycle incl. exhausted badge, targeting persist, VAST-tag copy+XML validity, stats CSV + empty-state, nav deep-links, keyboard a11y), k6 load + kill-a-dependency chaos. Add tests to the task's acceptance criteria at dispatch time — a task without test criteria ships untested.
- Review-loop status discipline: when a reviewer/fixer subagent is interrupted by infra (timeout, batch loss), check the repo state FIRST (`git status`, file mtimes) before re-dispatching — interrupted agents often saved their edits before dying, and a blind re-run double-applies fixes or re-reviews stale state.
- Delivery loop that works: plan → delegate a read-only reviewer (GO/NO-GO verdict + blockers) → delegate one fixer applying the full findings list → verify findings programmatically → convert plan to a task list → delegate week-sized implementation batches to subagents (each gets: repo path, doc list, CODE-STANDARD as binding, verification criterion `go build ./... && go vet ./...`, explicit no-commit rule). Run reviewers and fixers as separate agents — a reviewer that also edits loses its read-only skepticism.

## Domain primer (always-on)

- SSP = sell side (publisher traffic in, auction out); DSP = buy side (campaigns in, bids out); Ad Exchange = the RTB auction between them. One product often plays several roles — classify by which side the user enters, not by marketing labels.
- VAST/VPAID are delivery protocols (XML video-ad markup player←exchange), not platforms. 'Start with VAST' = flat-CPM tag serving, no real-time auction — the standard MVP before RTB.
- Revenue model: revshare with publishers (SSP keeps ~10-20%), markup on demand, and traffic arbitrage (buy flat low, sell RTB high) — the last is what small SSPs actually live on.
- Two-sided network: demand must exist before publishers will stay. MVP order = tag serving + direct campaigns first, auction engine second.

## Auditing open-source ad-tech on GitHub (procedure)

1. Enumerate candidates: `web_search` for the domain + 'github', then GitHub search API:
   `curl -s 'https://api.github.com/search/repositories?q=<terms>+language:go&sort=stars&per_page=15'`
2. Parse API output with **jq, never `json.loads`** — GitHub API responses contain raw control characters in descriptions that break strict parsing even with `strict=False`.
3. For each candidate fetch `/repos/{owner}/{repo}` and record: stars, forks, language, `license.spdx_id`, `pushed_at`, `archived`. Pushed >2 years ago = dead; read as reference only, never build on it.
4. License gate BEFORE recommending: AGPL/GPL forces opening your modifications when run as a service; licenses that say 'personal/internal use only' (e.g. sspserver) are unusable for commercial work; `spdx_id: NOASSERTION` means read the LICENSE file manually before trusting it.
5. Verify org-wide too (`/orgs/{org}/repos`) — the flagship repo often has sibling UI/campaign-manager repos that complete the picture.
6. Star counts < 15 mean zero production users: treat as unproven regardless of feature list; check that 'planned' integrations are not just empty interfaces.
7. When two sources disagree on a library choice, decide by repo ACTIVITY (commit cadence, open-issue backlog age), not star count — segmentio/kafka-go has more stars but a half-year-dead cadence and a 266-issue backlog; franz-go commits daily. Record the divergence as an explicit 'supersedes' note in the doc that wins, or implementers will pull different libs from different docs.

## Key landscape finding

There is NO mature open-source 'SSP under key' — the market is closed because the margin IS the product. The viable Go assembly is: own thin layer (admin, publisher cabinet, VAST endpoint, billing) + Prebid Server (Go, Apache-2.0) as the auction core + prebid/openrtb for protocol types. Details and per-project verdicts: references/go-oss-landscape.md

## Anti-fraud evasion testing (traffic generators)

When the task is making a test traffic generator (bid + VAST playback) indistinguishable from real users:

- Split the traffic into TWO planes and never mix them: **S2S plane** (bid request, nurl/win notice) legitimately goes server-direct — TCP-source ≠ device.ip is market norm, proxied bids are wasted money AND wrong. **User plane** (impression pixels, tracking, VAST wrappers, media) must be consistent: request IP = device.ip, request UA = device.ua, Accept-Language = geo of exit IP.
- Ad-fraud detection is CROSS-LAYER consistency (IP↔ASN↔geo↔language↔UA↔TLS↔behavior) plus behavioral distributions (completion rate, frequency, daypart), not single fields. Audit a generator by checking pairwise consistency of planes, not field quality.
- Kill one-shot identity: new user.id/ifa every attempt with a shared IP pool is a textbook bot pattern. Give each profile (device+ifa+user.id+sticky IP) a lifecycle of hours with long-tail frequency; this also cuts residential-proxy cost (fewer unique IPs per volume).
- Residential proxy economics: media is 99%+ of bytes. Save via lowest rendition choice, range requests with player-like buffer curve and early stop (players rarely fetch the full file), and 15-30% abandon profiles (simultaneously fixes suspicious 100% completion rate). Never proxy the S2S plane.
- Perfect zeros are signals: CTR=0, error-rate=0, jitter=0, flat 24/7 traffic. Real traffic has realistic zeros AND realistic non-zeros.
- Anti-boundary margins must scale with duration: a fixed ±1s 'never abandon near an event' margin makes abandon impossible on creatives < ~8s (quartile interval ≈ dur/4 < 2.1s window), silently collapsing completion to 100% exactly on short creatives. Use max(0.3, min(1.05, dur*0.05))-style scaled margins and test short creatives explicitly.
- Changing a saved config field's unit/semantics (e.g. jitter: absolute seconds → duration fraction) silently breaks stored campaign overrides: gate with a threshold heuristic, version via a new field, or migrate — and add a test documenting the override-merge semantics ({**defaults, **stored} gives partially-overridden campaigns the new defaults) as conscious.
- Subagent fan-out pattern that worked: one agent inventories the generator's emitted signals from code (each signal: file:line, value source, static/random), another compiles detection signals from public sources only (MRC IVT/SIVT, OpenRTB, VAST, vendor blogs), then synthesize the gap matrix. Verbatim-verify load-bearing findings (file:line) in the main thread before reporting.

### Spec-compliance gate (run BEFORE implementing)

- Validate any improvement plan against OpenRTB 2.6 + VAST 4.3 before coding — plausible fixes can silently violate specs. Delegated check, citations to spec sections required, verdict per task: compliant / partial / violation.
- VAST error codes (§2.3.6.3): 201/203 are TRAFFICKING mismatches (wrong linearity/size), not fetch failures. Wrapper-fetch failure → 300 (general) / 301 (VAST URI timeout) / 303 (no response after wrappers); media failure → 401 (not found) / 402 (timeout); 405 only for 'fetched but cannot render'. Fire the Error URI of EVERY Wrapper level where present plus InLine, one call per level, [ERRORCODE] percent-encoded (RFC 3986). Put the wrapper into the level list BEFORE fetching its URI so its own Error fires on its failure.
- Retry tracking pixels only on network-level failures (asyncio.TimeoutError / aiohttp.ClientConnectionError, detected via exc.__cause__), max 1 retry, never on HTTP responses — retrying a delivered pixel is double counting (§3.14.2); keep the cause chain ('raise ... from exc') or cause-based detection silently breaks.
- ORTB device enums come from AdCOM 1.0, not the 2.6 doc: devicetype 1–8 (7=STB, 8=OOH — CTV matters), connectiontype 1–7. device.language = ISO-639-1-alpha-2 only ('pt', never 'pt-BR'); country variants go to langb/BCP-47, mutually exclusive with language.
- Never send test=1 to live exchanges (§3.2.2): non-billable auction, DSPs may not respond or respond non-competitively — defeats realistic testing. test=1 only against own mock SSP.
- Do not synthesize sua (§3.2.29) for CTV/app-level (Dalvik) traffic: Sec-CH client hints don't exist there — a synthesized sua diverges from what real clients send.
- nurl macros (§4.4): resolve the full common set (PRICE/ID/BID_ID/CURRENCY/IMP_ID/SEAT_ID/AD_ID); AUCTION_PRICE passes through raw with NO reformatting (same currency/units as bid); missing value → empty string (never leave the macro literal); support the `:X` encoding suffix.
- Float prices via str() render scientific notation for micro-prices (str(1e-05) = '1e-05', but the exchange's JSON said '0.00001'): format floats via format(v,'f') + strip trailing zeros/dot, pass strings through untouched.
- Never log the RESOLVED nurl in request-error paths — the substituted clearing price leaks into logs/monitoring; log the raw nurl with literal macros.

### Executing the plan via subagent waves (SDD)

- Use `subagent-driven-development` (in ~/.agents/skills) as the controller skeleton: implementer per task → task-review after each → final whole-branch review + verification-before-completion. Audit step first: for each task check (a) standalone dispatchability, (b) file-overlap conflicts, (c) natural TDD cycle.
- ONE SUBAGENT PER TASK, never per week/milestone: delegating a whole week to one agent silently drops the per-task review gates and the user will catch it. Split the plan so each dispatch = one task with its own verification criterion; after a parallel batch lands, run a cross-task integration sweep (build all + one end-to-end test through the joined parts) before the whole-batch review.
- Two-stage review protocol per task: (1) spec-compliance reviewer — read-only, runs the build/test/lint gates itself, verdict PASS/FAIL with findings as file:line + severity; (2) quality reviewer against the code standard. Fix rounds get ONE fixer agent applying the full findings list with a minimal-diff instruction; defer minor cleanup findings to a tracked backlog instead of inflating the fix round.
- Gate parallelism on FILE overlap, not task independence: tasks touching the same flow file run strictly sequentially in SEMANTIC order, not plan order — e.g. abandon-semantics (abandon fires NO error) must land before error-firing tasks that edit the same exception paths, or the exception-handling changes conflict.
- Narrow each task's scope to existing infrastructure: if it depends on a component from a deferred task (e.g. media fetcher → media error codes), keep only the implementable part and mark the rest TODO — never let an implementer stub half a subsystem.
- To run tasks in PARALLEL that share components, define the seam as an interface and paste its exact signature into EVERY related agent's context (each programs against the interface, fakes in tests); otherwise agents invent incompatible stubs and the merge conflicts. E.g. parallel decision-module and VAST-endpoint tasks both get 'program against `Selector.Select(ctx, req)`; the real implementation is another agent's job — use a fake in tests'.
- Stochastic/behavioral tasks need seed-fixation and range asserts over N runs (e.g. completion 60–85% over 200 runs), never exact values; use tdd-red-phase-pitfalls for distribution-assert pitfalls.
- Parallel implementers must NOT share one repo checkout even on disjoint branches — concurrent branch surgery in one worktree corrupted branch topology. Sequence file-overlapping tasks (rule above) AND give genuinely parallel tasks separate `git worktree`s; prefer a linear stacked-branch chain (each task branches off the previous task's tip) — it makes the final gate a simple `git log <base>..HEAD` integrity check plus whole-stack review.
- Give reviewers QUANTITATIVE invariants to reconcile, not 'check correctness': 'measured completion 74.9% vs theoretical 75.5% — explain the gap' surfaced a real edge-case bug (margin on short creatives) that generic review language missed. Also ask targeted edge questions (smallest creative, skipoffset=0, retry classification).
- Verify 'configurable via X' claims end-to-end: a pydantic Literal-keyed API model silently drops dict keys it doesn't know, so a defaults key absent from the schema is unreachable no matter what the docstring says.

## Communication style for this user

Explain in plain Russian, step by step, with concrete numbers (latencies, revshare %, timelines). ASCII diagrams of money/data flow work well. Answer the actual question ('what do we build, how does it earn') before any tooling detail.