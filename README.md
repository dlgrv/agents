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

## Structure and skill provenance

The skills are **third-party**, taken from GitHub. To preserve attribution and easy
updates, each original lives as a **git submodule** under `_vendor/<repo>/`, and `skills/`
holds a **symlink** to the relevant subfolder inside it:

```
~/.agents
├── _vendor/                     ← submodules (clickable on GitHub → origin)
│   ├── multica-ai__andrej-karpathy-skills/
│   ├── mattpocock__skills/
│   ├── cursor__plugins/
│   ├── shadcn-ui__ui/
│   ├── garrytan__gstack/
│   └── Nanako0129__sepia/
├── skills/                      ← symlinks → ../_vendor/.../<skill-path>
│   ├── karpathy-guidelines            → multica-ai__andrej-karpathy-skills/skills/karpathy-guidelines
│   ├── improve-codebase-architecture  → mattpocock__skills/skills/engineering/improve-codebase-architecture
│   ├── thermo-nuclear-code-quality-review → cursor__plugins/cursor-team-kit/skills/thermo-nuclear-code-quality-review
│   ├── shadcn                          → shadcn-ui__ui/skills/shadcn
│   ├── plan-eng-review                 → garrytan__gstack/plan-eng-review
│   ├── sepia                           → Nanako0129__sepia/skills/sepia
│   ├── hallmark                        → Nutlope__hallmark/skills/hallmark
│   ├── anti-slop                       → rand__cc-polymath/skills/anti-slop
│   └── (14 × superpowers skills)       → obra__superpowers/skills/<name>
├── README.md                    ← this file
└── LICENSE                      ← MIT (for my files only; submodules keep their own licenses)
```

| Skill | Upstream | License (upstream) |
|---|---|---|
| karpathy-guidelines | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | MIT |
| improve-codebase-architecture | [mattpocock/skills](https://github.com/mattpocock/skills) | see upstream |
| thermo-nuclear-code-quality-review | [cursor/plugins](https://github.com/cursor/plugins) | see upstream |
| shadcn | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | see upstream |
| plan-eng-review | [garrytan/gstack](https://github.com/garrytan/gstack) | see upstream |
| sepia | [Nanako0129/sepia](https://github.com/Nanako0129/sepia) (skills/sepia) | MIT |
| hallmark | [Nutlope/hallmark](https://github.com/Nutlope/hallmark) | MIT |
| anti-slop | [rand/cc-polymath](https://github.com/rand/cc-polymath) (skills/anti-slop) | MIT |
| superpowers (14 skills) | [obra/superpowers](https://github.com/obra/superpowers) | MIT |

## Update (pull the latest)

```bash
cd ~/.agents
git pull                                   # superproject (README, .gitmodules, my files)
git submodule update --init --recursive     # after a fresh clone on a new machine
git submodule update --remote --recursive   # refresh third-party to their latest versions
```

Submodules **pin a specific commit** of the original; "latest" only appears after `--remote`.

## Add a new third-party skill

1. `git submodule add <url> _vendor/<repo>`
2. `ln -s ../_vendor/<repo>/<skill-path> skills/<name>`
3. `git add skills/<name> _vendor/<repo>` and commit.

## Your own materials

Future personal files (prompts, `AGENTS.md`, `CLAUDE.md`, notes) go in as regular repo
files — no submodules. The catalog grows horizontally without rework.

## Backup (survive upstream deletion)

The `_vendor/*` submodules only store a **pointer** (gitlink + commit SHA), not the
files. If an upstream repo is deleted from GitHub, a fresh clone or
`git submodule update --remote` can lose the skill contents.

To keep a real copy inside this repo, run the snapshot script — it copies the unpacked
skill files (without nested `.git`) into `_vendored_snapshot/<name>/`, which IS committed
to `dlgrv/agents`:

```bash
bash scripts/snapshot.sh
git add -A && git commit -m "snapshot: $(date +%F)" && git push
```

`_vendored_snapshot/` is **restore-only** — agents keep reading `skills/*` (symlinks into
`_vendor`). Run the snapshot whenever you update submodules or want a fresh safety copy.
