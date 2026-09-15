---
name: agent-skills-hub
description: "Own agent-config hub (~/.agents): inlined third-party skills with attribution, subagents + Cursor rules with whole-dir symlinks into app config dirs; PR-based workflow."
version: 1.2.0
author: dlgrv
license: MIT
metadata:
  hermes:
    tags: [git, github, submodules, agent-skills, dotfiles, skills-hub]
    related_skills: [github-repo-management, github]
---

# Agent Skills Hub (submodule + symlink bridge)

> **For dlgrv/agents specifically:** the live hub moved past submodules (PR #6,
> 2026-09-08) — third-party skills are inlined real copies, subagents/rules use
> whole-dir symlinks. See "Backup against upstream deletion → ARCHITECTURE" below
> and `references/recipe.md`'s superseded banner before re-applying any submodule
> commands there. The submodule/bridge technique below remains valid for OTHER
> hubs where a thin pointer to upstream is actually wanted.

Turn a local skills directory (e.g. `~/.agents`, `~/.claude/skills`) into a public or
private git repo that collects **third-party skills scraped from GitHub**, while:

- Keeping **attribution** (one click from your repo → the origin repo on GitHub).
- Not breaking **agent discovery** (`skills/<name>/SKILL.md` must resolve directly).
- Preserving an existing `ln -sfn <hub> <project>/.agents` workflow (the hub stays a
  plain directory on disk; submodules/symlinks are transparent to it).

## When to use
- "Mirror my `~/.agents` skills to a GitHub repo."
- "Keep third-party agent skills versioned but link back to their sources."
- "Make a public showcase of the skills I use (for profile/achievements)."
- "Back up my skills hub in case an upstream repo gets deleted."

## Core technique (the non-obvious part)

Third-party skills almost always live in a **subfolder of a larger upstream monorepo**
(e.g. `shadcn` is at `shadcn-ui/ui/skills/shadcn`, not its own repo).

❌ **Naive:** `git submodule add <repo> skills/<name>`
→ nests the ENTIRE upstream repo, so agents see `skills/<name>/skills/.../SKILL.md`
and fail to discover it.

✅ **Bridge pattern:**
1. Submodule the **whole upstream repo** under `_vendor/<repo>/`.
2. Put a **symlink** in `skills/<name>` → `../_vendor/<repo>/<skill-path>`.

Agents read the symlink transparently (still `skills/<name>/SKILL.md`); GitHub shows
`_vendor/<repo>` as a clickable ⤵ submodule → origin.

## Steps
0. **Backup:** `cp -R ~/.agents ~/.agents.bak`
1. **Create empty repo:** `gh repo create <you>/agents --public --description "..."`
   (do NOT add README/license yet — init in the existing dir).
2. **Init local git:** `cd ~/.agents && git init -b main && git remote add origin git@github.com:<you>/agents.git`
3. **Per skill:**
   ```bash
   rm -rf skills/<name>                                   # safe verbatim upstream copy
   git submodule add -b <branch> git@github.com:<up>/<repo>.git _vendor/<repo>
   ln -s ../_vendor/<repo>/<skill-path> skills/<name>
   git add skills/<name> _vendor/<repo>
   ```
   Use `-b main` when the upstream default branch is `main`; omit for detached tags.
4. **README** with attribution table (upstream + skill path) + update commands.
5. **LICENSE** (MIT for your files; submodule contents keep upstream licenses).
6. **Commit + push:** `git add -A && git commit -m "..." && git push -u origin main`
7. **Verify** with a fresh clone (see references/recipe.md).

## Pitfalls
- **GitHub repo names cannot start with a dot** → use `agents`, not `.agents`.
- **Submodules pin a commit** — "latest" only after `git submodule update --remote`.
- **Fresh clone shows `-` (uninitialized) in `git submodule status`** → must run
  `git submodule update --init --recursive` before skills resolve. Verify this!
- **SSH auth** must work for submodule clone (`git@github.com:...`); test with
  `ssh -T git@github.com` first. Fall back to HTTPS if no key.
- **Keep symlink targets relative** (`../_vendor/...`) so the repo works on any machine.
- See `references/recipe.md` for the exact command sequence that was validated.
- **`git add -A` on a hybrid tree re-stages removed submodule metadata**: after
  `git rm --cached _vendor/...`, a following `git add -A` re-added `_vendored_snapshot/`
  and `.gitmodules` back into the index; the amend only removed `_vendor`. Fix:
  explicit adds (`git add skills/ scripts/ README.md`) or verify with
  `git ls-files | grep <path>` before amending.

