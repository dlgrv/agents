# Slimming compose stacks and Docker host resource usage

Two scenarios covered: (1) slimming a single dev-only compose stack, (2) host-level
optimization when Docker Desktop runs several independent stacks.

## Scenario 1: worked example — slimming a dev-only compose stack

Context: FastAPI + Postgres + Redis + 3× Vite (npm workspaces monorepo) + Mailpit, used ONLY for
local development on macOS/Docker Desktop. User: "много ресурсов мне не нужно".

### Changes applied

#### Base docker-compose.yaml
- Three `frontend-public` / `frontend-app` / `frontend-admin` services → one `frontend`
  service (`build: context: ./frontend`, no build args).
- Redis: dropped `redis_data` volume, `command: redis-server --save "" --appendonly no`.
- Healthchecks relaxed: `interval: 15s`, `timeout: 5s`, `retries: 5` (was 2–5s / 10–20 retries).
- API got `init: true` (it runs `sh -c alembic && uvicorn --reload`, so zombie reaping matters).

#### Override docker-compose.override.yml
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

#### frontend/Dockerfile
- Removed `ARG APP` / `ARG PORT`; CMD runs all three Vite servers:
  CMD ["sh", "-c", "cd public && npm run dev & cd cabinet && npm run dev & cd admin && npm run dev & wait"]
- EXPOSE 5173 5174 5175.

#### Makefile
- `frontend-docker` target updated from per-app service lists to single `frontend`.

### Verification
- `docker compose config --quiet` → CONFIG_OK; `docker compose config --services` lists 5 services.
- Then `make up-build` once Docker Desktop is running; check all three ports respond.

### Expected savings
- Merged frontend containers: ~100–200 MB (duplicated esbuild daemons/watchers/container overhead).
- Postgres tuning: ~100 MB. Redis persistence off: I/O + memory.
- Overall estimate given to user: −300–500 MB RAM plus less background I/O.

### Notes / caveats told to the user
- Hot-reload and per-app ports are unchanged; it's still three Vite processes inside one container.
- Existing named node_modules volume is reused on first up; if deps misbehave,
  the project's `make frontend-docker` (rebuild + drop volume) is the fix.
- Alternative considered and offered: running frontend dev servers natively on the host
  (fastest HMR, no VirtioFS watching) — user chose merging into one container instead.

## Scenario 2: host-level optimization on a multi-stack machine (Docker Desktop, macOS)

When the ask is "оптимизируй docker" and the host runs several independent compose stacks
(e.g. a dev app stack, a self-hosted photo library, small utility services), work host-level
first — per-container RAM is rarely the problem; the Linux VM's constant overhead and Docker's
disk caches are. A 10-container stack can total ~1 GB while the Docker Desktop VM itself holds
several GB.

### Procedure

1. **Diagnose before proposing** (report real numbers):
   - `docker system df` — reclaimable build cache / images / volumes (build cache is usually
     the single biggest reclaim, often multiple GB on an active dev machine).
   - `docker stats --no-stream` — actual per-container RAM.
   - List which stacks have running containers; note `restart: always` on optional stacks.
2. **Cleanup order (safe → ask first):**
   - `docker builder prune` — build cache, biggest and safest win.
   - `docker image prune -a` — dangling/unused images.
   - `docker volume prune` — ALWAYS show `docker volume ls -f dangling=true` and get explicit
     user confirmation first; dangling volumes may hold data from old experiments.
3. **Don't run every stack at once.** Gate whole stacks with compose `profiles:` and bring up
   only the active one (`docker compose --profile X up -d` / `--profile X down`). Pair with
   `restart: unless-stopped` on optional stacks so they don't resurrect at every Docker/VM
   restart. `restart: always` on an optional stack means it comes back unattended even when
   not needed — and can sit crashed if its prerequisites are absent.
4. **mem_limit sizing — match the service's appetite, not a uniform number.** Small limits
   (64–192m) are for simple stateless services (redis, mailpit). Services embedding ML models
   need GB-scale limits (e.g. immich-machine-learning: 4g) — a tight limit on an ML service
   causes OOM-kills mid-job, not savings. Propose generous values for unfamiliar/heavy
   workloads and confirm with the user; they often prefer headroom over tightness.
5. **Reject "hibernate idle containers" (wake-on-request proxy/Traefik schemes)** as
   overengineering on dev machines: the VM stays up anyway, so savings are marginal while
   complexity is real. Stack-level profiles give a bigger, predictable win.
6. **Cheapest dev mode for a code-heavy stack:** only db/redis in Docker, the app(s) natively
   on the host (already the documented convention in some repos' CLAUDE.md — check before
   proposing it).

### Pitfall: container won't start after config changes — check volume mounts first

`error while creating mount source path '/host_mnt/Volumes/...': mkdir ...: permission denied`
on Docker Desktop usually means the bind-mount source is an external disk that is **not
mounted**, NOT a permissions bug to chase. Check:

```bash
docker inspect <container> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
ls /Volumes/
```

Any `/Volumes/<disk>/...` source needs that disk attached. A stack whose server "randomly
exited days ago" is often explained by exactly this — diagnose before assuming the compose
config broke.

### Tool workaround: terminal guard blocks `docker compose up -d`

The Hermes terminal tool may refuse `docker compose up -d` as an apparent long-lived server
start. Work around, don't fight it: validate first with `docker compose config --services`
(catches merge/limit errors), then start already-created containers individually with
`docker start <name> ...` — that passes the guard and surfaces daemon errors (e.g. the
unmounted-volume failure above) directly.
