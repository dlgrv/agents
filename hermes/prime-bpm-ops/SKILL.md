---
name: prime-bpm-ops
description: Use when working on primebpm.ru or the prime-bpm repo.
---

# prime-bpm operations (primebpm.ru)

Production: server `web-main` (109.236.57.134, SSH as `ldolgirev`, sudo needs password — Leonid runs root commands himself). Backend: systemd `bpm-api.service`, env in `/opt/prime-bpm/backend/.env`, deployed SHA in `/opt/prime-bpm/DEPLOYED_SHA`. Local repo: `~/work/prime-bpm`, origin `https://primegit.ru/prime-web/prime-bpm` (default branch `master`, no `main`). The repo-local git config pins `http.proxy = http://127.0.0.1:17890` (clash), which breaks fetch/pull to primegit.ru with `SSL_ERROR_SYSCALL` — override per-command: `git -c http.proxy= fetch origin` / `git -c http.proxy= pull`. Work infra inventory: `~/work/infra/docs/inventory.md` (servers A–F + NAS). Git to primegit.ru must bypass proxy env vars.

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

**Naming convention (set 2026-10-23, branch `feat/primebpm-00-mcp-roadmap-tools`, NOT yet deployed):** tools are `<domain>_<verb>_<object>`, verb-first, self-documenting for LLMs: `weekly_list_tasks/create_task/set_task_status/move_task_to_day/rename_task/delete_task` + `roadmap_get_structure/list_tasks/create_task/move_task_to_step/rename_task/delete_task`. Roadmap mutations require PAT scope `roadmap:tasks` (generic `<domain>:<resource>` matching in `api_tokens.py`, not the old hardcoded weekly-only list); cross-project/cross-roadmap moves are rejected. Until this deploys, prod still exposes the 6 old-named weekly tools (`weekly_list` etc.) and zero roadmap tools — after deploy, update this skill's tool names. `docs/mcp.md` + `tests/docs/test_mcp_md_contract.py` pin all tool names and scopes — a rename must touch doc + contract test together.

## Weekly-plan tools

`weekly_list` takes argument `week: "YYYY-MM-DD"` (a week start date) — NOT `week_start`; a wrong key is silently ignored and returns the current week. `weekly_move_day(task_id, date)`, `weekly_set_status(task_id, status)` (`todo|done|blocked`), `weekly_create(title, date, end_date?, kind?)`. Roadmap-sourced tasks (`source: roadmap`, author `admin`) often CANNOT be moved via `weekly_move_day` even when the task object says `can_move: true` — check the response `isError`, and fall back to telling Leonid to move them in the web UI. A "blocked" dependency chain: closing the root blocker does NOT auto-unblock children — statuses must be flipped individually.

NEVER use `weekly_create` for Leonid's work items: his work tasks live in the roadmap's «прочие задачи» per project, and anything entered in the personal weekly plan does not appear there — his manager sees the roadmap lists, not his personal board. If a `tools/list` shows no roadmap tools (pre-deploy), say the capability is missing instead of shoving the task into the weekly plan; once deployed, use `roadmap_create_task` (project + step required) instead.

## Testing conventions (backend)

TDD RED→GREEN, full suite before done. `Manager` is a singleton: tests must never overwrite its attributes directly — use `monkeypatch`, or overrides leak into every later test in the run. `app/mcp` is held at 100% coverage (argued with `--cov=app.mcp`, not by eye). Known legacy baseline on master: `tests/` full run gives ~15 collection errors (missing `app.main`, `app.managers.otk/reports/tables`, stale local Postgres volume without `users.access_id`) and some tests need the compose db (`docker compose up -d db`, then stop it) — these are pre-existing, prove your diff clean by comparing error counts against a stash-baseline. Style: `bash scripts/check-backend-style.sh` must pass.

## Pitfalls

- NEVER put a literal URL inside a shell command you hand to Leonid to paste: his chat client wraps URLs as `` @url:`https://...` `` and he pastes it verbatim, corrupting the file/command. Build commands so the URL appears only in output, or include a strip step: `sed 's|@url:`\([^`]*\)`|\1|'`.
- Don't trust `git pull` on a work server dir blind: check `DEPLOYED_SHA` matches `origin/master` head before diagnosing version-dependent behavior.
- Fleet/server-park operations (firewall, fail2ban, WireGuard mesh, Kuma instances, sudoers, the A–F + NAS hosts) have their own runbook: see `references/work-infra-fleet.md`. Read the inventory (`~/work/infra/docs/inventory.md`) before touching any work server, and update it after any topology change.
