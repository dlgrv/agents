---
name: programmatic-adtech
version: 1.1.0
author: Hermes Agent
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
- Week-2 (store/cache/decision/VAST-gate) DONE and PASS after a fix round; the integration sweep found 4 seam defects no implementer saw (see SDD pitfalls below). Week-3 (Redis budgets DECRBY+rollback+exhausted, Kafka producer + bidmap — bidmap closes the `/clk?click=` open redirect, MaxMind + CH inserter) and Week-4 (/rtb endpoint per krutilka contract: gzip/deflate bodies, 204 no-bid, X-Error headers, one bid, adm string, literal nurl, bid.id echo; cmd/consumer prod wiring) both DONE and PASS after fix rounds. Week-5 (Admin API: bcrypt+Redis-sessions+CSRF+rate-limit, CRUD zones/campaigns incl. hard DELETE, stats from CH + CSV, migration 0002_users, api.md contract; frontend/ Vite+shadcn per DESIGN.md tokens, MSW mocks, Vitest; go:embed SPA in the gateway binary — mount the SPA last, Go 1.22 mux `/` catches only unmatched paths so /api,/vast,/rtb,pixels stay intact; Dockerfile multi-stage node:22→go, `make build-frontend`) DONE, all green (16 Go pkgs race+lint 0+integration; frontend lint/tsc/vitest/vite-build). Week-5.5 in flight: Playwright e2e (7 UX scenarios vs the real gateway + embed, no MSW) + two-stage week-5 review. Week-6 remains: VPS deploy + live krutilka integration. Data note: seed campaigns must target the device types real partner traffic arrives as (krutilka = SmartTV, devicetype 3) — a mobile-only seed makes the e2e green while real traffic gets 204. Progress ledger for the whole SDD cycle: `.superpowers/sdd/progress.md` in the repo (per-week status, verdicts, tails) — write it so context compression cannot lose the plan state.
- Frontend verification criterion: vitest green does NOT mean shippable — `tsc -b && vite build` catches a separate class of errors (missing `vite-env.d.ts` for `import.meta.env`, recharts vs lucide name collisions like `Bar`, zod input/output type splits) that component tests skip. Put the PROD BUILD command, not just the test runner, in every frontend task's acceptance criteria and in the reviewer's checklist.
- franz-go gotcha: since ~v1.22 the client defaults to idempotent write, which forces acks=all and silently conflicts with `kgo.RequiredAcks(LeaderAck)`-style contracts — the gateway fails at startup, not at first produce. Fix: `kgo.DisableIdempotentWrite()` when the delivery contract specifies leader-ack.
- Before choosing soft-delete for an entity, read the migration's CHECK constraints first — an enum CHECK without an 'archived'/'deleted' value makes soft-delete a migration, and a hard DELETE with ON DELETE CASCADE may be the honest minimal choice.
- When a subagent reports a file-edit FAILED, read the file at the CORRECT path before dispatching a fixer — the failure is often the agent typo-ing the absolute path (e.g. wrong home dir), while the real file is already in place; a blind fix round churns working code.
- MaxMind license: the paid GeoIP2-City base already exists in the sibling repo (`~/aezly/krutilka/backend/data/maxmind/GeoIP2-City_*/GeoIP2-City.mmdb`, ~128 MB) — reuse it via `MAXMIND_DB_PATH` env + `*.mmdb` in .gitignore, no license key needed (a key is only for auto-updates). Before asking the user for a paid API/credential, check sibling repos in the same product family for an existing copy of the resource.
- Testing requirement (user-set, binding): EVERY layer tested — Go unit (table + golden), integration via testcontainers-go, contract tests vs the krutilka emulator, API httptest, UI component tests (Vitest+Testing Library), Playwright UX use-case scenarios (login fail/success, campaign lifecycle incl. exhausted badge, targeting persist, VAST-tag copy+XML validity, stats CSV + empty-state, nav deep-links, keyboard a11y), k6 load + kill-a-dependency chaos. Add tests to the task's acceptance criteria at dispatch time — a task without test criteria ships untested.
- Review-loop status discipline: when a reviewer/fixer subagent is interrupted by infra (timeout, batch loss), check the repo state FIRST (`git status`, file mtimes) before re-dispatching — interrupted agents often saved their edits before dying, and a blind re-run double-applies fixes or re-reviews stale state. Resume, don't restart: read the interrupted agent's live transcript (`~/.hermes/cache/delegation/live/<delegation-id>/task-N.log`), pass its uncommitted work AND the in-flight problem it was mid-way through (e.g. a race it just found in a Lua script, with its fix idea) into the successor's context, and have the successor finish on top of the existing files. When SEVERAL parallel agents die on model timeout, merge their remaining scopes into ONE sequential successor continuing over the survivors' uncommitted files — re-spawning the same parallel split repeats both the timeout and the shared-worktree contention.
- Literal `{name}`-shaped placeholders in a delegated task's `goal` text are rejected at dispatch as unexpanded template markers — write example keys, file paths and dict access without braces.
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
- Residential proxy economics: media is 99%+ of bytes. Save via lowest rendition choice, range requests with player-like buffer curve and early stop (players rarely fetch the full file), and 15-30% abandon profiles (simultaneously fixes suspicious 100% completion rate). Never proxy the S2S plane. When the user bills proxy traffic per GB, rank every plan task by proxy-byte impact BEFORE ease/effect: zero-byte tasks (headers, nurl macros, device fields, config plumbing) run first, and any realism feature that INCREASES media fetches (deeper site interactions, more page visits) is off by default unless the user re-authorizes the spend.
- Perfect zeros are signals: CTR=0, error-rate=0, jitter=0, flat 24/7 traffic. Real traffic has realistic zeros AND realistic non-zeros.
- Every behavior knob ships as a per-campaign SETTING, never hard-coded: backend default (optimal, usually below 100% — even honest players lose error pixels) + API model field + UI control with a question-mark help tooltip (campaignFieldHelp.ts). The user treats a hard-coded probability as incomplete work, and every default value must be defensible ('why 95, not 100').
- Probabilistic gates (fire_chance etc.) must apply PER-EVENT-LEVEL, never to a whole batch/cascade: a cascade-level gate at 95% randomly drops the ENTIRE cascade ~5% of the time, which both distorts the realistic-error-rate model and flakes deterministic tests. Same principle as abandon margins: simulate the per-pixel/per-level behavior of real players, not a coin-flip over the whole failure.
- Anti-boundary margins must scale with duration: a fixed ±1s 'never abandon near an event' margin makes abandon impossible on creatives < ~8s (quartile interval ≈ dur/4 < 2.1s window), silently collapsing completion to 100% exactly on short creatives. Use max(0.3, min(1.05, dur*0.05))-style scaled margins and test short creatives explicitly.
- Changing a saved config field's unit/semantics (e.g. jitter: absolute seconds → duration fraction) silently breaks stored campaign overrides: gate with a threshold heuristic, version via a new field, or migrate — and add a test documenting the override-merge semantics ({**defaults, **stored} gives partially-overridden campaigns the new defaults) as conscious.
- Subagent fan-out pattern that worked: one agent inventories the generator's emitted signals from code (each signal: file:line, value source, static/random), another compiles detection signals from public sources only (MRC IVT/SIVT, OpenRTB, VAST, vendor blogs), then synthesize the gap matrix. Verbatim-verify load-bearing findings (file:line) in the main thread before reporting.
- Adversarial test wave (when the user wants bug-hunting tests, NOT coverage): dispatch 2 parallel test-writer agents with disjoint domains (e.g. Lua-store chaos + property/fuzz vs playback/builder edge paths); each creates ONLY new test files, never edits product code, reports bugs as file:line + repro + expected-vs-actual, and pins each reproduced bug as strict-xfail with a BUG-id. A single wave reliably finds real bugs (16 in one pass, incl. a critical ordering bug and a probability-gate flake) — offer it after any large feature wave. Then fix in batches by severity (critical → robustness → low), one commit per batch, acceptance = xfail removed and green. Boundary conditions that paid off: quota/cap checks AT the boundary (N-1 vs N), TTL expiring mid-operation, garbage/non-numeric fields in the store, Redis failures mid-operation (SCRIPT FLUSH), duration=0/1s VAST, spec-optional nodes missing (VAST TrackingEvents), spec'd mocks with un-stubbed seam methods.

