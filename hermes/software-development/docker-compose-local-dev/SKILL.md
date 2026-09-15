---
name: docker-compose-local-dev
description: "Add Docker/docker-compose for local development with instant code-reload (no rebuild), without breaking an existing non-Docker (or Docker) production CI/CD pipeline. Covers base+override compose files, live-reload mechanisms per stack, and the classic bind-mount pitfalls."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docker, docker-compose, local-development, live-reload, hot-reload, devops, ci-cd]
    related_skills: [plan, github-pr-workflow]
---

# Docker Compose for Local Development

Use this skill when the user wants `docker compose up -d` to bring up a service for local dev, with code changes picked up immediately (no image rebuild, no manual restart).

## Before proposing anything: check the existing CI/CD

Never assume containerizing local dev affects production. Many services deploy via `tar`+`scp`+`systemd`/bare VM and never touch Docker in prod — in that case new Dockerfiles/compose files are purely additive and inert for deploy. Verify, don't assume:

1. `search_files(target='files', pattern='*.yml')` / `*.yaml` at repo root and `.github/workflows/` — read every CI/CD workflow file found.
2. Check for deploy docs (`docs/*cicd*.md`, `docs/*deploy*.md`, `README`) describing the prod pipeline.
3. Confirm explicitly whether the deploy workflow references `docker`, `docker-compose`, `Dockerfile`, or a registry push. If it does not (e.g. it does `rsync`/`scp` + `systemctl restart`), state plainly that new Docker files are inert for prod deploy and won't be picked up by that pipeline.
4. If the deploy pipeline packages the whole repo into an archive (e.g. via `rsync --exclude=...` then `tar`), new Docker files will ride along as harmless dead weight unless explicitly excluded — flag this to the user as optional cosmetic cleanup, not a blocker, and let them decide (some prefer not to touch a working deploy script at all).

## Core pattern: base + override compose files

Don't cram dev-only hacks (bind mounts, `--reload` flags) into a single compose file that might later double as a prod/CI reference. Split:

- `docker-compose.yaml` — base: service definitions, `build:`, healthchecks, networks, ports. No volumes-over-code, no reload flags. This is what you'd also use for a "prod-like" sanity build.
- `docker-compose.override.yml` — dev-only: bind-mounts (`./backend:/app`), `--reload`/watch commands, dev env vars.

`docker compose up -d` with **no `-f` flag automatically merges `docker-compose.yaml` + `docker-compose.override.yml`** if the override file sits next to the base file — this is Compose's default discovery behavior, not a manual merge. So the user's literal ask ("just `docker compose up -d`") is satisfied while keeping the files clean. To sanity-check the base alone (e.g. simulate what CI would build): `docker compose -f docker-compose.yaml up -d` explicitly skips the override.

## Live-reload mechanisms — the point is to not reinvent this

The reload behavior almost always already exists in the dev server; you're just making sure the container can see file changes on disk.

| Stack | Mechanism | Notes |
|---|---|---|
| FastAPI/Python | `uvicorn ... --reload` | Uses `watchfiles` (inotify-based) when `uvicorn[standard]` is installed — not slow polling. |
| Vite/React | Built-in HMR | Needs `--host 0.0.0.0` in the container so the dev server is reachable from outside; nothing else to configure. |
| arq workers | `arq <settings> --watch <path>` | arq's own watch flag (uses watchfiles too) — without it, worker code changes need a manual container restart; there's no separate "arq reload" trick. |
| Node/Nodemon-style | `nodemon` or framework's own `--watch` | Same shape as above — check for a built-in watch flag before adding an external watcher. |

For dependency changes (new package in `requirements.txt`/`package.json`), file-watch reload does **not** help — the installed package set doesn't change without a rebuild. If this matters to the user, mention Docker Compose Watch (`develop.watch`, Compose v2.22+/Docker Desktop 4.24+): declarative `sync` for code paths and `action: rebuild` triggered on lockfile changes, invoked via `docker compose watch` (or `up --watch`) instead of plain `up -d`. It's an opt-in addition on top of the bind-mount approach, not a replacement — plain `up -d` still works without it.

## Runtime context: which Docker engine on macOS

