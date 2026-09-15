---
name: hermes-desktop-ui-debugging
description: "Drive the Hermes desktop UI over CDP with a mock backend."
version: 1.0.0
author: dlgrv
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [desktop, electron, cdp, mock-backend, mcp, ui-debugging, hermes-agent]
    related_skills: [inspecting-hermes-desktop-dom, systematic-debugging]
---

# Debugging / driving the Hermes desktop UI

The bundled `inspecting-hermes-desktop-dom` skill covers *reading* the live DOM
over CDP. This skill covers the other half: **driving** it (click, type,
submit) and **reproducing UI bugs** — which needs a backend, and which the
read-only skill deliberately leaves out. It also documents the Desktop Debug
MCP server (native LLM-agent tools for the same job).

## ⚠️ ISOLATION IS MANDATORY — never debug against the user's real home

A debug instance MUST run against an isolated `HERMES_HOME`. If you set
`HERMES_DESKTOP_USER_DATA_DIR` (the Chromium profile) but NOT `HERMES_HOME`,
the instance silently falls back to `~/.hermes` — reading the user's real API
keys and chat history, and **writing** into their real `state.db`. This
happened in the 2026-08-26 incident: a manual `electron .` launch with only
`HERMES_DESKTOP_USER_DATA_DIR` set leaked a test message into the user's
production `state.db`.

Rule, non-negotiable:
- Always launch with `HERMES_HOME=/tmp/<sandbox>` plus its own mock
  `config.yaml` (see `references/isolated-launch.md` for the exact recipe).
- If you run the Debug MCP server with mutating tools, you MUST also set
  `DESKTOP_DEBUG_MCP_EXPECTED_HOME=/tmp/<sandbox>` to match. The server is
  **fail-closed**: without it (or if it equals the default home), every
  `ui_click`/`ui_type`/`ui_press`/`ui_flow_*` call returns `REFUSED`.
- Never point a debug instance at `~/.hermes`, even "just to read".

## When to use

- You must type into / submit from the composer in a test instance.
- You're reproducing the known chat-edit silent-fail races. **Re-verify before
  acting** (see Pitfalls): a compacted session may cite a stale file:line. On
  current `upstream/main` the `editMessage` action
  (`apps/desktop/src/app/chat/session-tile-actions.ts:~576`) already catches and
  calls `notifyError(err, copy.editFailed)` — the "empty catch swallowing
  Composer is not available" variant is **already fixed**. The inline
  edit-composer UI itself lives inside the external `assistant-ui` `Thread`
  component (not in our tree), so a blur-cancel race there is not fixable in
  `apps/desktop`. The reproducible part for our repo is the `submitRewind`/edit
  action path + the model-switch layout shift.
- You're building or running the `apps/desktop/mcp/` Desktop Debug MCP server.
- `npm run dev:mock` produced a blank window or a non-editable composer.

## The backend is the whole game

