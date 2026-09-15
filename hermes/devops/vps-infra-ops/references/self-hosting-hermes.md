# Self-hosting the Hermes agent (server «hermes-vm», active)

The agent is a process: skills, sessions, memory, cron live where the process
runs; desktop app and Telegram are only frontends to it. Moving to a server =
moving the process; state travels with it. Recommended geo for a
Telegram-facing box: Amsterdam/Frankfurt (low RTT to Telegram DCs).

## Servers
- **ACTIVE: 178.104.217.93** (DE-датацентр, 2 vCPU), Tailscale IP
  100.93.178.88. SSH aliases: `hermes-vm` (public IP) and `hermes-vm-ts`
  (Tailscale IP) — both in local ~/.ssh/config, key ~/.ssh/hermes, key-only.
  Bot @efaecab_bot. A2A peer over Tailscale (100.93.178.88:9900).
- DECOMMISSIONED: 193.148.253.171 — all hermes services stopped/disabled,
  Linger=no, ports closed, crontab clean, desktop-ssh tokens removed; machine
  and data intact.
- State of truth: the Mac's `~/.hermes` only AT MIGRATION TIME (rsync
  snapshot, strictly one-way — re-syncing the Mac OVER a live server clobbers
  newer server state). Once the Mac desktop is connected via remote gateway,
  the SERVER is the live source of truth: new sessions land there whichever
  frontend (desktop/Telegram) created them.
- Versions must match on both sides (`hermes --version`) — sessions/state
  schema moves with the state files.

## State sync — rsync include filter (validated)
Sync ONLY agent state, never the whole `~/.hermes` (677MB incl. hermes-agent
source, node/, caches vs ~416MB of actual state). Include: config.yaml, .env,
SOUL.md, auth.json, skills/, memories/, sessions/, state.db (+ -wal/-shm),
cron/, platforms/, plans/, desktop-plugins/, hooks/, pets/, plugins/,
mcp-tokens/; everything else `--exclude='*'`.

Pitfalls:
- macOS ships openrsync: `--info=stats2` and other newer flags fail with a
  usage dump; plain `-az --stats --partial` + include rules works.
- Verify by COUNTS, not bytes: `ls skills | wc -l` and the sessions count
  must match on both sides — transfer stats alone prove nothing. The server
  has no sqlite3 CLI: query state.db via the hermes venv python
  (`/usr/local/lib/hermes-agent/venv/bin/python -c "import sqlite3; ..."`).
- Strip local-only env from the server's .env: HTTP(S)_PROXY pointing at the
  local clash proxy (127.0.0.1) does not exist remotely and breaks egress.
- Smoke test with `hermes chat -q ...` and read the FULL output — the reply
  box prints above the session footer, so `| tail -5` cuts it off.

## Telegram gateway (validated, running)
- config.yaml: bot token under platforms.telegram, user's Telegram ID in the
  allowlist. Safe mode denies unknown senders ("Unauthorized user") — after
  allowlist edits restart the gateway.
- Runs as a systemd **user** service `hermes-gateway`; restart with
  `systemctl --user restart hermes-gateway`, and `loginctl enable-linger root`
  so it autostarts without an SSH login session.
- Logs: `journalctl --user -u hermes-gateway --no-pager` plus
  `~/.hermes/logs/gateway.log` / `errors.log`; filter noise first with
  `grep -viE "check_fn|tools.registry"`.
- Healthy startup: "Connected to Telegram (polling mode)" after "polling
  confirmed healthy". DoH fallback-IP discovery and sticky-IPv4 lines from
  the adapter are normal, not errors.

- Session visibility is origin-scoped (IDOR guard): `/sessions` lists only
  sessions of the requester's platform/chat — Telegram won't see the
  desktop-synced sessions, and cross-origin `/resume` is blocked («belongs
  to a different user or chat»). The scoping relaxation lives in config.yaml
  on the server; read the live config (`grep -iE 'origin|visibility'
  ~/.hermes/config.yaml`) instead of assuming a key name.
- Threaded mode is verifiable without the user: Bot API getChat returns
  `has_topics_enabled` / `allows_users_to_create_topics`.

## «Бот не отвечает» checklist (in order)
1. Grep the journal for "Ignoring /start platform ping" — /start is a
   platform ping the gateway deliberately ignores; ask the user to send a
   normal message before debugging anything else.
2. WARNING "Normal final-send NOT suppressed … possible duplicate send"
   means a reply DID go out (content_len=N) — cosmetic warning, not a fault.
3. From the server: `curl -sm 10
   "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"` — pending count
   growing with empty url = poller stuck; 409 Conflict = a second poller
   (e.g. a local gateway still running) is stealing updates.
