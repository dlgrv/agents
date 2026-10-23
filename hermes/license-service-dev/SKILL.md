---
name: license-service-dev
description: Use when editing the license-service repo (primepilot.tech).
version: 1.0.0
author: hermes-mac
license: private
metadata:
  hermes:
    tags: [frontend, primepilot, fsd]
    related_skills: [macos-proxy-ops, prime-bpm-ops]
---

# license-service (primepilot.tech) frontend work

## When to Use

Any edit in `~/work/license-service` (primepilot.tech site, offers/PDF viewer, cabinet, admin, packages/shared), its local dev servers, or a "primepilot.tech won't load" report.

Monorepo frontend at `~/work/license-service/frontend`: `public/` (сайт primepilot.tech, FSD structure), `cabinet/`, `admin/`, `packages/shared/`. Local dev: `npm run dev` in `public` (port 5174) and in crbsit-site (`~/work/crbsit-site`, port 5173). Prod: primepilot.tech on RU hosting 94.26.229.45.

## Gates before commit

- Run BOTH lints from `frontend/`: `npm run lint` runs eslint over `public/src cabinet/src admin/src packages` with `--max-warnings 0`, then steiger (FSD lint:fsd). Format with `npx prettier --write` first — the string-class ternaries prettier collapses will fail eslint review otherwise.
- Run tests from the `frontend/` ROOT via `npm run test:unit -- <paths>` (or `npx vitest run --project packages`): the jsdom environment lives in `vitest.workspace.ts` at the root. Calling `npx vitest run <file>` inside `cabinet/` or `admin/` skips it — every DOM test dies with `ReferenceError: document is not defined`, which looks like real failures but is pure invocation error (`cabinet/package.json` has no test script either).
- CI pins ruff (0.11.7) — a newer local ruff formats differently. Before pushing to `main`, run the CI's exact checks, not just `ruff check`: `ruff format --check .` and `npx prettier --check` over touched files; keep Cyrillic string literals in tests off the lint radar via the existing per-file-ignore pattern for RUF001/003. CI runs `check`-only (never `--write`) jobs, so pure formatting failures block the pipeline.
- The playwright route-coverage test (`test/playwright/routes.ts` + `route-manifest.ts`) requires a manifest case per canonical cabinet route. When deleting pages that keep their path constants for legacy redirects (`/classic/*`, `/licenses`), compare the manifest against `cabinetCanonicalPaths` (in `cabinet/src/shared/lib/cabinetPaths.ts`), not the full `cabinetPaths` object — the full object contains redirect-only aliases and the equality test fails with a diff that does not name the cause.
- Single-consumer slices (`features/view-pdf`, `features/offer` → only `pages/offer`) are overridden in the steiger config's `insignificant-slice` list — follow that existing override pattern when a new single-consumer slice trips `lint:fsd`, instead of restructuring the slice or letting CI go red.

## Shared working tree — foreign edits everywhere

Parallel Hermes sessions drop uncommitted edits into this repo (cabinet widgets, brand assets). Rules:
- NEVER `git stash -u` here: the stash swallows foreign edits and the pop conflicts mid-foreign-work. Stage only your own paths by explicit path (`git add <paths>`), never `git add -A`.
- If foreign edits block a checkout, commit them to a dated `wip/unsaved-YYYY-MM-DD` branch on their own — never discard, never mix into your feature commit.
- If a stash conflict happened anyway, resolve toward the stashed (newer) side and verify `grep -c '<<<<<<<'` = 0 afterwards.

## Offer links & PDF viewer conventions

- Offer links in shared `LegalLinks` must be host-aware: relative `/offer/<slug>` when hostname is `primepilot.tech`/`localhost`/`127.0.0.1` (viewer lives there), absolute `https://primepilot.tech/offer/...` from cabinet/admin (no local viewer). A hard-coded absolute URL sends localhost clicks to prod — Leonid rejects that.
- The primepilot PDF viewer is a copy of crbsit-site's with primepilot styling: NO card borders or `bg-card` background around pages (transparent gutters, page edge-to-edge). Keep the two implementations visually distinct; don't "sync" styles back to crbsit without asking.
- Legal labels use full product names: «Оферта PRIMEPILOT», «Оферта PRIMEPILOT Configurator».

## Offers are the source of truth (legal alignment)

The two Минцифры offers (PRIMEPILOT, PRIMEPILOT Configurator) govern every license price, billing text and cabinet wording. Before changing any of those, re-check the offer text — the cabinet must never assert more than the offer states (it passes legal review precisely because it asserts almost nothing itself; keep it that way).