## Branch + PR workflow (user-mandated)
The user requires **no direct pushes to `main`** — every change goes through a feature
branch + pull request + merge. Encode this as the default, not an exception:

```bash
git checkout -b feat/<name>          # branch off clean main
# ... make changes, git add, git commit ...
git push -u origin feat/<name>
gh pr create --base main --head feat/<name> --title "..." --body "..."
gh pr merge <N> --merge --delete-branch
```

Keep `main` untouched until the PR is merged. After merge, `git checkout main && git pull`
to sync the local hub; the working symlinks are unaffected.

## Backup against upstream deletion → ARCHITECTURE: inline real copies (PR #6)

**2026-09-08, PR #6: the submodule bridge (`_vendor/` + symlinks +
`_vendored_snapshot/`) is REPLACED by inlined real copies.** `skills/<name>/` now
holds the actual files with an attribution table in the README (upstream + path).
Why: submodules were the main pain — dirty working copies inside vendored repos
(` m` drift), init-on-fresh-clone failures, `git rm --cached` vs `git add -A`
index fights. Real copies are self-contained and survive upstream deletion by
definition. Per-skill refresh: `bash scripts/update-skill.sh <name>` (replaces
snapshot.sh; hash-verifies fetched content against the pinned commit so drift is
explicit before overwriting).

Pre-PR#6 snapshot mechanics kept below for reference on old clones:

1. `scripts/snapshot.sh` copied each unpacked skill's files (excluding nested
   `.git`) into `_vendored_snapshot/<name>/` as plain files.
2. `_vendored_snapshot/` was restore-only; `.gitignore` carried
   `_vendored_snapshot/**/.git`.

## Update workflow (document in README)
```bash
cd ~/.agents
git pull
git submodule update --init --recursive     # fresh clone (pre-PR#6 layout only)
git submodule update --remote --recursive    # refresh third-party to latest
```
Post-PR#6 (inlined copies) the per-skill refresh is:
`bash scripts/update-skill.sh <name>` — refetches that skill's upstream subtree and
hash-verifies against the pinned commit before overwriting.

## Adding a new third-party skill later
`git submodule add <url> _vendor/<repo>` → `ln -s ../_vendor/<repo>/<path> skills/<name>` → `git add` both.

## Your own (non-third-party) content
Prompts, `AGENTS.md`, `CLAUDE.md`, notes → commit as normal files, no submodule.
The repo grows horizontally without rework. To patch an upstream skill yourself,
point that one submodule's URL at your fork.

### Agent config files belong in the hub too (validated 2026-09)
The "single source of truth + symlink" pattern extends beyond skills to **agent
config**. Unified layout (works because Cursor reads the Claude-Code subagent
format and even `~/.claude/agents/` natively):

- `subagents/*.md` — own subagents, ONE source dir, symlinked WHOLE into BOTH apps.
- `cursor/rules/*.mdc` — Cursor-only global rules (`.mdc` is a Cursor format; no
  cross-agent standard for global rules exists).

**Whole-DIRECTORY symlinks, not per-file (final pattern, 2026-09-08).** Linking the
dir once means new files in the hub appear in every app automatically — no extra
symlink per subagent/rule (user pushed back on per-file links: "why not symlink the
directory at once?"):

```bash
ln -sfn ~/.agents/subagents    ~/.cursor/agents   # one dir doubles for both apps
ln -sfn ~/.agents/subagents    ~/.claude/agents
ln -sfn ~/.agents/cursor/rules ~/.cursor/rules
# per project (documented rules location — the guaranteed one):
mkdir -p <project>/.cursor/rules && ln -sfn \
  ~/.agents/cursor/rules/delegation.mdc <project>/.cursor/rules/delegation.mdc
```

Edit in the hub → every linked app sees the change; git history covers config.
Note: a `model:` field like `composer-2.5` is Cursor-specific — Claude Code ignores
unknown model ids and falls back to its default (harmless).
Caveat to mention to the user: app-written files inside a dir-symlinked target land
in the hub's git — acceptable (history of everything), just be aware.
Current instance: token-saving delegation (bulk-reader / boilerplate-writer
subagents + delegation.mdc), inspired by Spotify's shunt pattern. Full detail,
Cursor-specific gotchas and the hooks alternative: `references/cursor-delegation.md`.

Pitfall: **`~/.cursor/rules/` is not an officially documented rules source**
(User Rules via Settings→Rules are; `~/.cursor/agents/` IS documented user scope
for subagents). For guaranteed rule enforcement, symlink the .mdc into each
project's `.cursor/rules/` — the user picked per-project wiring (option 2) over
the undocumented global path. Rule files should be project-agnostic (no hardcoded
paths/names) so one hub file serves every project.
