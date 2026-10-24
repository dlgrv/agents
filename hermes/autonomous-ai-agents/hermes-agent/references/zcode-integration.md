# ZCode ↔ Hermes integration (skills, MCP, chat history)

ZCode (Z.AI's desktop/CLI coding agent, binary `zcode`, app bundle ships the runtime at `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs`) can consume Hermes assets. Source of truth for mechanics: `github.com/zai-org/ZCode`, files `apps/zcode-cli/packages/adapters/src/skills/{scan,roots}.ts` and `.../config/schema.ts` — read those before guessing at config fields.

## Procedure

1. **Backup first**: `cp ~/.zcode/cli/config.json ~/.zcode/cli/config.json.bak-$(date +%Y%m%d-%H%M%S)`. Runtime config (MCP, skills, plugins, hooks) lives at `~/.zcode/cli/config.json`; it is shared by the desktop app and CLI and is schema-validated (zod, strict).
2. **Skills — symlink, don't reconfigure.** ZCode scans each root only ONE level deep (`root/<skill>/SKILL.md`), so Hermes's `category/skill/SKILL.md` nesting is invisible via a plain root entry. Instead create `~/.zcode/skills/` and symlink every skill dir found under `~/.agents/hermes` (flatten categories; prefix nested-name collisions with the category). User-level roots follow symlinks by design ("symlink 导入" is a supported feature); plugin-scope scanning rejects them. Roots resolved automatically: user `~/.zcode/skills` + `~/.agents/skills` (zcode wins on name conflicts), then project-level up to the git worktree root. Verify with `zcode skills list --json` (run via the bundled runtime or PATH binary).
3. **MCP — mirror `mcp_servers` from Hermes `config.yaml` into `cfg["mcp"]["servers"]`**, and set `features: {mcp: true, skill: true}`. Schema is `.strict()` per server type — an extra/misspelled field silently drops the WHOLE server entry:
   - stdio: `{type, command, args?, cwd?, env?, enabled?, timeoutMs?, alwaysLoad?, protocolVersion?}`
   - http/sse: `{type, url, headers?, oauth?, enabled?, timeoutMs?}`; interactive OAuth = `oauth: {type: "authorization_code"}` (user clicks through in-app on first use)
   - Hermes-specific fields have no equivalent: `tools.exclude` (unsupported — server exposes all tools) and string `args` (must be split into an array).
   Copy secrets straight from Hermes config in a script — never print them into the chat. Carry over Hermes's enabled/disabled state per server.
4. **History — expose as a skill, there is no native import.** Write a `hermes-history` skill into `~/.zcode/skills/` instructing read-only SQLite access: `sqlite3 'file:~/.hermes/state.db?mode=ro'` — tables `sessions` (id, display_name, started_at epoch, message_count, model), `messages` (session_id, role, content, tool_name, timestamp), FTS via `messages_fts` (join `f.rowid` → `messages.id`). The DB is live — always `mode=ro`, never plain open.
5. **Verify + hand over**: `zcode doctor --json` (config loads), `zcode skills list --json` (count + probe known names). The desktop app must be RESTARTED to pick up the config. Tell the user the roll-back path (restore backup, delete `~/.zcode/skills`).

## Pitfalls

- Validate the written config against the actual schema.ts from the matching ZCode version before calling it done — the schema evolves and strict fields mean a stale blog-post example can zero out servers silently.
- Headless end-to-end MCP test usually isn't possible: the bundled runtime errors "Select a model before sending a message" because model selection lives in desktop app state, and it needs `ZCODE_BUILTIN_PROVIDER_CONFIG_FILE=/Applications/ZCode.app/Contents/Resources/config/provider/zcode-builtin.json` when run outside the app. Don't edit the user's provider config just to test — verify config+skills via doctor/skills list and have the user do one live MCP call after restarting the app.
- macOS has no `timeout` command — a `timeout N cmd ...` verification silently runs nothing with exit 0. Use the tool call's own timeout parameter.
