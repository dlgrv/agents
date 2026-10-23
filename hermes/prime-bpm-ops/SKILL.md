---
name: prime-bpm-ops
description: Use when working on primebpm.ru or the prime-bpm repo.
---

# prime-bpm operations (primebpm.ru)

Production: server `web-main` (109.236.57.134, SSH as `ldolgirev`, sudo needs password — Leonid runs root commands himself). Backend: systemd `bpm-api.service`, env in `/opt/prime-bpm/backend/.env`, deployed SHA in `/opt/prime-bpm/DEPLOYED_SHA`. Local repo: `~/work/prime-bpm`, origin `https://primegit.ru/prime-web/prime-bpm` (default branch `master`, no `main`). The repo-local git config pins `http.proxy = http://127.0.0.1:17890` (clash), which breaks fetch/pull to primegit.ru with `SSL_ERROR_SYSCALL` — override per-command: `git -c http.proxy= fetch origin` / `git -c http.proxy= pull`. Work infra inventory: `~/work/infra/docs/inventory.md` (servers A–F + NAS). Git to primegit.ru must bypass proxies: the repo has a LOCAL `http.proxy=127.0.0.1:17890` (clash) config that BREAKS fetch — use `git -c http.proxy= -c https.proxy= <cmd>` (direct works; primegit → 109.236.57.134).

**Deploy = GitLab CI, not manual SSH.** MR → squash-merge to master (API: `PUT .../merge_requests/:iid/merge?squash=true`; token via `git credential fill` for primegit.ru). Pipeline: test-backend/test-frontend → build → `deploy-prod` is a **manual** job — play via API `POST /projects/prime-web%2Fprime-bpm/jobs/:id/play` (job id from `pipelines/:id/jobs`), runs ~1 min. No server-side git pull/systemctl needed.

Flow for a change: branch → commit (pre-commit must pass) → create MR from push options `git -c http.proxy= push -u origin <branch> -o merge_request.create -o merge_request.target=master -o merge_request.remove_source_branch` → squash-merge via the API above → sync local master (`fetch`, `checkout master`, `merge --ff-only` — the checkout matters: committing leaves you on the feature branch and the next ff-merge fails confusingly) → poll pipeline status until `manual` → play the deploy job. Post-deploy smoke: raw `tools/list` (current tool count + names) for backend changes; for frontend, grep the JS bundle linked from `https://primebpm.ru/` (`assets/*.js`) for a string only the new build contains.

## Procedure: talk to the MCP endpoint raw (no Cursor needed)

Streamable HTTP at `https://primebpm.ru/mcp`, Bearer PAT. Session-based — every call is a 3-step dance:

1. `initialize` with `Accept: application/json, text/event-stream`, capture `Mcp-Session-Id` response header (`curl -D headers.txt`).
2. POST `notifications/initialized` with that header.
3. POST `tools/call` / `tools/list` with `Mcp-Session-Id: <sid>`.

Always pass curl `--max-time 15` (streamable HTTP keeps the connection open after a response — without the timeout curl hangs) and `--noproxy '*'` (local proxies interfere with the SSE handshake).

Sessions expire (server restart / idle): a mid-work `Session not found` means re-run the initialize dance and swap in the fresh `Mcp-Session-Id` — do not retry the old sid. Caching the sid in the scratch dir between calls is fine, but expect to re-initialize at least once per session.

PAT lives in `~/.cursor/mcp.json` under `mcpServers.primebpm.headers.Authorization` — read it from there, update it there when Leonid sends a new token.

Status-by-response cheat sheet:
- `503 {"ok":false,"msg":"MCP disabled"}` → env gate off; comes BEFORE auth check, so a bad/expired token still gives this, not 401.
- `401 Unauthorized` (plain text) → endpoint on, token unknown/revoked/expired.
- `Missing session ID` → you skipped the initialize/session dance, not an auth problem.

## Enable-gate (why "MCP disabled")

`backend/app/mcp/policy.py::enabled()` requires, in production: `MCP_ENABLED=1` AND non-empty valid `MCP_ALLOWED_HOSTS` AND `MCP_ALLOWED_ORIGINS` in `.env` + `systemctl restart bpm-api.service`. One invalid entry makes the whole list empty → disabled. Expected values: `MCP_ALLOWED_HOSTS=primebpm.ru`, `MCP_ALLOWED_ORIGINS=https://primebpm.ru`.

## PAT lifecycle

Tokens are `bpm_*`, stored hash-only (`sha256(raw)` in `api_tokens` table, model `backend/app/database/models/auth.py`). Revoked/expired = plain 401. To check a token server-side: hash it and query `api_tokens` by `token_hash`. Mint new ones via UI or `backend/scripts/smoke_mcp.py` (login → CSRF → PAT → initialize → tools/list).

## Extending the MCP toolset

The tool inventory is hardcoded in `server.py` (`register_weekly_tools` + `register_roadmap_tools`). Answer "can MCP do X" from a live `tools/list`, never from memory or this skill — locally written but undeployed tools don't show until the prod restart. Touchpoints for adding a tool category, plus the scope pitfalls, are in `references/mcp-tools-extending.md`.

