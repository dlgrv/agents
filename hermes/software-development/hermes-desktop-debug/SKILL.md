---
name: hermes-desktop-debug
description: Debug Hermes desktop UI via isolated CDP+MCP.
version: 1
author: dlgrv
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, desktop, electron, cdp, mcp, debugging, ui]
    related_skills: [inspecting-hermes-desktop-dom]
---

# Hermes Desktop Debug — isolated instance + MCP driving

## When to Use

- Debug or reproduce a Hermes **desktop** UI behavior (chat flow, composer,
  edit races, model-switch jank, layout).
- Build or run the debug MCP server (`apps/desktop/mcp/server.mjs`).
- Drive the live renderer from an agent without sending a real message to a real
  LLM or touching the operator's `~/.hermes`.

Do NOT use this for TUI/dashboard work, or any run against the operator's real
`HERMES_HOME`.

Running Hermes desktop against its **real** `~/.hermes` from a debug tool is a
data-leak incident class. Always launch an isolated instance. This skill
captures the verified, working recipe (tested 2026-08-26 on macOS arm64).

## The one rule (fail-closed)

**Never launch a debug instance against the operator's real `~/.hermes`.**
A manual `electron .` with only `HERMES_DESKTOP_USER_DATA_DIR` set silently
falls back to `~/.hermes` as `HERMES_HOME` — the instance then reads real API
keys and WRITES test messages into the real chat history (`state.db`).

The debug MCP server (`apps/desktop/mcp/server.mjs`) enforces this with
`assertTargetAttested(cdp, {expectedHome, defaultHome})` (in `guard.mjs`): every
consequential tool — read AND act/flow — reads the **realized** target's data
root from a per-instance descriptor (`globalThis.__DEBUG_MCP_INSTANCE__`, emitted
by the Electron main process into the renderer at `did-finish-load`) and REFUSES
unless it matches `DESKTOP_DEBUG_MCP_EXPECTED_HOME`. This is *target-derived
authority*, not a caller declaration: a real Desktop on `~/.hermes` cannot be
reached by declaring a fake `EXPECTED_HOME`. See `references/isolation-guard.md`
for the full design, the P1 reviewer blockers, and the residual risk.

## Verified isolated-launch recipe (macOS)

```bash
# 1. isolated home + mock provider config
mkdir -p /tmp/hermes-debug-home
cat > /tmp/hermes-debug-home/config.yaml <<'YAML'
model: { default: mock-model, provider: mock }
providers:
  mock: { api: http://127.0.0.1:53999/v1, name: Mock, api_mode: chat_completions,
          key_env: MOCK_API_KEY, models: { mock-model: {} }, context_length: 4096 }
YAML
echo "MOCK_API_KEY=debug" > /tmp/hermes-debug-home/.env

# 2. (separate process) mock inference server on 53999 returning SSE chunks
#    (any OpenAI-compatible /v1/chat/completions streamer works)
# 3. (separate process) vite renderer
cd apps/desktop && ( npm run dev:renderer & )   # http://127.0.0.1:5174
# 4. electron against isolated home, with CDP port, SEPARATE user-data-dir
HERMES_HOME=/tmp/hermes-debug-home \
HERMES_DESKTOP_PYTHON=<repo>/.venv/bin/python \
HERMES_DESKTOP_CDP_PORT=9333 \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_USER_DATA_DIR=/tmp/cdp-probe-userdata \
HERMES_DESKTOP_IGNORE_EXISTING=1 \
  <repo>/apps/desktop/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron . \
  --user-data-dir=/tmp/cdp-probe-userdata
```

Then start the MCP server declaring the same home:
```bash
cd apps/desktop/mcp && npm install
DESKTOP_DEBUG_MCP_ALLOW_ACT=1 \
DESKTOP_DEBUG_MCP_EXPECTED_HOME=/tmp/hermes-debug-home \
DESKTOP_DEBUG_MCP_PORT=9333 \
  node server.mjs
```

## Gotchas (all hit and resolved 2026-08-26)

