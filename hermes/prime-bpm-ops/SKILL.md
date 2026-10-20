---
name: prime-bpm-ops
description: Use when working on primebpm.ru or the prime-bpm repo.
---

# prime-bpm operations (primebpm.ru)

Production: server `web-main` (109.236.57.134, SSH as `ldolgirev`, sudo needs password — Leonid runs root commands himself). Backend: systemd `bpm-api.service`, env in `/opt/prime-bpm/backend/.env`, deployed SHA in `/opt/prime-bpm/DEPLOYED_SHA`. Local repo: `~/work/prime-bpm`, origin `https://primegit.ru/prime-web/prime-bpm` (default branch `master`, no `main`). Work infra inventory: `~/work/infra/docs/inventory.md` (servers A–F + NAS). Git to primegit.ru must bypass proxy env vars.

## Procedure: talk to the MCP endpoint raw (no Cursor needed)

Streamable HTTP at `https://primebpm.ru/mcp`, Bearer PAT. Session-based — every call is a 3-step dance:

1. `initialize` with `Accept: application/json, text/event-stream`, capture `Mcp-Session-Id` response header (`curl -D headers.txt`).
2. POST `notifications/initialized` with that header.
3. POST `tools/call` / `tools/list` with `Mcp-Session-Id: <sid>`.

PAT lives in `~/.cursor/mcp.json` under `mcpServers.primebpm.headers.Authorization` — read it from there, update it there when Leonid sends a new token.

Status-by-response cheat sheet:
- `503 {"ok":false,"msg":"MCP disabled"}` → env gate off; comes BEFORE auth check, so a bad/expired token still gives this, not 401.
- `401 Unauthorized` (plain text) → endpoint on, token unknown/revoked/expired.
- `Missing session ID` → you skipped the initialize/session dance, not an auth problem.

## Enable-gate (why "MCP disabled")

`backend/app/mcp/policy.py::enabled()` requires, in production: `MCP_ENABLED=1` AND non-empty valid `MCP_ALLOWED_HOSTS` AND `MCP_ALLOWED_ORIGINS` in `.env` + `systemctl restart bpm-api.service`. One invalid entry makes the whole list empty → disabled. Expected values: `MCP_ALLOWED_HOSTS=primebpm.ru`, `MCP_ALLOWED_ORIGINS=https://primebpm.ru`.

## PAT lifecycle

Tokens are `bpm_*`, stored hash-only (`sha256(raw)` in `api_tokens` table, model `backend/app/database/models/auth.py`). Revoked/expired = plain 401. To check a token server-side: hash it and query `api_tokens` by `token_hash`. Mint new ones via UI or `backend/scripts/smoke_mcp.py` (login → CSRF → PAT → initialize → tools/list).

## Weekly-plan tools

`weekly_list` takes argument `week: "YYYY-MM-DD"` (a week start date) — NOT `week_start`; a wrong key is silently ignored and returns the current week. `weekly_move_day(task_id, date)`, `weekly_set_status(task_id, status)` (`todo|done|blocked`), `weekly_create(title, date, end_date?, kind?)`. Roadmap-sourced tasks (`source: roadmap`, author `admin`) often CANNOT be moved via `weekly_move_day` even when the task object says `can_move: true` — check the response `isError`, and fall back to telling Leonid to move them in the web UI. A "blocked" dependency chain: closing the root blocker does NOT auto-unblock children — statuses must be flipped individually.

## Pitfalls

- NEVER put a literal URL inside a shell command you hand to Leonid to paste: his chat client wraps URLs as `` @url:`https://...` `` and he pastes it verbatim, corrupting the file/command. Build commands so the URL appears only in output, or include a strip step: `sed 's|@url:`\([^`]*\)`|\1|'`.
- Don't trust `git pull` on a work server dir blind: check `DEPLOYED_SHA` matches `origin/master` head before diagnosing version-dependent behavior.