### Spec-compliance gate (run BEFORE implementing)

Validate any improvement plan against OpenRTB 2.6 + VAST 4.3 before coding — run as a delegated check with spec-section citations, verdict per task: compliant / partial / violation. Full rule set (VAST error codes, pixel-retry rules, device enums, test=1, sua, nurl macros, float formatting, price-in-logs): `references/ortb-vast-compliance.md`.

## Executing the plan via subagent waves (SDD)

Full controller protocol (per-task dispatch, two-stage reviews, file-overlap parallelism rule, stacked branches, seam interfaces, reviewer checklists, integration-sweep defect shapes): `references/sdd-waves.md`. Always-on core:

- ONE SUBAGENT PER TASK with its own verification criterion; implementer → task-review after each → final whole-branch review. Reviewers are read-only and separate from fixers.
- Gate parallelism on FILE overlap, not task independence; prefer a linear stacked-branch chain — parallel implementers must never share one repo checkout, even on 'disjoint' branches.
- Give reviewers QUANTITATIVE invariants to reconcile and audit test ASSERTS, not test existence; a PASS with a money-affecting finding still forces an immediate fix round.

## Communication style for this user

Explain in plain Russian, step by step, with concrete numbers (latencies, revshare %, timelines). ASCII diagrams of money/data flow work well. Answer the actual question ('what do we build, how does it earn') before any tooling detail.