# Standalone preview apps (design prototypes) in a monorepo

Pattern for shipping design prototypes that are isolated from the main apps but still build in CI and deploy behind nginx. Source of record: license-service (app.primepilot.tech); the sibling preview `frontend/previews/5e37ae` is the reference implementation. Use when the user asks for a "визуальный прототип ЛК / мок home + shell" etc.

## Layout
- `frontend/previews/REGISTRY.md` — one row per preview: `<hash> | <title> | active|archived` (e.g. `127db3 | cabinet home+shell mock (frosted glass restyle) | active`). **Read it first and pick a free 6-hex hash** — never reuse or collide with archived rows.
- `frontend/previews/<hash>/` — fully standalone Vite+React package: own package.json (`<repo>-preview-<hash>`), `vite.config` with `base: '/<hash>/'`, own tsconfig, own vitest, `src/{app,components,data}`. Mock data in `src/data/mock.ts` — no auth/API wiring, it's a design artifact.
- Do NOT touch `frontend/cabinet`, `frontend/admin`, `packages/` — isolation is the point.

## Branching (critical)
The preview infra (REGISTRY, nginx conf, `.gitlab-ci.yml`, `deploy.sh`) lives on the FIRST preview branch, not main. A new preview branches FROM THE SIBLING PREVIEW BRANCH (e.g. `feature/cabinet-preview-5e37ae`) in a worktree:
`git worktree add .worktrees/cabinet-preview-<hash> <new-branch>`.
Branching from main loses the deploy plumbing and the preview never ships.

## Infra changes (4 files, copy the sibling's shape 1:1)
1. `REGISTRY.md` — add the row.
2. `deploy/nginx/sites/app.primepilot.tech` — `location = /<hash>` (302 → `/<hash>/`) + `location ^~ /<hash>/` with `alias .../previews/<hash>/`, SPA fallback `@preview_<hash>` (`try_files $uri $uri/ /<hash>/index.html`), security headers.
3. `.gitlab-ci.yml` — build block: `cd frontend/previews/<hash> && npm ci && npm run build`, artifact `dist/`.
4. `deploy/scripts/deploy.sh` — rsync `dist/` → `${WWW}/previews/<hash>/` with a fail-if-dist-missing guard.

## Verification before handing over (all passed on 127db3)
- `npm run build` (tsc -b + vite) — exit 0.
- vitest — **ru-RU currency pitfall:** `Intl.NumberFormat('ru-RU')` inserts NBSP (U+00A0) as the group separator; string assertions must normalize `text.replace(/\u00a0/g, ' ')` or they fail for no visible reason.
- `vite preview --port <port>` (per-preview port; 127db3 used 5203) + curl: `/`, js/css assets, font file, and an SPA route that must hit the fallback → index.html, 200. Note: with `base: '/<hash>/'` the root URL 404s locally — always open the `/<hash>/` path.
- Headless computed-style audit (fonts loaded, sub-10px text scan, backdrop-filter actually applied, no horizontal scroll, modal opens) — see the `web-design-extraction` skill, "Design-prototype acceptance audit" section.
- Screenshots (desktop + a key state like an open modal) delivered via `MEDIA:` for human review.

## Concretely (127db3, the worked example)
Glassmorphism restyle on the M.O.N.K.Y template basis: two fonts only (Inter + repo mono for caps labels/digits/IDs), frosted `backdrop-filter: blur(18px) saturate(140%)` over oklch translucent surfaces on a dusk gradient + noise, status colors from NTA, secondary text 14px, nothing below 10px, labeled sidebar (not icon-only), mobile bottom tab bar, `prefers-reduced-motion` + `@supports` fallback for no-backdrop-filter browsers.

## Rules
- Commit/MR only on explicit user request (house rule) — check `dist/` and `tsconfig.tsbuildinfo` don't leak into git before committing.
- After merge, CI builds and deploy.sh rsyncs; live at `https://app.primepilot.tech/<hash>/`.
