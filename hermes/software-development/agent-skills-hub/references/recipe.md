# Validated recipe: ~/.agents → public dlgrv/agents hub

> **SUPERSEDED (PR #6, 2026-09-08):** the hub no longer uses submodules —
> `skills/<name>/` holds inlined real copies with README attribution, refreshed via
> `scripts/update-skill.sh <name>`. This recipe is kept for historical reference and
> for repairing any pre-PR#6 clone (old forks, other machines). Do NOT re-apply the
> submodule bridge to the current hub.

Captured from a real run (all 5 submodules cloned, symlinks resolved, fresh-clone
verified). Full-history clone (no `--depth`) was used per user preference.

## Upstream map (verified against local SKILL.md frontmatter)
| Local skill | Upstream repo | Skill path in repo |
|---|---|---|
| karpathy-guidelines | multica-ai/andrej-karpathy-skills | skills/karpathy-guidelines |
| improve-codebase-architecture | mattpocock/skills | skills/engineering/improve-codebase-architecture |
| thermo-nuclear-code-quality-review | cursor/plugins | cursor-team-kit/skills/thermo-nuclear-code-quality-review |
| shadcn | shadcn-ui/ui | skills/shadcn |
| plan-eng-review | garrytan/gstack | plan-eng-review |

## Commands (in order)
```bash
# 0. backup
cp -R ~/.agents ~/.agents.bak

# 1. empty public repo
gh repo create dlgrv/agents --public --description "Central hub of third-party agent skills."

# 2. init in existing dir
cd ~/.agents && git init -b main && git remote add origin git@github.com:dlgrv/agents.git

# 3. per skill (example: karpathy-guidelines)
rm -rf skills/karpathy-guidelines
git submodule add -b main git@github.com:multica-ai/andrej-karpathy-skills.git _vendor/multica-ai__andrej-karpathy-skills
ln -s ../_vendor/multica-ai__andrej-karpathy-skills/skills/karpathy-guidelines skills/karpathy-guidelines

# repeat for the other 4 with their upstream/repo/path (see table above)

# 4-5. write README (attribution table) + LICENSE (MIT, note submodules keep upstream)
# 6. commit + push
git add -A && git commit -m "Add agent skills hub: submodules + symlink bridge" && git push -u origin main

# 7. verify with FRESH clone (critical — proves it works for others)
cd /tmp && rm -rf agents-check && git clone git@github.com:dlgrv/agents.git agents-check
cd agents-check && git submodule update --init --recursive
for s in skills/*/; do test -f "$s/SKILL.md" && echo "OK $s" || echo "MISS $s"; done
```

## What to expect
- `git submodule status` shows ` ` (space) prefix once initialized, `-` before init.
- GitHub shows `_vendor/<repo>` with a ⤵ icon; clicking opens the origin repo.
- A fresh clone WITHOUT `submodule update` shows skills as broken symlinks → that's
  expected; the README update section must document the `--init --recursive` step.

## Notes
- `_vendor/<repo>` dir names use double-underscore `__` to flatten `owner/repo`.
- Symlinks are relative (`../_vendor/...`) so they survive a clone to any path.
- SSH worked (`ssh -T git@github.com` → "Hi dlgrv!"). If it fails, switch submodule
  URLs to `https://github.com/<up>/<repo>.git`.