- **CDP port only opens for dev-server runs.** `electron dev-cdp.ts` closes the
  port unless `HERMES_DESKTOP_DEV_SERVER` is set AND the build isn't treating
  itself as packaged. Use the `npm run dev:renderer` + explicit `Electron .`
  form above (NOT `npm run dev` concurrently — its vite child dies on a
  port-5174 clash and SIGTERMs electron before CDP binds). Pass
  `HERMES_DESKTOP_DEV_SERVER` even when launching electron manually.
- **`findElectron()` in `scripts/dev-mock.mjs` is Linux-only** — looks for
  `dist/electron`, missing the macOS `Electron.app/Contents/MacOS/Electron`.
  `npm run dev:mock` therefore fails on macOS. Launch manually per recipe above.
- **`ui_type` MUST use `Input.insertText`, not `dispatchKeyEvent` with
  `type:'char'`.** A contentEditable composer (rich-editor.ts) relies on the
  browser's native `beforeinput`→`insertText` pipeline; synthetic `char`
  keydown events never produce a real `beforeinput` with inputType
  `'insertText'`, so the text silently fails to land (composer shows empty).
  `Input.insertText({text})` drives the correct pipeline and the React-controlled
  editor receives the characters. `ui_press` sends `commands:['Enter']` AND
  focuses the composer first — React ignores synthetic `dispatchEvent` Enter,
  so a real CDP Input key event is required for submit.
- **`ui_screenshot` is read-only and returns image content** — it does NOT
  write to disk (a caller-supplied `path` was an arbitrary-file-write, the P1-2
  blocker). Persist the returned `image` bytes yourself if you need a file.
  spawns `hermes` gateway which dies with `ModuleNotFoundError: No module
  named 'yaml'`. Fix: `uv venv .venv && uv pip install -e .` in repo root,
  point `HERMES_DESKTOP_PYTHON` at `.venv/bin/python`. Or use the installed
  Hermes venv (`~/.hermes/hermes-agent/venv/bin/python`) if its deps match.
- **`build/install-stamp.json` required** before `npm run dev` / electron main
  boots: `node scripts/write-build-stamp.mjs`.
- **`electron` not on PATH** when launched from agent shell — use the absolute
  binary path under `node_modules/electron/dist/Electron.app/...`.
- **Single-instance lock**: if your real Hermes desktop is running, the debug
  electron exits immediately unless `--user-data-dir` differs from the live
  one. Always pass a unique `--user-data-dir`.

## MCP tools surface (`apps/desktop/mcp`)

Read-only: `desktop_ui_status`, `ui_inspect`, `ui_query`, `ui_console`,
`ui_screenshot`. Gated by `DESKTOP_DEBUG_MCP_ALLOW_ACT=1` + expected-home:
`ui_click`/`ui_type`/`ui_press` (real CDP Input events — blur/focus races
reproduce like a human), `ui_eval` (bounded JS), `ui_flow_edit`
(reproduces chat-edit silent-fail races: hover→edit→type→Enter→structured
report), `ui_flow_model_switch` (MutationObserver over thread for layout jank).

Server reuses `scripts/perf/lib/cdp.mjs` (stable `SELECTORS`, one CDP client).
Outputs are bounded (≤20 nodes, ≤80-char snippets, ≤4KB eval).

### Isolation architecture (post P1-home-authority, 2026-08-27)

The descriptor chain is now: `resolveHermesHomeFromInputs()` in
`electron/hermes-home.ts` (pure, every input injected — env, platform, appHome,
userDataOverride, registry/fs deps, `pathModule`) → `main.ts` thin adapter →
`resolveDevCdpInstance({ resolvedHermesHome })` → descriptor. dev-cdp.ts must
NEVER read env for the root itself. Cross-platform gotcha found while testing:
`path.join` on macOS mangles Windows paths, so the resolver injects
`pathModule` (and passes it through to `normalizeHermesHomeRoot`) — Windows
test cases use `path.win32` + win-style `appHome`.

### Module layout (post hardening pass, 2026-08-27)

`server.mjs` is pure MCP wiring — logic lives in modules (same layout as
`tools/act.mjs` / `tools/flows.mjs`); extend the module, not the entry point:

- `dispatch.mjs` — tool dispatch + `wrapResult`. **`wrapResult` passes
  pre-formed `{content:[...]}` through verbatim** — a tool returning MCP image
  content (screenshot) must not be JSON-stringified, or the image block is lost
  (locked by `dispatch.test.mjs`).
