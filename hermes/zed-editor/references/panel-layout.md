# Zed panel layout reference

## Panels and their settings (Zed >= 0.233, Parallel Agents release)

| Panel | Setting | What it is |
|---|---|---|
| Agent Panel (chat) | `agent.sidebar_side` | The conversation view + message input |
| Threads Sidebar | `threads_sidebar.dock` | List of agent threads grouped by project (cmd-alt-j) |
| Thread History | toggled inside Threads Sidebar | Archived/restored threads (cmd-g) |
| Project Panel | `project_panel.dock` | File tree |
| Git Panel | `git_panel.dock` (implied) | Git changes |

Key fact: `agent.sidebar_side` does NOT move the Threads Sidebar. They dock independently and both default LEFT since 0.233 ("Threads now dock on the left by default, next to the Agent Panel, with the Project Panel and Git Panel on the right" — zed.dev/blog/parallel-agents).

## Symptom → fix

- "Chat on the left but history on the right" → settings have `agent.sidebar_side: left` (or default) + `threads_sidebar.dock: right`. Set both.
- "Settings say right but panel shows left" → per-window dock override. Right-click the panel icon in the bottom status bar → Dock Right. This wins over settings.json for the open window.
- Two `agent` keys in settings.json → last one wins silently; dedupe.

## User's chosen layout (Cursor-style)

```jsonc
"agent": { "sidebar_side": "right" },
"threads_sidebar": { "dock": "right" },
"project_panel": { "dock": "left" }
```
