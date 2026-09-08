# ~/.agents — central agent-skills hub

All skills for AI agents (Cursor, Codex, Claude Code, Hermes, etc.) live here, in one place.
This folder is both the on-disk working directory **and** a public mirror:
[github.com/dlgrv/agents](https://github.com/dlgrv/agents).

## Add skills to a project

```bash
ln -sfn ~/.agents <project>/.agents
```

Symlink the whole `~/.agents` directory — the project gets all its contents
(skills, README, etc.) and stays always up to date.

## Why symlink the whole directory

- **Single source of truth**: update something in the hub — it's instantly current in every project.
- Cursor reliably reads `.agents/skills/` only inside a project; global user skills are unstable for it.
- Zero sync commands, zero cron jobs, zero diverging copies.

## Structure — real copies, attribution in README

`skills/<name>/` are **real committed copies** (not symlinks, not submodules) of
**only the used subfolder** of each upstream repo. We don't vendor whole upstream
monorepos (they can be tens of thousands of files) — just the skill we use, pinned
to the upstream commit it was taken from (see the attribution table). This survives
upstream deletion by design, needs no `git submodule update --init` on a fresh
machine, and keeps the repo at a few MB.

```
~/.agents
├── skills/                      ← real dirs, committed files
│   ├── karpathy-guidelines/           ← from multica-ai/andrej-karpathy-skills
│   ├── improve-codebase-architecture/ ← from mattpocock/skills
│   ├── thermo-nuclear-code-quality-review/ ← from cursor/plugins
│   ├── shadcn/                        ← from shadcn-ui/ui
│   ├── plan-eng-review/               ← from garrytan/gstack
│   ├── sepia/                         ← from Nanako0129/sepia
│   ├── hallmark/                      ← from Nutlope/hallmark
│   ├── anti-slop/                     ← from rand/cc-polymath
│   ├── anthropic-frontend-design/     ← from anthropics/skills
│   ├── design-taste-frontend/, high-end-visual-design/,
│   │   redesign-existing-projects/, image-to-code/  ← from Leonxlnx/taste-skill
│   ├── omo-frontend/                  ← local build from code-yeongyu/oh-my-openagent (see below)
│   └── (14 × superpowers skills)      ← from obra/superpowers
├── subagents/                   ← own subagents, unified Cursor + Claude Code (see below)
├── cursor/rules/                ← Cursor-specific global rule (see below)
├── scripts/
│   └── update-skill.sh          ← refresh one skill from upstream
├── README.md                    ← this file
└── LICENSE                      ← MIT (for my files only; skills keep upstream licenses)
```

## Attribution

Third-party skills belong to their authors; this repo ships only the skill
subfolders, each pinned to the upstream commit it was copied from.
`_ pins` = the upstream commit SHA the copy was taken from (also recorded in
`skills/<name>/.upstream-pin`).

| Skill | Upstream (we use only the skill subfolder, not the whole repo) | License (upstream) | _ pin |
|---|---|---|---|
| karpathy-guidelines | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) `skills/karpathy-guidelines` | MIT | `2c60614` |
| improve-codebase-architecture | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/improve-codebase-architecture` | see upstream | `6654f6b` |
| thermo-nuclear-code-quality-review | [cursor/plugins](https://github.com/cursor/plugins) `cursor-team-kit/skills/thermo-nuclear-code-quality-review` | see upstream | `bdf7aa3` |
| shadcn | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) `skills/shadcn` | see upstream | `683a5a9` |
| plan-eng-review | [garrytan/gstack](https://github.com/garrytan/gstack) `plan-eng-review` | see upstream | `ad84005` |
| sepia | [Nanako0129/sepia](https://github.com/Nanako0129/sepia) `skills/sepia` | MIT | `4c8d782` |
| hallmark | [Nutlope/hallmark](https://github.com/Nutlope/hallmark) `skills/hallmark` | MIT | `13ac0ec` |
| anti-slop | [rand/cc-polymath](https://github.com/rand/cc-polymath) `skills/anti-slop` | MIT | `baa2df1` |
| superpowers (14 skills) | [obra/superpowers](https://github.com/obra/superpowers) `skills/<name>` | MIT | `b36e082` |
| anthropic-frontend-design | [anthropics/skills](https://github.com/anthropics/skills) `skills/frontend-design` | see upstream | `41bbe19` |
| design-taste-frontend | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) `skills/taste-skill` | see upstream | `ccbc156` |
| high-end-visual-design | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) `skills/soft-skill` | see upstream | `ccbc156` |
| redesign-existing-projects | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) `skills/redesign-skill` | see upstream | `ccbc156` |
| image-to-code | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) `skills/image-to-code-skill` | see upstream | `ccbc156` |
| omo-frontend (local build) | [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) — SKILL.md из `packages/skills-loader-core/.../frontend`, references из `packages/shared-skills/skills/frontend/references` (design/designpowers/perfection); Layer A taste-файлы — симлинки на скиллы из этого хаба; брендовые Layer B (Open Design) — заглушки | see upstream | local |

## Update a skill from upstream

```bash
cd ~/.agents
./scripts/update-skill.sh <skill-name> <subpath-in-upstream-repo>
# e.g.:
./scripts/update-skill.sh karpathy-guidelines skills/karpathy-guidelines
git add skills/<name> && git commit -m "update <name> from upstream"
```

The script shallow-clones the upstream repo and rsyncs the subfolder over the
inlined copy. Check the diff before committing — upstream may have moved ahead.

## Add a new third-party skill

1. Clone the upstream repo (shallow), copy the skill subfolder into `skills/<name>/`.
2. Write the pinned upstream SHA into `skills/<name>/.upstream-pin`.
3. Add a row to the attribution table above and commit.

## Your own materials

Personal files (subagents, rules, prompts, notes) go in as regular repo files —
no submodules. The catalog grows horizontally without rework.

## Subagents (`subagents/`) — unified across agents

Own subagents in the common Claude-Code format (md + YAML frontmatter). Cursor and
Claude Code both read this format; each is wired to the single source with symlinks:

```
~/.agents/subagents/          ← symlinked WHOLE into ~/.cursor/agents and ~/.claude/agents
├── bulk-reader.md          ← reads files, returns only a summary; composer-2.5, readonly
└── boilerplate-writer.md   ← tests/config/stubs by pattern; composer-2.5
```

```bash
# Cursor (user scope, all projects — whole-dir symlink)
ln -sfn ~/.agents/subagents ~/.cursor/agents
# Claude Code (user scope, all projects — whole-dir symlink)
ln -sfn ~/.agents/subagents ~/.claude/agents
```

Pattern: token-saving delegation (inspired by Spotify's shunt / Portal AiKA modes) —
subagents keep bulky file contents out of the main thread. Note: the `model:` field
like `composer-2.5` is Cursor-specific — Claude Code ignores unknown ids and uses
its default.

## Cursor rule (`cursor/rules/`)

`cursor/rules/delegation.mdc` — Cursor-specific `.mdc` rule telling the main agent to
route 3+ file reads / 350+ line files to the subagents above. There is no cross-agent
standard for global rules, so this stays Cursor-only:

```bash
# whole-directory symlinks (one command per app; new files appear automatically)
ln -sfn ~/.agents/subagents       ~/.cursor/agents   # same dir doubles as ~/.claude/agents
ln -sfn ~/.agents/subagents       ~/.claude/agents
ln -sfn ~/.agents/cursor/rules    ~/.cursor/rules
# per project (documented rules location, guaranteed effect)
mkdir -p <project>/.cursor/rules && ln -sfn ~/.agents/cursor/rules/delegation.mdc <project>/.cursor/rules/delegation.mdc
```

`~/.cursor/rules/` is not an officially documented rules source — for a guaranteed
effect, paste the rule body into **Settings → Rules → User Rules** (one-time) or
symlink it into a project's `.cursor/rules/`.
