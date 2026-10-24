---
name: zcode-hermes-integration
description: Use when bridging Hermes skills, MCP or history into ZCode.
---

# ZCode ↔ Hermes integration (macOS, this machine)

## Layout
- ZCode runtime config (MCP, features, skills, hooks, plugins): `~/.zcode/cli/config.json` — shared by desktop app and CLI agent. Backup before editing (`config.json.bak-<ts>`).
- ZCode provider/model: `~/.zcode/v2/provider_config.json` (desktop keeps model selection in app state; headless `-p` fails with "Select a model" — don't hack this file to test).
- ZCode sessions: `~/.zcode/cli/db/db.sqlite` — schema is an implementation detail, NOT a stable API; never write into it (docs forbid; weekly releases change it). Read-only analysis is OK.
- ZCode instructions: `~/.zcode/AGENTS.md` (user) merged with project AGENTS.md. Memory: `features.memory` + `memory.use`; memory is extracted from ZCode's own sessions only — no import API.
- Hermes skills: `~/.hermes/skills` is a symlink to `~/.agents/hermes` (dlgrv/agents hub; category/skill/SKILL.md nesting).
- Third-party flat skills: `~/.agents/skills` (32) — ZCode discovers this path natively.
- Hermes MCP servers: `mcp_servers:` in `~/.hermes/config.yaml`.
- Hermes chat history: `~/.hermes/state.db` sqlite, tables `sessions`/`messages` (+FTS `messages_fts`). Live DB — always open `file:...?mode=ro`.

## Skill discovery mechanics (zcode 0.17 / apps/zcode-cli/packages/adapters/src/skills/ in zai-org/ZCode)
- Roots: user `~/.zcode/skills` + `~/.agents/skills`, project `<dir>/.zcode/skills` + `<dir>/.agents/skills` (walk up to git/worktree root). `.zcode` root wins on name conflict at same level.
- Scan depth = ONE level: root/SKILL.md + root/<child>/SKILL.md. Category dirs (cat/skill/SKILL.md) are NOT scanned — flatten with symlinks (user-level roots follow symlinks; officially supported import; plugin-scope does NOT follow links).
- Config `skills.roots` adds extra roots but same one-level rule → cannot replace flattening.

## Working recipe (done 2026-10-24)
- `~/.zcode/skills/<name>` → symlink per Hermes skill dir (flatten categories, prefix name on collision). Auto-updates via skills-sync since targets are the hub.
- Custom skill `~/.zcode/skills/hermes-history/SKILL.md` = read-only sqlite queries into state.db (recent sessions, FTS keyword search, dump session by id). This is the supported way to give ZCode access to Hermes chat history. Do NOT import chats into ZCode's db.sqlite: schema unstable, writes forbidden by docs.
- MCP: convert Hermes `mcp_servers` into `mcp.servers` in `~/.zcode/cli/config.json`. STRICT zod schema (.strict()): stdio = {type,command,args,cwd,env,enabled,timeoutMs,alwaysLoad,protocolVersion}; http = {type,url,headers,oauth:{type:"authorization_code"|"client_credentials",...},enabled,timeoutMs}. Any extra field (e.g. Hermes `tools.exclude`) silently drops the WHOLE server. Add `"features":{"mcp":true,"skill":true}`.
- Tokens land in plaintext in config.json (same exposure as Hermes config.yaml) — acceptable per user, but never print to chat; move programmatically.

## API retries (busy/429/5xx)
- Built-in by default: 10 retries (11 attempts), exponential backoff 2s base, factor 2, cap 60s, jitter. No config.json field.
- Override via env only: `ZCODE_MODEL_RETRY_MAX_RETRIES`, `ZCODE_MODEL_RETRY_BASE_DELAY_MS`, `ZCODE_MODEL_RETRY_BACKOFF_FACTOR`, `ZCODE_MODEL_RETRY_MAX_DELAY_MS`. For the desktop app use `launchctl setenv` before launch; CLI runs inherit shell env. Source: apps/zcode-cli/packages/adapters/src/model/retry-policy.ts.

## Verify
- Runtime: `node /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs` (needs `ZCODE_BUILTIN_PROVIDER_CONFIG_FILE=/Applications/ZCode.app/Contents/Resources/config/provider/zcode-builtin.json` outside the app; macOS has no `timeout` cmd).
- `zcode skills list --json` (count + probe names), `zcode doctor --json`. No `zcode mcp list`; MCP connect check requires the desktop app (login + model selection live there).
- Restart the desktop app to pick up config changes.
