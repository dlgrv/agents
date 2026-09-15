---
name: vendored-skills-hub
description: Mirror third-party agent skills into a git hub.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, github, submodules, agent-skills, dotfiles, backup]
    related_skills: [github-repo-management, github-issue-to-pr]
---

# Vendored Skills Hub

A repeatable way to run a **central hub of third-party agent skills** (Cursor,
Claude Code, Codex, Hermes, Windsurf, …) as a git repo that:
- preserves **attribution** (one click from your repo → the upstream origin),
- keeps **agent discovery working** (`skills/<name>/SKILL.md` stays where agents look),
- **survives upstream deletion** (a committed file copy, not just a git pointer).

## When to use
- User wants a `~/.agents`-style hub backed by GitHub (or any git remote).
- User wants third-party skills mirrored publicly without copy-pasting and losing provenance.
- User already symlinks the hub into projects (`ln -sfn ~/.agents <project>/.agents`) and you must not break that.

## Architecture (the working shape)
```
hub/                        ← git repo (the hub)
├── _vendor/                ← git SUBMODULES, one per upstream repo (clickable on GitHub → origin)
│   └── <repo>/             ← full upstream clone, pinned to a commit
├── skills/                 ← SYMLINKS → ../_vendor/<repo>/<skill-path>
│   └── <name>  ->  ../_vendor/<repo>/<skill-path>
├── _vendored_snapshot/     ← committed REAL copies (no .git) — survive deletion
├── scripts/snapshot.sh
├── README.md               ← attribution table + update workflow
├── LICENSE                 ← covers your files only; submodules keep their licenses
└── .gitignore              ← exclude nested .git in snapshots
```

## Why submodule-in-_vendor + symlink (not naive submodule)
Almost all agent skills live in **subfolders of large monorepos**, not as standalone
repos. A naive `git submodule add <repo> skills/<name>` nests the *entire* upstream
repo and breaks agent discovery:
`skills/<name>/skills/.../SKILL.md` instead of `skills/<name>/SKILL.md`.

The bridge fixes this: submodule the whole upstream under `_vendor/<repo>/`, then
symlink the exact skill subfolder into `skills/<name>`. Agents read the symlink
transparently; project symlinks (`ln -sfn ~/.agents <project>/.agents`) keep working
because they target the directory, not the git internals.

## Steps
1. `git init -b main` in the hub dir; `git remote add origin <url>`.
2. For each skill:
   - `git submodule add [-b main] <upstream-url> _vendor/<repo>`
   - `ln -s ../_vendor/<repo>/<skill-path> skills/<name>`
   - `git add skills/<name> _vendor/<repo>`
3. Write `README.md` with an attribution table (skill → upstream URL → license) and the
   update workflow. Add `LICENSE` (MIT) + `.gitignore` (`_vendored_snapshot/**/.git`).
4. Commit + push.
5. Run `bash scripts/snapshot.sh` to seed `_vendored_snapshot/`, commit, push.

## Update workflow (document in README)
```bash
cd <hub>
git pull
git submodule update --init --recursive     # after fresh clone on a new machine
git submodule update --remote --recursive    # refresh third-party to latest
bash scripts/snapshot.sh && git add -A && git commit -m "snapshot: $(date +%F)" && git push
```
Submodules **pin a commit** — "latest" only appears after `--remote`.

## Survival property (why the snapshot exists)
`_vendor/*` submodules store only a **gitlink + SHA** (a pointer), NOT the files. If an
upstream repo is deleted, a fresh clone or `git submodule update --remote` loses the
skill contents. `_vendored_snapshot/` holds real committed copies and survives that.
It is **restore-only** — agents keep reading `skills/*` (symlinks into `_vendor`).

## Pitfalls
- **Skills are subfolders of monorepos** → always submodule the repo root, symlink the
  skill path. Never `submodule add <repo> skills/<name>`.
- **Submodule `.git` is a gitlink FILE, not a dir** → `test -d .git` is false even when
  files are present and the submodule is initialized. Don't infer "not initialized" from that.
- **macOS default bash is 3.2** → `declare -A` (associative arrays) and `mapfile` are
  unreliable/absent. Write scripts with plain `while IFS='|' read` loops over
  `name|path` pairs. See `scripts/snapshot.sh` (known-good, bash 3.2 safe).
- **Snapshot script must exclude nested `.git`** or you commit submodule git metadata.
  Filter with `find . -path ./.git -prune -o -type f -print` and copy files only.
- **`gh repo edit --visibility`** needs `--accept-visibility-change-consequences` on
  gh ≥2.94 (otherwise it errors after listing every flag). See `references/gh-cli-gotchas.md`.
- **Don't hand-edit `~/.hermes/config.yaml`** for MCP servers — use `hermes mcp add`.
  In the desktop app, `/reload-mcp` is NOT in the slash palette; restart the app to
  pick up a new MCP server (CLI/TUI support it).
- **Symlinks in git**: `git add skills/<name>` stages the symlink itself (correct), not
  the target contents. Verify with `git ls-files --stage` (submodules show mode `160000`).

## Support files
- `scripts/snapshot.sh` — bash-3.2-safe snapshot of unpacked skills into `_vendored_snapshot/`.
- `references/gh-cli-gotchas.md` — `gh` visibility/bulk-edit gotchas that silently break scripts.
