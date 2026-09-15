---
name: hermes-desktop-ui-automation
description: "Agent MCP tools to drive the Hermes desktop UI, isolated."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, electron, cdp, mcp, ui-debugging, isolation, automation]
    related_skills: [inspecting-hermes-desktop-dom, systematic-debugging, node-inspect-debugger]
---

# Hermes desktop UI automation for agents

## When this applies

You are building or using a tool surface that lets an LLM agent **drive** the
Hermes desktop renderer (click, type, press, run scripted flows) — not just
read it. The companion read-only skill is `inspecting-hermes-desktop-dom`; this
one covers the *acting* layer and, critically, the **safety rail** around it.

This is the class of work that produced the `apps/desktop/mcp/` debug-MCP
server (issue NousResearch/hermes-agent#95489): tools like `ui_click`,
`ui_type`, `ui_press`, `ui_eval`, `ui_flow_edit` over the dev CDP port.

## When to Use

- Adding, extending, or reviewing an agent-facing desktop tool surface that
  *acts* on the UI (not just reads it).
- Launching a debug/dev desktop instance and needing it fully isolated from the
  user's real `~/.hermes` (keys + chat history).
- Driving the renderer via CDP and hitting a "message won't submit" or "edit
  composer won't open" dead end.

Do not use for read-only inspection alone — that is `inspecting-hermes-desktop-dom`.

## The one rule that is not optional: isolation

A desktop instance keeps its config, API keys, and **entire chat history**
(`state.db`) under `HERMES_HOME`. If you launch a debug instance without an
isolated `HERMES_HOME`, it falls back to `~/.hermes` — the user's real install —
and **writes your test messages into their real session history**. This happened
in the 2026-08-26 incident: a manual `electron .` launch set only
`HERMES_DESKTOP_USER_DATA_DIR` (Chromium profile only) and silently used
`~/.hermes`, sending a test prompt to the real model and landing the reply in
the user's `state.db`.

**Rule:** any mutating tool MUST be fail-closed. The `apps/desktop/mcp` server
requires `DESKTOP_DEBUG_MCP_EXPECTED_HOME` to be set AND to differ from the
default home; if unset or equal to `~/.hermes`, every mutating call returns
`REFUSED`. You cannot reliably read the target's `HERMES_HOME` from the renderer
(it isn't exposed), so require the operator to *declare* it.

## Verified isolated-launch recipe

See `references/isolated-instance.md` for the full sequence. The non-negotiables:

1. `HERMES_HOME=/tmp/<throwaway>` with a **mock provider** `config.yaml` (no real
   keys, no real chats).
2. A Python venv with `yaml` installed (`uv venv .venv && uv pip install -e .`)
   — otherwise the backend exits and the composer renders `contentEditable=false`
   (disabled), so you can't type.
3. `HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174` + a running vite — the CDP
   port only opens with a dev server set (`electron/dev-cdp.ts`).
4. `HERMES_DESKTOP_CDP_PORT=9333` (≠ 9222, to avoid colliding with a running
   `hgui`) and `--user-data-dir=/tmp/<throwaway>` (avoids Electron's
   single-instance lock).
5. Launch the server with `DESKTOP_DEBUG_MCP_EXPECTED_HOME=/tmp/<throwaway>`.

## Driving gotchas (real events only)

- Use real CDP `Input.dispatch*` — synthetic `dispatchEvent` doesn't trigger
  React handlers or blur→cancel races.
- **Sending a message:** click composer → type → press Enter does NOT submit
  unless the composer keeps focus. The press step must re-focus
  `[data-slot="composer-rich-input"]` *before* `keyDown`/`keyUp` with
  `commands:['Enter']`. Without that, Enter is swallowed and `turnPair` stays
  empty.

## Pitfalls

- Never launch a debug instance against `~/.hermes`. Set an isolated
  `HERMES_HOME` every time, no exceptions.
- `HERMES_DESKTOP_USER_DATA_DIR` is NOT a substitute for `HERMES_HOME`.
- A visible window opens — warn the user before spawning it.
- `npm run dev:mock` doesn't open CDP (no dev server) and its `findElectron()`
  only checks the Linux `dist/electron` path (fails on macOS
  `Electron.app/Contents/MacOS/Electron`). Prefer the manual sequence in the
  reference until patched.