**Naming convention (deployed to prod):** tools are `<domain>_<verb>_<object>`, verb-first, self-documenting for LLMs: `weekly_list_tasks/create_task/set_task_status/move_task_to_day/rename_task/delete_task` + `roadmap_get_structure/list_tasks/create_task/move_task_to_step/rename_task/delete_task`. Roadmap mutations require PAT scope `roadmap:tasks` (generic `<domain>:<resource>` matching in `api_tokens.py`, not the old hardcoded weekly-only list); cross-project/cross-roadmap moves are rejected. Until this deploys, prod still exposes the 6 old-named weekly tools (`weekly_list` etc.) and zero roadmap tools — after deploy, update this skill's tool names. `docs/mcp.md` + `tests/docs/test_mcp_md_contract.py` pin all tool names and scopes — a rename must touch doc + contract test together.

## Tools (12 in prod; old short weekly_* names are gone — trust a live `tools/list` over this list if versions drift)

Weekly (scope `weekly_plan:personal`): `weekly_list_tasks(week="YYYY-MM-DD" opt)` — a wrong key is silently ignored and returns the current week. `weekly_create_task(title, date, end_date?, kind?)`, `weekly_set_task_status(task_id, todo|done|blocked)`, `weekly_move_task_to_day(task_id, date)`, `weekly_rename_task(task_id, name)`, `weekly_delete_task(task_id)`.

Roadmap (scope `roadmap:tasks`; mint a PAT with BOTH scopes — via the /profile UI, which now has scope checkboxes (both on by default), or `POST /api/v1/tokens` with `scopes: ["weekly_plan:personal","roadmap:tasks"]`. Any token minted through the UI BEFORE the checkbox deploy silently lacks `roadmap:tasks` — a token where weekly works but roadmap denies means missing scope, not a broken endpoint): `roadmap_get_structure(project_id?)` — phases/steps, source of exact `phase`/`step` names and `step_id`; `roadmap_list_tasks(project_id?)` — uuid + names + status + owner + dates; `roadmap_create_task(title, phase, step, project_id?, assignee?, status?, end_date?)`; `roadmap_move_task_to_step(task_id, step_id, position?)` — same-project only, enforced; `roadmap_rename_task(task_id, name)`; `roadmap_delete_task(phase, step, task, project_id?)` — archives the task. Workflow: get names/ids from get_structure/list_tasks, then mutate.

**Routing rule (boss's directive 2026-10-23): work/licensing tasks go into the ROADMAP (`roadmap_create_task`), NOT the personal weekly plan. Personal plan only for genuinely personal items.**

Quirks: roadmap-sourced tasks on the weekly board often CANNOT be moved via `weekly_move_task_to_day` even when `can_move: true` — use `roadmap_move_task_to_step`. A "blocked" dependency chain: closing the root blocker does NOT auto-unblock children — statuses flip individually.

NEVER use `weekly_create` for Leonid's work items: his work tasks live in the roadmap's «прочие задачи» per project, and anything entered in the personal weekly plan does not appear there — his manager sees the roadmap lists, not his personal board. If a `tools/list` shows no roadmap tools, the token most likely lacks `roadmap:tasks` (or the deploy is stale) — report that instead of shoving the task into the weekly plan. Use `roadmap_create_task` (project + step required) for work items.

## Testing conventions (backend)

TDD RED→GREEN, full suite before done. `Manager` is a singleton: tests must never overwrite its attributes directly — use `monkeypatch`, or overrides leak into every later test in the run. `app/mcp` is held at 100% coverage (argued with `--cov=app.mcp`, not by eye). Known legacy baseline on master: `tests/` full run gives ~15 collection errors (missing `app.main`, `app.managers.otk/reports/tables`, stale local Postgres volume without `users.access_id`) and some tests need the compose db (`docker compose up -d db`, then stop it) — these are pre-existing, prove your diff clean by comparing error counts against a stash-baseline (move NEW untracked test files aside during the stash run, or their missing fixtures will poison the baseline). Style: `bash scripts/check-backend-style.sh` must pass. The MCP SDK wraps tool exceptions as `Error executing tool …` — tests must assert on that masked contract, not the original error text.

## Commit gates (repo pre-commit + LOC allowlist)

`scripts/file-loc-allowlist.json` forbids growing legacy files past their recorded LOC. The prescribed fix for an oversized file is NOT an allowlist bump: split it to <400 LOC and DELETE its entry in the SAME commit — the gate verifies the removal condition, and a split without entry removal fails. The pre-commit black version differs from the venv's and may flag format-debt in legacy files OUTSIDE your commit: check whether the offender is in your staged set; if not, apply the hook's formatting only to your files — never reformat unrelated legacy inside a feature PR. After a `git pull`, reinstall frontend deps before `npm run check` — vitest fails on missing transitive deps (e.g. unified/remark-parse) from a stale `node_modules`. Frontend suite: `npx vitest run`; full gate: `npm run check`.

## Pitfalls

- NEVER put a literal URL inside a shell command you hand to Leonid to paste: his chat client wraps URLs as `` @url:`https://...` `` and he pastes it verbatim, corrupting the file/command. Build commands so the URL appears only in output, or include a strip step: `sed 's|@url:`\([^`]*\)`|\1|'`.
- Don't trust `git pull` on a work server dir blind: check `DEPLOYED_SHA` matches `origin/master` head before diagnosing version-dependent behavior.
- Fleet/server-park operations (firewall, fail2ban, WireGuard mesh, Kuma instances, sudoers, the A–F + NAS hosts) have their own runbook: see `references/work-infra-fleet.md`. Read the inventory (`~/work/infra/docs/inventory.md`) before touching any work server, and update it after any topology change.
