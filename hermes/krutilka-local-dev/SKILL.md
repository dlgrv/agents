---
name: krutilka-local-dev
description: Run krutilka locally — docker ports, creds, rebuild gotchas.
---

# Krutilka (Lowbid) local runbook

Repo: `/Users/dlgrv/aezly/krutilka`. Ad-traffic generator (OpenRTB bid + VAST playback) for testing the internal anti-fraud system.

## Services (docker compose at repo root)

| Service | Container | Port |
|---|---|---|
| API (FastAPI) | lowbid_api | 8000 (`/docs` for Swagger) |
| Frontend | lowbid_frontend | 5173 |
| uSSP mock (test SSP) | lowbid_ussp_mock | 8091 (`/docs`) |
| Postgres | lowbid_postgres_db | healthy-gated |
| Redis | lowbid_redis | healthy-gated |
| bid_worker / playback_worker | — | — |

## Admin login

- Login: `bootstrap@test.local` (auto-created from env on first API start when users table is empty).
- Password: `backend/.env` → `BOOTSTRAP_ADMIN_PASSWORD` at first bootstrap. Do not rely on the env var later: the password is only hashed in the DB, so a missing env var means the old password is unrecoverable — reset the hash, don't hunt for it.
- Never print a password in chat, even when the user asks and says it's test-only — reset it to a new dev password and hand over the new one (that is what the user actually needs).
- Verify any reset with `curl -s -X POST http://127.0.0.1:8000/api/auth/login -H 'Content-Type: application/json' -d '{...}' -o /dev/null -w '%{http_code}'` → expect 200 before reporting success.

### Password-reset recipe (verified)

Run inside the API container — it has all deps and DB access; no psql needed:

```bash
docker exec lowbid_api python -c "
import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.utils.default.database import get_async_engine
from app.database.models import User
from app.services.auth.passwords import hash_password
from settings import settings

async def main():
    engine = get_async_engine(params=settings.db, application_name='password-reset')
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        row = await session.scalar(select(User).where(User.email=='bootstrap@test.local'))
        row.password_hash = hash_password('<NEW_DEV_PASSWORD>')
        row.session_version = (row.session_version or 0) + 1  # invalidates old sessions
        await session.commit()
    await engine.dispose()

asyncio.run(main())
"
```

Note the import paths — they differ from what the file layout suggests: engine factory is `app.utils.default.database.get_async_engine(params=settings.db, application_name=...)` (needs both args), session factory is plain `async_sessionmaker`, not a helper in `app.database`. `app.database.session` does not exist. Check `backend/app/api/lifespan.py` for the canonical wiring before scripting against the DB.

## Frontend conventions (verified in repo)

- **Two content modules, split by purpose**: visible chrome labels (tabs, buttons) live in `src/content/uiStrings.ts` (English), per-field help tooltips live in `src/content/campaignFieldHelp.ts` (Russian). When adding a control you usually need both; never hardcode the label string in the component. The user flags mixed-language chrome (e.g. a Russian tab next to English `Runtime`/`Settings`) as a bug.
- **Tests import the shared strings, not literals**: a Playwright spec that clicks `getByRole('tab', { name: 'Калькулятор' })` breaks on the next label change; import from `uiStrings`/`campaignFieldHelp` like the components do. After changing any label or dialog, grep the test tree for the old string.
- **This is a test instrument: do NOT hard-cap tunable parameters for 'realism'.** The user removed 1–3 caps on profiles-per-IP / sessions-per-day with «убери все ограничения» — realism guidance belongs in the help tooltip («обычно 1–2, но можно любое»), never in validation. Keep only sanitary lower bounds (≥1, gap ≥0) that protect the math. When adding or relaxing any bound, touch ALL layers in one change: backend `MAX_*` constants (identity/user_profile.py), API `Field(ge=…, le=…)` (api/entities/campaign_settings.py), `frontend/src/constants/campaignSettings.ts`, the help text in campaignFieldHelp.ts, and grep the test tree for the old cap — a test pinning the rejected value will fail after widening.
- **Master enable/disable toggle goes FIRST in a settings block**, before all numeric parameters of that feature. The user flagged a feature flag sitting last in its own block as wrong (fields had been added in implementation order, flag appended last) — placement must follow the reader's logic: on/off first, then the knobs.
- **Tri-state or multi-option controls need each option explained in plain language on the question-mark tooltip** (e.g. «Включено» = what happens, «Выключено» = what happens, «Как на сервере» = inherit global), not just the field name restated. The user asks for plain-language explanations of such toggles.
- **Controlled `<input type="number">` with clamping must keep a draft string while the user types** (see `CampaignProfileSettings.tsx` NumberField): clamping `Number(e.target.value)` on every change snaps empty/garbage input to `min` (NaN → min), so the field 'sticks' at 1 and the user cannot clear or retype. Store the raw string in local state, render it, commit the clamped number on blur/Enter only. The user reported exactly this stuck-at-1 behavior as a bug.
- **After any scripted splice/regex edit of a .tsx file, run `npm run check` before claiming done** — index-based replacement of a function body can silently eat the adjacent props-interface declaration; TypeScript errors surface only in the check, not in patch diffs.
- **Actions that apply/overwrite settings open the repo's existing `ConfirmDialog` first** (title + what-will-change description + Apply/Cancel) — the user asked for this pattern on "apply recommendations"-style buttons; treat it as the default for destructive or bulk-apply actions.

## Gotchas