- The offer PDFs are scans with no text layer. Extract text by rendering pages (e.g. `docker run --rm -u $(id -u):$(id -g) -v "$PWD:/docs" alpine:3.20 sh -c 'apk add -q poppler-utils && pdftoppm -png -r 150 file.pdf page'`) and dispatching vision-capable subagents to transcribe (~6 pages each); keep transcripts in scratch and the findings in `docs/legal-review-*.md` on the feature branch.
- Payment requisites shown to users come from `PaymentSettings` in `backend/settings.py` (env-overridable `PAYMENT_*`); verify the `/api/v1/payment-details` payload against the official requisites from the offer before any release — placeholder defaults have shipped before.
- Balance-debiting transaction comments must quote the offer's payment purpose verbatim; when editing manager texts, grep the test tree for the old wording and update those assertions in the same change.
- Any new balance-debiting endpoint follows the Redis Idempotency-Key pattern in `backend/app/utils/idempotency.py` (cache successful responses only; same key + different body → 409) — an unprotected renew/top-up double-bills on double-click.
- The edition PUBLISHED on the sites is the governing text, even if the lawyer has newer drafts — Leonid treats published docs as authoritative. Before writing any fix wording, verify the clause verbatim against the published edition (compare file hashes of the site's PDF vs the lawyer's copy; if they differ, render the title page and read the revision date) — clause numbering and phrasing can shift between editions, and a fix written against the wrong edition embeds the drift it was meant to remove.
- Triage divergences in three classes before editing: (1) verbatim fix — anything the user copies into a real-world action: bank payment purpose (п. 6.6 + keep the request id for matching), support emails shown to clients (п. 5.3 channel), requisites; (2) deliberate divergence, do NOT "fix": site prices shown as «по запросу» (the offer itself carries the public price — a test may pin this), promising faster than the offer (instant activation vs «2 рабочих дня» is never a violation); (3) out of scope — contacts inside the ПДн/РКН-registered policies: a registered policy may name a specific address, so align those only with the lawyer's explicit approval.
- When a «все как в документах» fix wave lands, re-check both repos' `company.ts` (license-service `frontend/packages/shared/src/shared/config/`, crbsit-site `src/entities/company/model/`) in the same change — the same contact lives in both and they drift apart independently.

### Full wording audit ("перепроверь всё с юридической точки зрения")

When Leonid asks for a legal sweep of user-facing texts, dispatch one vision-free subagent per site (license-service and crbsit-site are governed by the SAME offers) with this scope — UI alone is not enough:
- Frontend: public site tariff/licensing texts, cabinet purchase/renew/top-up dialogs, admin, LegalLinks/footer.
- Backend texts are legally significant: mail templates (`grep -rn template backend/app --include='*.py' | grep -i mail`), `purpose_template` in `backend/settings.py` (the «Назначение платежа» the user copies for bank transfer), transaction comments. Verify each against п. 6.6 verbatim.
- Each formulation gets a verdict: СООТВЕТСТВУЕТ (offer clause) / РАСХОЖДЕНИЕ (file:line, what) / НЕТ В ДОКУМЕНТАХ (UI asserts something no doc covers — risk) / НЕ КРИТИЧНО (UI slang, no legal assertion). Report to `docs/legal-review-wording*.md` on the branch.
- High-risk patterns to check for: promising instant activation (offer says «как правило 2 рабочих дня»), «бессрочно/навсегда» for anything (base license is 5 лет with auto-renewal; PrimePilot firmware is 0 ₽ with NO paid configurations — п. 4.2), SLA/30-min fund figures, support contacts vs the offer.
- Companion docx (тарифы, договор на доработку) have no PDF tooling: read via `python3 -c "import zipfile; print(zipfile.ZipFile(f).read('word/document.xml').decode())"` and strip tags.
- Reuse the transcripts already in scratch (`~/.hermes/cache/scratch/offer-pages/transcript-*.md`) before re-OCR-ing the PDFs — they survive across sessions until pruned.

## Prod pitfall: .mjs MIME breaks the pdf.js worker

The primepilot-main nginx maps `.mjs` → `application/octet-stream`; browsers refuse module workers with that MIME, so the offer viewer shows «Не удалось загрузить PDF» while the PDF itself is served fine (dev works because Vite serves correct `text/javascript`). Fixed on BOTH sides: `assetFileNames` in `frontend/public/vite.config.ts` emits the worker as `.js`, and primepilot-main's `/etc/nginx/mime.types` now maps `application/javascript js mjs` (verified with curl on a `.mjs` asset — a correct `.js` response does not prove the mapping). If a «PDF won't load» report comes in prod, check `performance.getEntriesByType('resource')` in the page: no PDF request = worker/MIME problem, not a content problem. Do NOT fix by overwriting live `/etc/nginx/sites-available/*` with repo templates — certbot modifies those; the allowed sudoers path (`cp` site file from `/opt`, `nginx -t`, `reload`) would clobber certbot TLS changes.

