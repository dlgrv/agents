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

## Gotchas

- **Backend dep change → rebuild image**: `docker compose up -d --build api`. A plain `up -d` keeps the stale image (happened with `itsdangerous` after auth feature). Same for workers if they share requirements.
- **Port 8000 conflicts**: stray `python -m http.server` processes from other sessions occupy it. Check `lsof -i :8000` before blaming docker.
- **Postgres queries**: `docker compose exec postgres_db` may report "not running" even when the container is up — use `docker exec lowbid_postgres_db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "..."'`.
- Full test suite (backend): ~200+ tests; e2e Playwright needs docker services up (webServer 120s timeout otherwise fails — infra, not code).
- "The new UI settings are missing" reports: verify the SERVED bundle first (grep the frontend container's output for the new symbol) before debugging code — the usual cause is a cached browser bundle or the user looking in the wrong place (settings live inside the campaign detail form, not on the campaign list); then have the user hard-refresh.

## Verified happy path

`docker compose up -d --build api` → all 7 containers Up/healthy → curl 200 on :8000/docs, :5173, :8091/docs.
