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
- Know the 2 pre-existing steiger `fsd/insignificant-slice` errors on `features/view-pdf` (only referenced from `pages/offer`) — they fail `npm run lint` and are NOT caused by your change. Confirm by checking against HEAD~1 before "fixing" them; ask Leonid whether to merge the slice or ignore before restructuring.

## Shared working tree — foreign edits everywhere

Parallel Hermes sessions drop uncommitted edits into this repo (cabinet widgets, brand assets). Rules:
- NEVER `git stash -u` here: the stash swallows foreign edits and the pop conflicts mid-foreign-work. Stage only your own paths by explicit path (`git add <paths>`), never `git add -A`.
- If foreign edits block a checkout, commit them to a dated `wip/unsaved-YYYY-MM-DD` branch on their own — never discard, never mix into your feature commit.
- If a stash conflict happened anyway, resolve toward the stashed (newer) side and verify `grep -c '<<<<<<<'` = 0 afterwards.

## Offer links & PDF viewer conventions

- Offer links in shared `LegalLinks` must be host-aware: relative `/offer/<slug>` when hostname is `primepilot.tech`/`localhost`/`127.0.0.1` (viewer lives there), absolute `https://primepilot.tech/offer/...` from cabinet/admin (no local viewer). A hard-coded absolute URL sends localhost clicks to prod — Leonid rejects that.
- The primepilot PDF viewer is a copy of crbsit-site's with primepilot styling: NO card borders or `bg-card` background around pages (transparent gutters, page edge-to-edge). Keep the two implementations visually distinct; don't "sync" styles back to crbsit without asking.
- Legal labels use full product names: «Оферта PRIMEPILOT», «Оферта PRIMEPILOT Configurator».

## Network: RU hosting vs local proxy

primepilot.tech sits on RU hosting and breaks through the local clash proxy (TLS handshake hangs inside CONNECT; direct works). If the site "won't load", first diff direct vs via-proxy with curl before touching the site. Fix is a PAC exception `dnsDomainIs(host, "primepilot.tech")` → DIRECT in `~/Library/Application Support/dev.clashghost.app/proxy.pac` (suffix match covers all subdomains); see the macos-proxy-ops skill for the proxy workflow.