4. MCP "parked" warnings after failed connects are tool-level (missing
   launcher such as uvx, or connection closed) and unrelated to message
   flow; install the launcher on the server or expect those tools absent.

## Telegram topics (multi-session DM) — user's hands required
One DM = many isolated session-threads. Prereq is a BotFather toggle the
agent cannot perform: @BotFather → /mybots → Bot Settings → Threads Settings
→ Threaded Mode ON (keep «users can create topics» enabled). Then the user
sends `/topic` in the DM to activate: the bot lists old sessions for restore,
`+` adds topics, each topic is an isolated session with its own history, and
topic names follow Hermes session titles. Without topics, `/sessions` +
`/resume` still reach every synced session. Fixed preset workspaces =
`dm_topics` in config.yaml — offer only if the user wants named constant
workspaces instead of free-form topics.

## A2A Mac ↔ server (validated)
- Both ends run a gateway with the A2A platform. Mac side: `A2A_HOST=<own
  Tailscale IP>` + `A2A_PEER_TOKENS` in ~/.hermes/.env, serves an agent card
  as 'hermes-Mac' on :9900. Server side accepts peers listed in its
  `A2A_PEER_TOKENS` as `<peer-name>:<token>`. The caller declares the peer in
  config.yaml (`a2a_agents: <name>: {url: http://100.93.178.88:9900, token}`)
  and sends that token as bearer — the peer name must match the server's
  peer-table key or auth fails.
- Keep the Mac gateway resident with `hermes gateway install` (launchd
  LaunchAgent, autostart at login + restart on crash): A2A inbound silently
  disappears when the gateway only ever ran inside a desktop session.
- Verify pairing BEFORE any cross-agent task: GET the peer's
  /.well-known/agent.json with the bearer token — 200 proves URL+auth in one
  request without spending a model turn.
- HTTP 502 from a2a_call with a HEALTHY agent card = the REMOTE agent's LLM
  stream died (remote journal: "Upstream HTTP/2 stream failed"), not an A2A
  config fault — the adapter surfaces the remote turn's failure as 502.
  Confirm with a direct JSON-RPC `message/send` carrying a SHORT message
  (short turns complete, long turns die), then read the remote journal;
  retry or fix the remote provider. Do not re-edit A2A config.

## Mac network paths (validated)
- The Mac's VPN client (Happ: Tunnel system extension + mihomo) owns the
  default route (utun6) when running — ALL Mac traffic incl. SSH rides it.
  Tailscale is a SEPARATE tunnel (utun7) and keeps working when the VPN
  stops: it re-dials over the direct Wi-Fi path.
- Tailscale IP is the resilient route: SSH via `ssh hermes-vm-ts` and the
  A2A endpoint over 100.93.178.88:9900 were both verified working. Prefer
  the Tailscale alias for Mac→server SSH when the VPN state is uncertain.
- Server-side agent/bot NEVER depend on the Mac's VPN state: Telegram
  polling is server→Telegram outbound.
- Audit connectivity dependencies before assuming one: `route -n get <ip>`
  shows the interface (utun = tunnel); `ping`/`curl` the Tailscale path
  separately from the public path.

## Dashboard / remote gateway (Mac desktop → server, validated)
Connect: Desktop → Settings → Gateways → Remote gateway →
`http://<server>:9119` → Sign in (dlgrv + dashboard password) → name
the connection → optionally set Primary. Desktop and Telegram then share ONE
agent's sessions. Pre-flight from the Mac without the desktop (scripted:
scripts/dashboard_preflight.sh):
1. `GET /` → title "Sign in — Hermes Agent" = auth gate active.
2. API auth is COOKIE-based, NOT HTTP Basic: `-u user:pass` on /api/* still
   returns 401 — never conclude the creds are wrong from that probe alone.
3. Login: `POST /auth/password-login`, JSON `{"provider":"basic", ...}` with
   `-c cookies.txt` → 200 `{"ok":true,"next":"/"}` + `hermes_session_*`
   cookies. Diagnostic map: POST /login = 405; POST /api/auth/login = not a
   route; 422 naming a missing "provider" field = right endpoint, wrong body.
4. `GET /api/sessions?limit=5 -b cookies.txt` → 200 + session JSON = desktop
   sign-in will work with those creds.
Auth routes live in `hermes_cli/dashboard_auth/routes.py` on the server
(`/login` page, `/auth/password-login`, `/auth/native/*`) — grep there when
the desktop login flow changes instead of guessing endpoints.
- Renaming a gateway connection or its SSH key breaks the DESKTOP's
  connection registry, not the server: stale entries in
  `~/Library/Application Support/Hermes/connections.json` keep pointing at
  the old key/URL after the server side is already fixed. Read and clean
  that file whenever connection names or keys change.
