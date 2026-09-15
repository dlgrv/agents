# Isolated Hermes desktop debug instance (verified recipe)

Goal: a drivable, editable, mock-backed Electron instance with CDP open — that
touches NONE of the user's real data (`~/.hermes`).

## Why isolation fails (the trap)

`HERMES_DESKTOP_USER_DATA_DIR` != `HERMES_HOME`.
- `HERMES_DESKTOP_USER_DATA_DIR` = Chromium profile only (window state, cache).
- `HERMES_HOME` = data dir: `config.yaml`, provider API keys, and the whole
  chat DB (`state.db`, `state.db-wal`, `sessions` + `messages` tables).

If `HERMES_HOME` is unset, Hermes resolves it via `hermes_constants.get_default_hermes_root()`
-> `~/.hermes` (POSIX). The debug instance then **reads the user's real keys and
writes test chatter into their real history.** Always set `HERMES_HOME` to a
throwaway dir.

## Prereqs (one-time, in the checkout)

```bash
cd ~/github/hermes-agent
uv venv .venv
uv pip install -e .          # hermes + deps incl. pyyaml  -> backend can boot
cd apps/desktop && npm run build   # writes dist/index.html + dist/electron-main.mjs
```

Without the venv the backend exits (`ModuleNotFoundError: No module named 'yaml'`)
and the composer renders `contentEditable=false` (disabled).

## The command (vite + dev electron; CDP opens because DEV_SERVER is set)

Terminal 1 — renderer only (HTTP, no window):
```bash
cd ~/github/hermes-agent/apps/desktop && npm run dev:renderer   # vite :5174
```

Terminal 2 — electron (FOREGROUND; opens a VISIBLE window — WARN THE USER first):
```bash
cd ~/github/hermes-agent/apps/desktop
HERMES_HOME=/tmp/hermes-debug-home \
HERMES_DESKTOP_PYTHON=$PWD/../../.venv/bin/python \
HERMES_DESKTOP_CDP_PORT=9333 \
XCURSOR_SIZE=24 \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_USER_DATA_DIR=/tmp/cdp-probe-userdata \
HERMES_DESKTOP_IGNORE_EXISTING=1 \
node_modules/electron/dist/Electron.app/Contents/MacOS/Electron . \
  --user-data-dir=/tmp/cdp-probe-userdata
```

Notes:
- `HERMES_HOME` MUST be a throwaway dir — this is the isolation guarantee.
- `npm run dev` (concurrently dev:renderer + dev:electron) is equivalent but
  collides if a vite already holds :5174; kill stray vite first.
- `npm run dev:mock` launches the **packaged dist** electron -> `dev-cdp.ts` keeps
  the CDP port closed regardless of `HERMES_DESKTOP_CDP_PORT`. Do NOT use it for
  CDP work.

Poll after ~20s: `curl -s --max-time 3 http://127.0.0.1:9333/json/version`.

## Verify the instance is actually isolated

After launch, confirm it is NOT touching `~/.hermes`:
```bash
ls -la /tmp/hermes-debug-home            # config.yaml + .env were written here
grep -a "MARKER_TEXT" ~/.hermes/state.db 2>/dev/null && \
  echo "CONTAMINATION — instance wrote to real DB" || echo "clean: real DB untouched"
```

## Cleanup of a contamination (if HERMES_HOME was ever omitted)

A debug instance without `HERMES_HOME` wrote a test session into `~/.hermes/state.db`.
Find and remove ONLY that session — never restore from an old `.bak` (that would
drop the user's real sessions created since the backup).

```bash
cd ~/.hermes
python3 - <<'PY'
import sqlite3
con = sqlite3.connect('state.db'); con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("SELECT session_id, substr(content,1,60) FROM messages "
            "WHERE content LIKE '%MARKER_TEXT%' ORDER BY id DESC")
rows = cur.fetchall()
for r in rows: print(r['session_id'], r['content'])
# then: DELETE FROM messages WHERE session_id=?; DELETE FROM sessions WHERE id=?;
PY
```
Replace `MARKER_TEXT` with the literal text sent during the test. Do this only
after showing the user the matched `session_id` and confirming.

## MCP server port mismatch

The Desktop Debug MCP server (`apps/desktop/mcp/server.mjs`) defaults to CDP
port 9222. When the instance runs on 9333, run the server with
`DESKTOP_DEBUG_MCP_PORT=9333` (and `DESKTOP_DEBUG_MCP_ALLOW_ACT=1` for click/type).
`connect()` is established per request in act/flow handlers — pass the live port
env so `ui_flow_edit` / `ui_click` get a live `cdp` handle.
