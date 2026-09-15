---
name: zed-editor
description: Use when configuring Zed editor settings or AI providers.
---

# Zed editor configuration

Config lives in `~/.config/zed/settings.json` (JSONC — comments allowed; strip `//` lines before `json.loads` validation).

## AI providers (openai_compatible)

```jsonc
"language_models": {
  "openai_compatible": {
    "cometapi": {
      "api_url": "https://api.cometapi.com/v1",
      "available_models": [
        {"name": "glm-5.3-flash", "max_tokens": 1000000}
      ]
    }
  }
}
```

- API key env var is `<PROVIDER_ID>_API_KEY` — provider id + `_API_KEY`, NOT whatever the key is called in ~/.hermes/.env: `cometapi`→`COMETAPI_API_KEY`, `openrouter-free`→`OPENROUTER_FREE_API_KEY`, `opencode-zen`→`OPENCODE_ZEN_API_KEY`. Setting only `COMETAPI_KEY` (the key's .env name) hides the provider's models from the picker — hit exactly this.
- Native-OpenRouter gotcha: Zed ships a built-in OpenRouter provider; setting `OPENROUTER_API_KEY` alone makes the picker show ALL OpenRouter models incl. `openrouter/auto` ("Auto Router"), even with no custom openai_compatible block — looks like your custom block works when it doesn't. Custom-block models appear only once their own `<ID>_API_KEY` is set.
- Zed launched from Finder does NOT inherit shell env — see note below on the REMOVED LaunchAgent.
- `max_tokens` = context window used for fill indicators. Check real model context (OpenRouter model page is reliable); better to understate than overstate — proxies may deliver less than advertised.
- User's provider set (2026-09): cometapi = glm-5.3-flash only (context 1M, real window 1,310,720); `openrouter-free` (17 free chat models); `opencode-zen` (8 free models) — zen is configured in settings but .env `OPENCODE_ZEN_API_KEY=` is EMPTY (no key yet), provider won't show until user fills it. Keep only what user asked — they prune lists deliberately.
- Free-list maintenance (user wants free-ONLY lists — "remove all paid, keep only free"): both lists should equal the FULL free set of their catalogs. Snapshot + refresh procedure: `references/free-model-catalogs.md`. Gotchas: OpenRouter catalog drifts — verify every existing id still exists before keeping it (found dead `z-ai/glm-5.2:free` on 2026-09-07); `:free` suffix is NOT a reliable free marker (`openrouter/free` has no suffix); skip $0 non-chat models (lyria = audio gen, nemotron content-safety = moderation classifier). Zen: `/zen/v1/models` returns NO pricing fields — free set is suffix-marked (`-free`, `-contributor-free`, plus `big-pickle`), everything else paid. Zed `max_tokens` for OR free = real context (128k standard; nemotron-3-nano-omni 256k).

## Env keys for GUI-launched apps (LaunchAgent REMOVED)

Finder-launched apps miss shell env. The LaunchAgent that handled this (`app.dlgrv.zed-provider-keys` + `~/.config/zed/set-provider-env.sh`, mapping keys from `~/.hermes/.env` to Zed `<ID>_API_KEY` names via `launchctl setenv`) was REMOVED at user request 2026-09-15. Backup with both files: `~/.hermes/backups/zed-provider-keys/` — restore = copy back to original paths + `launchctl bootstrap gui/$(id -u) <plist>`. Consequence: after reboot, Zed launched from Finder has no provider keys (custom providers vanish from picker) until the agent is restored or keys are set another way. Known-good script copy also lives at `templates/set-provider-env.sh`. Naming matters: macOS shows the launched binary as the process name — `/bin/sh -c '...'` displays as anonymous "sh", a named script file shows clearly. One agent per purpose; check `launchctl list` before adding duplicates. Verify with `launchctl getenv <NAME>` after running the script. A RUNNING Zed never picks up newly setenv'd vars — inspect what it actually sees via `ps -Eww -p $(pgrep -x zed)`; a full Cmd+Q restart is required for changes to land.

## Themes

Cursor themes (`Cursor Dark`, `Cursor Dark Midnight`, `Cursor Light`, HC) are converted from Cursor's own VS Code JSON themes into `~/.config/zed/themes/`. User wants Zed to look exactly like Cursor. Zed "Cursor Theme Pack" extension may not exist in the registry — local conversion is the working path.

## Panel layout (the big gotcha)

Since Zed 0.233 the agent area is TWO separate docks with independent positions — `agent.sidebar_side` moves only the chat, not the thread history:

- `agent.sidebar_side` — Agent Panel (the chat itself)
- `threads_sidebar.dock` — Threads Sidebar (thread history list; cmd-alt-j)
- `project_panel.dock` — file tree

Defaults flipped in 0.233: agent + threads LEFT, project panel RIGHT. User's layout (mirrors Cursor): project panel left, chat AND threads right. **Per-window override:** right-click a panel icon in the bottom status bar → Dock Left/Right beats settings.json for that window — if settings look right but layout is wrong, that's the cause.

## Fonts / look

Earlier font changes were reverted once ("верни как было") — but later the user asked AGAIN to match Cursor exactly; the final accepted state is a full Cursor match, don't assume they hate font changes. Key lesson: pull REAL values from Cursor's runtime state, don't guess VS Code defaults.

**How to read Cursor's actual fonts:** `settings.json` (`~/Library/Application Support/Cursor/User/settings.json`) has NO font overrides there — defaults lie. The rendered truth is in `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` (SQLite, table `ItemTable`, key `editorFontInfo`): it holds the *effective* editor font (family/size/lineHeight at current pixelRatio). UI font = VS Code base 13px, zoom 0 unless changed via Cmd+= (zoomLevel lives in the same DB / window state, check for 'zoom' keys).

Current matched state (user-approved): `buffer_font_size: 12`, `buffer_font_family: "Menlo"`, `buffer_line_height: "comfortable"`, `ui_font_size: 13`. Tuning history: started 15/16 (too big for user), went to 14/13, settled 12/13 to match Cursor exactly.

- Zed live-reloads settings.json on save — no restart needed; if nothing changed visually, the window just needs focus or was launched before the edit.
- Font sizing feedback loop: user judges by look, not numbers. Offer Cmd+-/Cmd+= for live preview, then pin the number into settings.json when they say stop.
- Other look prefs: `base_keymap: "VSCode"`, proxy `http://127.0.0.1:17890`.

## Workflow notes

- Edit settings.json with targeted string replacement + validate (strip comment lines, `json.loads`) — a broken bracket silently disables settings.
- Verify no duplicate JSON keys after scripted edits (regex count on raw text; `json.loads` keeps the last duplicate silently).
- See `references/panel-layout.md` for the full panel-position reference.