- `cdp-client.mjs` — connection lifecycle via `createCdpClient()` (thin wrapper
  over perf `cdp.mjs`): handle resets to `null` on failure, `invalidate()`
  clears closed sockets; `isConnectablePage` predicate shared by status() and
  the client so they never disagree about "alive" (`cdp-client.test.mjs`).
  **Socket close auto-invalidates**: `connect()` subscribes to the handle's
  `ws` close event with an identity guard (`thisHandle`) so a stale socket's
  late close can't null a newer handle — without this, a renderer reload
  poisoned the cached handle until server restart. Test fakes must store close
  listeners PER-SOCKET (a fake keeping only the latest listeners fires the
  fresh socket's close when you meant the stale one — bit once).
- `guard.mjs` — isolation is TWO independent policies, not one: (1) protected
  home refusal — realized home equal to the server's `defaultHome` or the OS
  user's `~/.hermes` is REFUSED even when `expectedHome === realized`
  ("agreement is not permission"; guard.mjs previously read `defaultHome` but
  never used it); (2) identity match to `EXPECTED_HOME`. The descriptor's
  `dataRoot` must come from the SINGLE home authority (`electron/hermes-home.ts`,
  extracted from main.ts as a pure injected-input function) — dev-cdp.ts
  re-deriving home from env alone attested the wrong root on
  `HERMES_DESKTOP_USER_DATA_DIR`-only sandbox launches (P1, review round 3).
  Never prove protected-home refusal with a live real-home instance — unit
  tests only.
- `desktop_ui_status` is a deliberate PREFLIGHT: it bypasses connect+attestation
  (early branch in `dispatch.mjs`) so `cdpAlive:false` is reachable; every
  other tool still attests. Negative test pins that `ui_inspect` under dead-CDP
  deps still refuses.
- `tools/read.mjs` — `createReadTools()`: status/inspect/query/consoleLog/
  screenshot/evalBounded (`tools/read.test.mjs`). Gotchas locked by tests:
  `query` `limit:0` falls back to the node cap (not 0 nodes); the whitespace
  regex inside the template-literal eval string must stay double-escaped
  (`/\\s+/g` in source → `/\s+/g` in the sent expression — a single-escape
  variant silently becomes `/s+/g`); empty/whitespace selector throws friendly
  error before eval (`requireSelector`, also applied by act click/type);
  `evalBounded` truncation reports the cut length and survives an `undefined`
  eval result (`JSON.stringify(undefined)` is `undefined` → `?? 'null'`).
- `scripts/perf/lib/cdp.mjs` `send()` has a 15s default timeout (rejects,
  cleans the pending entry, ignores late responses) and `eval()` uses
  `r.result?.value` (malformed responses resolve undefined, not TypeError)
  — a hung renderer can no longer block a tool call forever (`cdp.test.mjs`).

Test suite: 59 (54 mcp + 5 cdp). Run: `node --test *.test.mjs tools/*.test.mjs`.

## Repo layout facts

- Fork: `~/github/hermes-agent` (origin=dlgrv, upstream=NousResearch). Work on
  branch `feat/desktop-debug-mcp`. Issue #95489 proposes this server upstream
  (status OPEN, `needs-decision` on in-repo vs standalone placement).
- Debug module `src/debug/` + `scripts/diag-*.mjs` exist (render/atom churn,
  perf harness) — sibling tooling, good prior art before adding MCP flows.
- Desktop AGENTS.md: renderer never reaches Node; `process.env` NOT visible in
  the renderer. The server therefore cannot read the target's `HERMES_HOME`
  from a renderer global — but the **Electron main process** emits the descriptor
  (`resolveDevCdpInstance` → `globalThis.__DEBUG_MCP_INSTANCE__` via
  `executeJavaScript` at `did-finish-load`), so the server reads it from the
  realized target. Design history in `references/isolation-guard.md`.

## See also

- `references/isolated-launch.sh` — copy-ready launch script.
- Upstream proposal context in plan file
  `~/.hermes/plans/2026-08-26_134500-desktop-debug-mcp.md`.