- **Backend dep change → rebuild image**: `docker compose up -d --build api`. A plain `up -d` keeps the stale image (happened with `itsdangerous` after auth feature). Same for workers if they share requirements.
- **Port 8000 conflicts**: stray `python -m http.server` processes from other sessions occupy it. Check `lsof -i :8000` before blaming docker.
- **Postgres queries**: `docker compose exec postgres_db` may report "not running" even when the container is up — use `docker exec lowbid_postgres_db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "..."'`.
- Full test suite (backend): run `cd backend && uv run python -m pytest tests -q`. 1000+ tests as of the adversarial-fixes wave; coverage ~75% (new modules 88-99%). `pytest-cov` is NOT in deps — `uv pip install pytest-cov` for a coverage run. e2e Playwright needs docker services up (webServer 120s timeout otherwise fails — infra, not code).
- **Treat e2e failures in layout specs (mpg-layout, mobile-nav, campaigns-reorder) as flakes until proven otherwise**: run in full parallel they sub-pixel-fail against the one shared dev server under load, but pass when the same specs are re-run in small groups (4-9 tests). Triage rule: re-run only the failing specs with lower parallelism; only if a spec fails in isolation too, suspect real code — and confirm pre-existence by stashing local changes (`git stash -u`, re-run, `git stash pop`) instead of checking out another ref's files.
- **`git checkout <ref> -- frontend/` leaves the copied files STAGED in the index.** After a ref-swap probe, restore with `git reset HEAD` + `git checkout -- <paths>` and verify `git status --short` shows no modified entries before committing anything. Probe-copied paths can also stay UNTRACKED, which then blocks switching branches: `git checkout main` refuses to overwrite untracked files that exist on main (and a `gh pr merge` will not touch them either) — just `rm` the probe-copied paths, they return from the target branch on checkout.
- **Chaos/integration tests run against LIVE Redis db15** (docker `lowbid_redis`), by repo convention (see `test_profile_store.py` for the db15 + pool-id isolation pattern) — FakeRedis only where the repo already uses it. The whole suite passes against the live store; run it with the compose stack up.
- "The new UI settings are missing" reports: verify the SERVED bundle first (grep the frontend container's output for the new symbol) before debugging code — the usual cause is a cached browser bundle or the user looking in the wrong place (settings live inside the campaign detail form, not on the campaign list); then have the user hard-refresh.
- **Alembic `server_default` with a SQL expression must be wrapped in `sa.text()`** (e.g. `server_default=sa.text("'{}'::json")`) — a plain string is sent by asyncpg as a bound parameter, so expression defaults like `'{}'::json` fail the migration with invalid-json, while the same code works on psycopg. When a migration fails on the live stack, run `docker compose exec api ... alembic upgrade head` again after fixing and confirm the version table advanced.

## Production deploy (button workflow; `docs/lowbid-cicd.md` in-repo is the source of truth)

- User's standing flow: merged PR → deploy IMMEDIATELY in the same turn ("деплой сразу после мержа"). `gh workflow run cd.yaml --ref main`, then poll `gh run view <run-id> --json status,conclusion` in a loop (foreground sleep-loops >600s auto-promote to a tracked background process — fine, the notification arrives on its own; deploy takes ~2–5 min).
- Prod smoke over SSH (`dlgrv@135.106.162.15`, key `~/.ssh/id_ed25519_lowbid`) — **`/docs` returning 404 is EXPECTED in prod** (`APP_ENV=prod` hides it; do not 'fix' it): probe API liveness with `curl -X POST http://127.0.0.1:8000/api/auth/login -H 'Content-Type: application/json' -d '{}'` → 422 = endpoint alive; nginx `/` → 302 = auth redirect working; `ls /var/www/lowbid/dist/index.html`; `systemctl is-active lowbid_api lowbid_bid_worker lowbid_playback_worker@1 lowbid_playback_worker@2` + both timers.
- Prod `.env` and DB survive every deploy (workflow backs up and restores them) — prod credentials are NOT the local dev ones; the local password-reset recipe never touches prod.
- **Small post-merge hotfixes go direct to main** on the user's explicit "пуш и деплой": commit `fix(lowbid-NN): ...` → `git push origin main` → wait for CI on main → `gh workflow run cd.yaml --ref main` → poll run → SSH smoke (`curl` login page 200 + `systemctl is-active lowbid_api lowbid_bid_worker`). The PR route stays the default for feature waves; direct push is the user's call, never a default.
- Restart logic in deploy scripts must enumerate instantiated systemd units explicitly: `systemctl list-unit-files --state=enabled` lists only the TEMPLATE of a template unit (status `indirect`), so running instances `@1/2` are invisible and a match-based restart branch silently no-ops on them. Match with `systemctl list-units --all '<name>@*'` or restart the explicit instance list — then verify fresh `ActiveEnterTimestamp` per instance, per the standing post-deploy rule.
- New behavior ships behind a global env flag defaulting OFF in prod (e.g. profile leases: absent `PROFILE_LEASE_ENABLED` = disabled), so a deploy never changes live traffic by itself — enabling is a separate explicit step the user controls.

## Verified happy path

`docker compose up -d --build api` → all 7 containers Up/healthy → curl 200 on :8000/docs, :5173, :8091/docs.

## Test/fix workflow for this repo (proven)

Delegated waves (test-writers, implementers, reviewers) via subagent-driven-development; plan files in `.hermes/plans/`. Bugs found by adversarial tests are pinned as strict-xfail with BUG-ids — a fix commit's acceptance criterion is "xfails removed AND green". See `programmatic-adtech` skill (anti-fraud evasion + SDD sections) for the per-task dispatch protocol; `lowbid-git-workflow` for the commit gate (fix commits: `fix(lowbid-NN): ...`, never push without an explicit ask).
