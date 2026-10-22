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
- Run tests per project: `npx vitest run --project packages` (shared), `npx vitest run src/features/view-pdf` etc.
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

## Prod pitfall: .mjs MIME breaks the pdf.js worker

The primepilot-main nginx maps `.mjs` → `application/octet-stream`; browsers refuse module workers with that MIME, so the offer viewer shows «Не удалось загрузить PDF» while the PDF itself is served fine (dev works because Vite serves correct `text/javascript`). Fixed on BOTH sides: `assetFileNames` in `frontend/public/vite.config.ts` emits the worker as `.js`, and primepilot-main's `/etc/nginx/mime.types` now maps `application/javascript js mjs` (verified with curl on a `.mjs` asset — a correct `.js` response does not prove the mapping). If a «PDF won't load» report comes in prod, check `performance.getEntriesByType('resource')` in the page: no PDF request = worker/MIME problem, not a content problem. Do NOT fix by overwriting live `/etc/nginx/sites-available/*` with repo templates — certbot modifies those; the allowed sudoers path (`cp` site file from `/opt`, `nginx -t`, `reload`) would clobber certbot TLS changes.

## Merge → main → prod deploy

CI on `main` (primegit.ru GitLab) runs `npm run check` (format/typecheck/lint/test/build) per SPA and 221+ shared tests; `deploy-prod` needs a manual Play button — either Leonid clicks it, or deploy manually: the `prime-service-gitlab-deploy` SSH key (the CI deploy key) authenticates as `deployer@94.26.229.45` — build each SPA in a CLEAN worktree at `main` head and rsync like the CI job does.

Before merging to `main`:
- If `package.json` gained deps without a lock update, `npm ci` (CI step 1) fails hard. Generate the lock update in a clean worktree (`npm install` there), commit the lockfile, THEN merge — never push a package.json/lock mismatch to main.
- Run the exact CI command (`npm run check`) locally in a clean worktree, not just the affected package's tests.
- crbsit-site deploys differently: push to `main`, then the documented manual rsync path.

Static-file perms: files copied from `~/Downloads` inherit `600`; nginx runs as `www-data` and serves them 403 while everything else on the site works. `chmod 644` uploaded PDFs/assets after deploy and verify with curl (status + byte size vs source).

Deploy verification: curl the viewer routes AND the PDFs directly — a 200 on the page does not prove the assets load.

## Dev servers vs git operations

A running vite watcher dies (or corrupts) when you `git checkout`/merge in the same worktree underneath it — expect both dev ports (5173/5174) down after a merge/deploy session. Restart them after git surgery, and re-check with curl before telling Leonid «проверяй».

## Network: RU hosting vs local proxy

primepilot.tech sits on RU hosting and breaks through the local clash proxy (TLS handshake hangs inside CONNECT; direct works). If the site "won't load", first diff direct vs via-proxy with curl before touching the site. Fix is a PAC exception `dnsDomainIs(host, "primepilot.tech")` → DIRECT in `~/Library/Application Support/dev.clashghost.app/proxy.pac` (suffix match covers all subdomains); see the macos-proxy-ops skill for the proxy workflow.