A throwaway `HERMES_HOME` with no Python backend renders the composer
`contentEditable=false`. You can `ui_type` into it all day; nothing is editable
and Enter will not submit. The symptom is a **disabled composer**, not a broken
port. Fix: give electron a Python interpreter inside a venv that has `pyyaml`
(and the rest of `hermes`'s deps), via `HERMES_DESKTOP_PYTHON`.

```bash
cd ~/github/hermes-agent
uv venv .venv
uv pip install -e .          # hermes + deps incl. pyyaml
```

## Bring up a drivable, mock-backed, CDP-open, ISOLATED instance

Vite serves the renderer; dev-mode electron opens CDP (because
`HERMES_DESKTOP_DEV_SERVER` is set) and the backend uses the venv. **You must
isolate `HERMES_HOME`** (see `references/isolated-launch.md` for the full
recipe that also stands up the mock backend + an isolated `config.yaml`).

```bash
# terminal 1 — renderer only (HTTP, no window)
cd apps/desktop && npm run dev:renderer          # vite on :5174

# terminal 2 — electron (FOREGROUND; opens a VISIBLE window — WARN THE USER)
mkdir -p /tmp/hermes-debug-home
# ...write an isolated config.yaml with a mock provider (see reference file)...
cd apps/desktop
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

Poll `curl -s --max-time 3 http://127.0.0.1:9333/json/version` after ~20s.
`npm run dev` (concurrently dev:renderer + dev:electron) is equivalent but
collides if a vite already holds :5174 — kill stray vite first.

Run the Debug MCP server against it with BOTH safety envs set:
```bash
DESKTOP_DEBUG_MCP_ALLOW_ACT=1 \
DESKTOP_DEBUG_MCP_EXPECTED_HOME=/tmp/hermes-debug-home \
DESKTOP_DEBUG_MCP_PORT=9333 \
  node mcp/server.mjs
```
If you skip `DESKTOP_DEBUG_MCP_EXPECTED_HOME`, every mutating tool returns
`REFUSED`.

## Do NOT use `npm run dev:mock` for CDP work

`scripts/dev-mock.mjs` launches the **packaged dist** electron, so
`apps/desktop/electron/dev-cdp.ts` keeps the CDP port closed no matter what
`HERMES_DESKTOP_CDP_PORT` says. Fine for UI-without-CDP; for CDP + editable
composer, run vite + electron dev directly (above).

## Desktop Debug MCP server (`apps/desktop/mcp/`)

Native LLM-agent tools over `scripts/perf/lib/cdp.mjs`:
- **read** (always): `desktop_ui_status`, `ui_inspect`, `ui_query`, `ui_console`,
  `ui_screenshot`, `ui_eval`
- **act** (gated `DESKTOP_DEBUG_MCP_ALLOW_ACT=1`): `ui_click`, `ui_type`,
  `ui_press` — real CDP Input events
- **flow** (gated): `ui_flow_edit` (reproduces the chat-edit silent-fail race),
  `ui_flow_model_switch`

Run with `DESKTOP_DEBUG_MCP_PORT` to match the instance CDP port (default 9222).
`connect()` is per-request, so pass the live port. Proposed upstream in issue
**#95489** (NousResearch/hermes-agent) — triaged `needs-decision`; build locally
regardless.

## Gotcha: `ui_flow_edit` on an empty thread

It returns `edit-button-not-found` when there are no turn pairs. Send a message
first (click composer → `ui_type` → `ui_press` Enter). If the turn pair doesn't
appear after Enter in an isolated instance, click the real Send control by
coordinates — isolated instances don't always trip the form submit guard the
way a focused human keystroke does.

## Gotcha: Enter must re-focus the composer before dispatching

A bare `Input.dispatchKeyEvent` keyDown/keyUp for Enter is **swallowed** if the
composer lost focus between `ui_type` and `ui_press` (e.g. a click elsewhere,
or the renderer blurred on mouse-up). Symptom: `ui_press(Enter)` returns
`{pressed:"Enter"}` but no `turnPair` appears. Fix (already in `tools/act.mjs`):
`press()` first re-focuses `[data-slot="composer-rich-input"]` (falling back to
`document.activeElement`) and passes `commands:['Enter']` so CDP delivers a real
Enter that the React onSubmit handler catches. Without `commands:['Enter']`,
CDP sends the key but the app's form-submit guard may not fire. Synthetic
`dispatchEvent(new KeyboardEvent('keydown',{key:'Enter'}))` does NOT work —
React listens through its synthetic event system and ignores hand-built events.

## Gotcha: `ui_type` lands NO text in the contentEditable composer

`ui_type` sending `Input.dispatchKeyEvent type:'char'` returns `{typed:N}` but
the composer stays **empty** (`el.innerText === ""`) even though focus is held
(`document.activeElement === el`). The composer (`rich-editor.ts`) edits through
the `beforeinput` → `insertText` pipeline (it even routes pastes through
`insertComposerContentsAtCaret` instead of `execCommand('insertText')`
specifically because Chromium's editing pipeline is O(n²)). A bare char event
does not produce a proper `beforeinput` insertText the React handler commits.

**Fix:** `ui_type` must use the CDP `Input.insertText` method (not
`dispatchKeyEvent type:'char'`). `Input.insertText` drives the real
beforeinput→input→insertText pipeline the editor listens for. If you are patching
`tools/act.mjs`, replace the per-character `dispatchKeyEvent` loop in `type()`
with a single `cdp.send('Input.insertText', { text })`. After the fix, verify
with `ui_eval`: `document.querySelector('[data-slot="composer-rich-input"]').innerText`
should equal the typed text before you trust any `ui_flow_edit` repro. Until
then, every "edit race" repro is invalid because the text never reached the DOM.

Confirm focus + text landed with one `ui_eval` probe before asserting anything
about submit/send — a silent-empty composer is the single most common reason a
repro "does nothing."

## Pitfalls

- **Stale compacted details.** A summary handed to you from a *previous*
  context window may name files/lines/bugs that no longer exist (e.g. a cited
  `user-edit-composer.tsx:647` empty catch did not exist on `upstream/main` —
  the file isn't even named that, and `editMessage` already handles errors).
  Before editing code on a bug premise, `grep`/read the file on a fresh
  `git fetch upstream main`. Trust the live repo, not the summary.
- **ISOLATION FIRST.** `HERMES_DESKTOP_USER_DATA_DIR` is NOT `HERMES_HOME`.
  Set `HERMES_HOME=/tmp/<sandbox>` on every debug launch or it silently
  uses `~/.hermes` and writes into the user's real `state.db` (2026-08-26
  incident). The Debug MCP server additionally requires
  `DESKTOP_DEBUG_MCP_EXPECTED_HOME` to match or it refuses all mutations.
  Full recipe: `references/isolated-launch.md`.
- **A surprise visible Electron window confuses the user — announce it before
  spawning.**
- `dev-mock.mjs` `findElectron()` only checked the Linux path; on macOS the
  binary is `Electron.app/Contents/MacOS/Electron` (fixed on branch
  `feat/desktop-debug-mcp`).
- Never kill the user's running app to free the port; launch your own isolated
  instance with a separate `--user-data-dir` + `HERMES_HOME`.
- **`server.mjs` lives only on `feat/desktop-debug-mcp`, not `upstream/main`.**
  If you `git checkout` onto an `upstream/main`-based branch (e.g.
  `fix/chat-edit-race`) and try to run `node apps/desktop/mcp/server.mjs`, you
  get `Cannot find module …/mcp/server.mjs` and a dead repro. To run a live
  repro, check out `feat/desktop-debug-mcp` (or cherry-pick the mcp/ dir) — the
  MCP server is NOT yet merged. The current branch's `git status` / `ls` is the
  source of truth; don't assume the file is everywhere.
- **Reusing one `HERMES_HOME` reuses session history.** Running two repros
  against the same `/tmp/<home>` shows the *previous* run's `turnPair`s, which
  masks whether your new messages actually landed (you'll see stale text and
  think "it worked"). Use a **fresh temp `HERMES_HOME` per repro**
  (`rm -rf /tmp/hermes-repro-home && mkdir … && write config.yaml`), or assert
  on a message text only you sent this run. This bit variant-B: an old
  `stage2 test message` from a prior run hid the fact that the new composer
  input was silently empty.
