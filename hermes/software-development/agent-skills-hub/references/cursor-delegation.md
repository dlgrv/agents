# Cursor delegation setup — session detail (2026-09-08)

Goal: reproduce Spotify's Portal/shunt token-saving pattern in Cursor **without
any third-party API or Portal instance** (the official spotify/portal-ai-plugins
cursor-plugin exists but requires a Portal/Backstage instance → useless standalone).

## What was installed (Cursor 3.19.13)

Lives in `~/.agents/cursor/` (hub repo dlgrv/agents). **Final wiring: whole-DIRECTORY
symlinks** (one per app; new hub files appear in apps automatically):

| Hub dir | Symlink (whole dir) | Contents |
|---|---|---|
| `~/.agents/subagents/` | `~/.cursor/agents` AND `~/.claude/agents` | `bulk-reader.md` (reads files, returns only a summary; composer-2.5, readonly), `boilerplate-writer.md` (tests/config/stubs by pattern; composer-2.5) |
| `~/.agents/cursor/rules/` | `~/.cursor/rules` | `delegation.mdc`: delegate 3+ file reads / 350+-line files to subagents |

Plus the GUARANTEED per-project wiring the user chose (option 2):
`<project>/.cursor/rules/delegation.mdc` → symlink to the hub file. For
dlgrv.com this landed without a repo change — its `.gitignore` already ignores
`.cursor/`. Project wiring should be repeated per repo (one command in README).
The rule file itself must stay project-agnostic (no hardcoded paths/names).

Frontmatter for Cursor subagents: `name`, `description` (must start "Use when…" —
this is what the main agent matches on), `model: composer-2.5`, `readonly: true`
for readers. `/agent-name` in chat invokes explicitly (near-100% reliable).

## Cursor facts (verified via docs + forum, 2026-09)

- **No toggle forces subagent use.** Cursor staff: "delegation is controlled by
  the prompt, not enforced by structure." Strengtheners: "Use when…" descriptions,
  explicit `/agent-name`, rules.
- **Built-in subagents are free wins**: Explore / shell / browser subagents
  auto-engage on noisy ops (codebase search, long command output) out of the box.
- **`~/.cursor/agents/` is documented user scope** for custom subagents (all
  projects). **`~/.cursor/rules/` is NOT documented** as a global rules source —
  guaranteed paths: Settings → Rules → User Rules (paste), or per-project
  `.cursor/rules/*.mdc`.
- **Hooks exist** (cursor.com/docs/hooks) and are the hard-gate analog of shunt:
  `beforeReadFile`, `preToolUse`, `beforeShellExecution`, `beforeMCPExecution`,
  `subagentStart/Stop`, `beforeSubmitPrompt`, `preCompact`, `stop`, … A hook
  script can DENY a ≥350-line read and inject "use bulk-reader instead".
  Not enabled by default; Feb 2026 forum bug report says `beforeReadFile` did not
  fire in the IDE agent — **test live on the installed version before relying**.
- **Nested subagents**: a subagent spawning subagents is limited (~2 levels);
  flat `main → specialists` is the reliable topology. Orchestrator patterns
  degrade silently (main ends up doing the work itself).
- `Task()` params include `subagent_type`, `model` (enum varies by version —
  e.g. composer-2-fast), `run_in_background`, `readonly`, `resume`.
- Subagent runs bill as separate requests on legacy request-based plans.

## Status / follow-ups

- Hook gateway (block big reads → hint bulk-reader) was proposed, user hasn't
  approved yet — do not assume it exists.
- Config lives in the hub on branch `feat/inline-skills` (PR #6, 4 commits as of
  2026-09-08 evening: inline-skills refactor + README/docs commits). Until merge,
  hub `main` lags the working tree — working symlinks already point at the files,
  so both apps function regardless.
- Architecture note: the same PR inlined the third-party skills (submodules →
  real copies); `cursor/` + `subagents/` dirs were moved from `cursor/agents/` to
  the top-level `subagents/` during unification (Claude Code needed a home too).
