# Telegram UX Configuration and Features

## Reactions (Visual Acknowledgments)

Enable reactions to show bot status without text spam:

```bash
hermes config set platforms.telegram.extra.reactions true
systemctl --user restart hermes-gateway
```

**Lifecycle:**
- 👀 When message processing starts (acknowledgment)
- 👍 On successful completion
- 👎 On failure
- Clear on cancelled/timeout

Reactions work in both DM and group chats. No config needed beyond enabling.

## Tool Progress Cleanup

Remove technical messages after successful final response:

```bash
hermes config set display.cleanup_progress true
systemctl --user restart hermes-gateway
```

This deletes 🐍 Running code, ⏳ Working bubbles after successful responses. Failed runs retain breadcrumbs for debugging.

## Display Settings for Telegram

| Setting | Default | Effect |
|---|---|---|
| `tool_progress` | `off` (Telegram) | Controls tool execution messages (`all`/`new`/`off`) |
| `interim_assistant_messages` | `true` | Intermediate comments between tool calls |
| `long_running_notifications` | `true` | "Still working" notifications on long tasks |
| `busy_ack_detail` | `false` | Detailed acknowledgment text |
| `show_reasoning` | `false` | Display model reasoning output |
| `reasoning_style` | `code` | Markdown style for reasoning blocks |
| `tool_preview_length` | `0` | Max preview length in tool progress |

## Session Management

- `/sessions` shows last 10 sessions only (no pagination)
- Use `/resume <name>` for older sessions
- Pin state is stored in state.db, not exposed via CLI
- No dedicated "show pinned" command exists

## Group Chat Behavior

- Allowlist mode: `platforms.telegram.extra.allowlist = ["chat_id"]`
- Require mention: `platforms.telegram.extra.require_mention = true`
- Topics: Enable with `/topic` in the chat; Hermes respects Telegram's topic state
- Reactions work in groups (same lifecycle as DM)
- Model picker via inline buttons (if enabled)

## Stream Mode

- **Edit streaming** enabled by default (`streaming: true`)
- Shows live response editing as bot types
- Compatible with reactions and cleanup_progress

## Clarify and Buttons

- Questions appear as interactive buttons (not text)
- Use `clarify` tool for multi-option questions
- Buttons work in both DM and groups

## Pitfalls

- Reactions require gateway restart to take effect
- `cleanup_progress` only applies to NEW responses (old messages stay)
- `tool_progress` setting affects message verbosity; `off` + `cleanup_progress` = minimal noise
- No way to delete old technical messages retroactively
- Reactions are not customizable (fixed emoji lifecycle)
