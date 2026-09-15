# Worked example: slimming a dev-only compose stack

Context: FastAPI + Postgres + Redis + 3× Vite (npm workspaces monorepo) + Mailpit, used ONLY for
local development on macOS/Docker Desktop. User: "много ресурсов мне не нужно".

## Changes applied

### Base docker-compose.yaml
- Three `frontend-public` / `frontend-app` / `frontend-admin` services → one `frontend`
  service (`build: context: ./frontend`, no build args).
- Redis: dropped `redis_data` volume, `command: redis-server --save "" --appendonly no`.
- Healthchecks relaxed: `interval: 15s`, `timeout: 5s`, `retries: 5` (was 2–5s / 10–20 retries).
- API got `init: true` (it runs `sh -c alembic && uvicorn --reload`, so zombie reaping matters).

### Override docker-compose.override.yml
- Postgres dev tuning:
  command: >
    postgres -c shared_buffers=32MB -c max_connections=20
             -c effective_cache_size=64MB -c work_mem=2MB
  mem_limit: 192m
- Limits as safety net: api 512m, redis 64m, mailpit 128m.
- Mailpit: `command: --max-messages 200` (it grows unbounded with mail volume).
- Single frontend service publishes all three ports:
    ports:
      - "${FRONTEND_PUBLIC_PORT:-37173}:5173"
      - "${FRONTEND_APP_PORT:-37174}:5174"
      - "${FRONTEND_ADMIN_PORT:-37175}:5175"
    volumes:
      - ./frontend:/frontend
      - frontend_node_modules:/frontend/node_modules
    command: sh -c "cd public && npm run dev & cd cabinet && npm run dev & cd admin && npm run dev & wait"

### frontend/Dockerfile
- Removed `ARG APP` / `ARG PORT`; CMD runs all three Vite servers:
  CMD ["sh", "-c", "cd public && npm run dev & cd cabinet && npm run dev & cd admin && npm run dev & wait"]
- EXPOSE 5173 5174 5175.

### Makefile
- `frontend-docker` target updated from per-app service lists to single `frontend`.

## Verification
- `docker compose config --quiet` → CONFIG_OK; `docker compose config --services` lists 5 services.
- Then `make up-build` once Docker Desktop is running; check all three ports respond.

## Expected savings
- Merged frontend containers: ~100–200 MB (duplicated esbuild daemons/watchers/container overhead).
- Postgres tuning: ~100 MB. Redis persistence off: I/O + memory.
- Overall estimate given to user: −300–500 MB RAM plus less background I/O.

## Notes / caveats told to the user
- Hot-reload and per-app ports are unchanged; it's still three Vite processes inside one container.
- Existing named node_modules volume is reused on first up; if deps misbehave,
  the project's `make frontend-docker` (rebuild + drop volume) is the fix.
- Alternative considered and offered: running frontend dev servers natively on the host
  (fastest HMR, no VirtioFS watching) — user chose merging into one container instead.
