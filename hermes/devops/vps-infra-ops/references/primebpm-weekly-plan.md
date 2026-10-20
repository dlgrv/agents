# PrimeBPM weekly plan over raw MCP (validated protocol)

The plan lives at `https://primebpm.ru/mcp` (the prime-bpm backend's MCP
endpoint on the main server). Bearer token: read it from
`~/.cursor/mcp.json` (regex `Bearer\s+(...)`) — never echo it into chat.

## Protocol (python urllib works; curl needs `--noproxy '*'` — proxies break this host)
1. POST `initialize` (params: protocolVersion `2024-11-05`, capabilities `{}`, clientInfo) → grab `Mcp-Session-Id` from the RESPONSE HEADERS; cache it (scratch `sid.txt`).
2. POST `notifications/initialized` (no id) with that header.
3. `tools/list`, then `tools/call` with `{name, arguments}` + `Mcp-Session-Id` header.
- Responses come as SSE (`data:` lines) — parse the first `data:` line as JSON, or fall back to plain JSON.
- Sessions expire: `"Session not found"` → re-run initialize and refresh the cached sid before retrying.

## weekly_* tools (scope: the user's personal plan)
- `weekly_list {}` → week window, all tasks with `id`, `name`, `status`
  (todo/done/blocked), dates, permissions. ALWAYS verify a write by re-listing.
- `weekly_create {title, date, end_date?}` → returns task_id.
- `weekly_set_status {task_id, status}` — statuses seen: done / todo / blocked.
- `weekly_move_day`, `weekly_rename`, `weekly_delete` — same `{task_id, ...}` shape; check `tools/list` inputSchema when unsure.

## Conventions
- Close infrastructure tasks only AFTER the change is verified live (handshake
  probes, green heartbeats) — never on intent.
- Tasks the user authored as admin in other projects may be read-only for the
  personal-plan token — hand those to the user to close in the UI.
- When creating a task, pick the date from the work's natural slot in the
  current week and say so; moving it later is one `weekly_move_day` call.