## Merge → main → prod deploy

CI on `main` (primegit.ru GitLab) runs `npm run check` (format/typecheck/lint/test/build) per SPA and 221+ shared tests; `deploy-prod` is a manual job — trigger it via the Primegit API (token already configured in the Hermes env as `PRIMEGIT_TOKEN`; every API call must bypass the clash proxy — unset the `*_proxy` vars or use a no-proxy opener, or the TLS handshake dies). Procedure: find the pipeline (`GET /api/v4/projects/<pid>/pipelines?ref=main`, match the pushed sha), wait for checks to finish, then `POST /api/v4/projects/<pid>/jobs/<job-id>/play` for the deploy job, and poll the job until `success`. Project IDs: license-service = 22, crbsit-site = 23. Smoke prod afterwards (site 200, API auth endpoint answers 401) — a green deploy job does not prove the site serves.

Before merging to `main`:
- Leonid prefers SQUASH merges for a feature wave: in a throwaway worktree on fresh `main`, `git merge --squash <branch>` → one commit → `git push origin HEAD:main` (keep the feature branch). Verify the squash commit is content-identical to the branch (`git diff <branch> HEAD` empty) before pushing.
- If `package.json` gained deps without a lock update, `npm ci` (CI step 1) fails hard. Generate the lock update in a clean worktree (`npm install` there), commit the lockfile, THEN merge — never push a package.json/lock mismatch to main.
- Run the exact CI command (`npm run check`) locally in a clean worktree, not just the affected package's tests.
- crbsit-site deploys the same way: push to `main`, then play its `deploy` manual job (project 23).

Static-file perms: files copied from `~/Downloads` inherit `600`; nginx runs as `www-data` and serves them 403 while everything else on the site works. `chmod 644` uploaded PDFs/assets after deploy and verify with curl (status + byte size vs source).

Deploy verification: curl the viewer routes AND the PDFs directly — a 200 on the page does not prove the assets load.

## Local full-stack demo (worktree + docker compose + seed)

To show Leonid the app running with branch code, run the stack inside the feature worktree so `./backend` mounts that branch's code:
1. Copy env from the main checkout first — a fresh worktree has no `.env`, and compose silently fails to start without it: `cp ~/work/license-service/backend/.env <worktree>/backend/.env` (same for any other compose-consumed env).
2. Start with `docker compose up -d` — run it as a background terminal call with `notify=true` and poll `docker compose ps` via process_manage; a foreground call that starts containers is rejected as a long-lived process. Wait for readiness (healthcheck or a curl of the API) in a separate foreground command before seeding.
3. Seed with `make seed` (runs `scripts/seed_org_demo.py` in the api container). It prints the demo creds table at the end: admin on port 37175, app (client cabinet) on 37174, public site on 37173, API on 38080, Mailpit on 38125. All demo users share the seed's fixed TOTP secret — hand over the currently printed code; it rotates, so regenerate if it expired (no re-seed needed: `docker compose exec -T -e PYTHONPATH=/app api python scripts/print_local_creds.py` re-prints creds + a fresh TOTP). For a scripted live check, log in via `POST /api/v1/auth/login {email, password, totp_code}` with a cookie jar and call `/api/v1/payment-details` to verify the requisites/purpose payload end-to-end.
4. Verify before handing over: curl each port for 200, don't trust "containers Up".

Seed scripts are real API clients, not fixtures — they call managers directly (`manager.license.activate_for_device(...)`). Grep `backend/scripts/*.py` for any manager method whose signature you change; a missed call site only explodes at `make seed` time, on a stack Leonid is already looking at. Keep seeds idempotent: they re-run over an already-seeded org loop (e.g. the active-cabinet scenario is seeded twice), so check before mutating — for licenses, `get_active_for_device(...) is None` before `activate_for_device(action="purchase_and_assign")`, since the manager raises ConflictError on double purchase. If a partially-failed seed leaves dirty state, `docker compose down -v` and re-seed clean rather than patching around the leftovers.

## Dev servers vs git operations

A running vite watcher dies (or corrupts) when you `git checkout`/merge in the same worktree underneath it — expect both dev ports (5173/5174) down after a merge/deploy session. Restart them after git surgery, and re-check with curl before telling Leonid «проверяй».

## Network: RU hosting vs local proxy

primepilot.tech sits on RU hosting and breaks through the local clash proxy (TLS handshake hangs inside CONNECT; direct works). If the site "won't load", first diff direct vs via-proxy with curl before touching the site. Fix is a PAC exception `dnsDomainIs(host, "primepilot.tech")` → DIRECT in `~/Library/Application Support/dev.clashghost.app/proxy.pac` (suffix match covers all subdomains); see the macos-proxy-ops skill for the proxy workflow.