On macOS every Docker option is a Linux VM (Docker Desktop, OrbStack, Colima — see `macos-app-cleanup` skill's `references/macos-docker-runtimes.md` for comparison and OrbStack setup/migration). Compose files are engine-agnostic — base+override from this skill work unchanged on any of them. Two engine-dependent notes:

- Bind-mount filesystem speed differs hugely: OrbStack's virtiofs implementation reloads Vite HMR 2–3× faster than Docker Desktop. For vite-in-container dev setups, the runtime choice affects the live-reload experience more than any compose tuning.
- Set the VM memory ceiling from the worst simultaneous stack (sum service `mem_limit`s + ~1 GB VM overhead), not from fear — engines allocate lazily. If a heavy service (e.g. llama.cpp) lives under compose `profiles:`, it doesn't count unless explicitly activated.

## Pitfalls (each one bit someone before you)

- **`pip install` into the app directory gets wiped by the bind mount.** If you `COPY . .` then `pip install -e .` or install into a venv living under `/app`, mounting `./backend:/app` at runtime replaces the whole tree — including the installed packages — with the host copy. Fix: install into the system/global site-packages (`uv pip install --system ...`, or a venv path *outside* `/app`, e.g. `/opt/venv`), so the bind mount only ever overwrites source code, never installed dependencies.
- **`node_modules` bind-mount clobber.** `volumes: [./frontend:/app]` alone replaces `/app/node_modules` (built inside the Linux container image) with whatever is on the host — which is either empty or has macOS-native binaries (esbuild, rollup, etc.) that don't run in the Linux container. Fix: add a named volume mounted specifically at the subpath to "mask" it: `volumes: [./frontend:/app, frontend_node_modules:/app/node_modules]`. Declare `frontend_node_modules` under top-level `volumes:`.
- **`depends_on` without a healthcheck doesn't wait for readiness.** Plain `depends_on: [db]` only waits for the container process to start, not for Postgres/Redis to actually accept connections — migrations or app startup can race and fail with connection-refused. Fix: add `healthcheck:` to `db`/`redis` (`pg_isready -U <user>`, `redis-cli ping`) and use `depends_on: db: {condition: service_healthy}`.
- **Internal vs external ports/hosts mismatch.** If the app's config defaults assume host-published ports (e.g. `DB_PORT=28441` because that's what's exposed to the host), the app *inside* the docker network must instead use the service name and the container's internal port (`DB_HOST=db`, `DB_PORT=5432`). Override via `environment:` in compose — don't hardcode container-network values into the app's own default config, since those defaults are also used for non-Docker local runs.
- **Frontend dev-server → backend URL differs between host-browser and container-network contexts.** A Vite proxy target hardcoded to `http://127.0.0.1:8000` breaks when the frontend runs in a container and needs to reach `api:8000` on the compose network. Make it configurable via an env var with the old default as fallback (`process.env.VITE_API_TARGET ?? 'http://127.0.0.1:8000'`) so non-Docker `npm run dev` keeps working unchanged.
- **Non-root containers on macOS bind mounts are generally fine.** Docker Desktop's VirtioFS/osxfs mapping usually avoids UID/GID permission conflicts between a non-root container user and the host — don't skip `USER app` in Dockerfiles for dev out of unfounded fear of permission errors on macOS. (On a Linux host this can differ and might need `user: "${UID}:${GID}"` — verify rather than assume if the target host is Linux.)
- **Non-root `USER` + named volume on an install-created directory → `EACCES`.** If `npm ci`/`pip install` runs as root and creates a directory (e.g. `node_modules`) *before* the Dockerfile switches to `USER app`, that directory is root-owned in the image layer. A named volume mounted at that exact subpath (e.g. `frontend_node_modules:/app/node_modules`) seeds itself from the image's root-owned content on first `up`, so the non-root process later fails with `EACCES: permission denied, mkdir '/app/node_modules/.vite/...'` (or equivalent). `COPY --chown=app:app . .` does **not** fix this — it only chowns files copied in that instruction, not directories created by earlier `RUN` steps. Fix: end the Dockerfile with `RUN chown -R app:app /app` as the last step before `USER app`, after all installs/copies are done, so the volume seeds with correct ownership.

## Discussion vs. execution — don't jump ahead

Requests to "think through how to implement X" (e.g. "давай подумаем как это реализовать" / "how could we do X, let's think about it") are design discussions, not execution orders — even without an explicit `/plan`. Investigate, propose the plan, and hold off on writing/editing real files until the user explicitly confirms (a bare "давай подумаем" / "let's think" is not confirmation to start editing).

**If you start editing mid-discussion and the user says "I didn't authorize this, roll back":** don't argue, roll back immediately:
1. `git status --porcelain` and `git diff --stat` to see the *actual* current state — don't rely on memory of what you touched.
2. Delete new untracked files; for modified tracked files, `git diff` to confirm no stray changes remain (or `git checkout -- <path>`).
3. Re-run `git status --porcelain` and confirm it's empty before saying anything is rolled back.
4. Only then re-propose the plan and get explicit go-ahead before touching files again.

## Workflow

1. Read the current compose file (if any), Dockerfiles (if any), app entrypoints, and dependency manifests for every service being containerized — you need real paths, real run commands, real port/env conventions before writing anything.
2. Check the CI/CD pipeline as described above — report findings before proposing file changes.
3. Propose the plan (base + override split, which services, which pitfalls apply) and get explicit confirmation before writing files (see "Discussion vs. execution" above).
4. Write Dockerfiles, `.dockerignore`, base compose, override compose, and any small app-config tweaks (env-var fallbacks) needed to make the app dual-mode (container-network aware AND still working for non-Docker local runs).
5. Verify: `docker compose up -d --build`, confirm health via logs/`curl`, then prove live-reload actually works — edit a line in a handler/component and watch the log/browser update without a manual rebuild.
