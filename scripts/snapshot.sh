#!/usr/bin/env bash
#
# snapshot.sh — back up the *unpacked* third-party skills into _vendored_snapshot/
# so the files survive even if an upstream repo is deleted from GitHub.
#
# The _vendor/* submodules only store a pointer (gitlink + SHA). This script
# copies the real files (minus any nested .git) into _vendored_snapshot/<name>/,
# which IS committed to the superproject. Agents do NOT read from here — they
# use skills/* (symlinks into _vendor). This dir is restore-only.
#
# Usage:  bash scripts/snapshot.sh
#
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SNAP="$ROOT/_vendored_snapshot"
mkdir -p "$SNAP"

# name|path-inside-_vendor  (one per line)
PAIRS="karpathy-guidelines|_vendor/multica-ai__andrej-karpathy-skills/skills/karpathy-guidelines
improve-codebase-architecture|_vendor/mattpocock__skills/skills/engineering/improve-codebase-architecture
thermo-nuclear-code-quality-review|_vendor/cursor__plugins/cursor-team-kit/skills/thermo-nuclear-code-quality-review
shadcn|_vendor/shadcn-ui__ui/skills/shadcn
sepia|_vendor/Nanako0129__sepia/skills/sepia
plan-eng-review|_vendor/garrytan__gstack/plan-eng-review
taste-skill|_vendor/taste-skill__taste-skill/skills/taste-skill
hallmark|_vendor/Nutlope__hallmark/skills/hallmark
anti-slop|_vendor/rand__cc-polymath/skills/anti-slop
brainstorming|_vendor/obra__superpowers/skills/brainstorming
dispatching-parallel-agents|_vendor/obra__superpowers/skills/dispatching-parallel-agents
executing-plans|_vendor/obra__superpowers/skills/executing-plans
finishing-a-development-branch|_vendor/obra__superpowers/skills/finishing-a-development-branch
receiving-code-review|_vendor/obra__superpowers/skills/receiving-code-review
requesting-code-review|_vendor/obra__superpowers/skills/requesting-code-review
subagent-driven-development|_vendor/obra__superpowers/skills/subagent-driven-development
systematic-debugging|_vendor/obra__superpowers/skills/systematic-debugging
test-driven-development|_vendor/obra__superpowers/skills/test-driven-development
using-git-worktrees|_vendor/obra__superpowers/skills/using-git-worktrees
using-superpowers|_vendor/obra__superpowers/skills/using-superpowers
verification-before-completion|_vendor/obra__superpowers/skills/verification-before-completion
writing-plans|_vendor/obra__superpowers/skills/writing-plans
writing-skills|_vendor/obra__superpowers/skills/writing-skills
caveman|_vendor/JuliusBrussee__caveman/skills/caveman
caveman-commit|_vendor/JuliusBrussee__caveman/skills/caveman-commit
caveman-compress|_vendor/JuliusBrussee__caveman/skills/caveman-compress
caveman-discover|_vendor/JuliusBrussee__caveman/skills/caveman-discover
caveman-evidence-review|_vendor/JuliusBrussee__caveman/skills/caveman-evidence-review
caveman-explore|_vendor/JuliusBrussee__caveman/skills/caveman-explore
caveman-help|_vendor/JuliusBrussee__caveman/skills/caveman-help
caveman-learn|_vendor/JuliusBrussee__caveman/skills/caveman-learn
caveman-manage|_vendor/JuliusBrussee__caveman/skills/caveman-manage
caveman-optimize|_vendor/JuliusBrussee__caveman/skills/caveman-optimize
caveman-review|_vendor/JuliusBrussee__caveman/skills/caveman-review
caveman-setup|_vendor/JuliusBrussee__caveman/skills/caveman-setup
caveman-stats|_vendor/JuliusBrussee__caveman/skills/caveman-stats
investigate-first|_vendor/JuliusBrussee__caveman/skills/investigate-first
lean-build|_vendor/JuliusBrussee__caveman/skills/lean-build
safe-refactor|_vendor/JuliusBrussee__caveman/skills/safe-refactor
surgical-patch|_vendor/JuliusBrussee__caveman/skills/surgical-patch
verify-and-stop|_vendor/JuliusBrussee__caveman/skills/verify-and-stop"

echo "$PAIRS" | while IFS='|' read -r name src; do
  [ -z "$name" ] && continue
  src="$ROOT/$src"
  dst="$SNAP/$name"
  if [ ! -d "$src" ]; then
    echo "SKIP  $name — source missing: $src (run: git submodule update --init)"
    continue
  fi
  rm -rf "$dst"
  mkdir -p "$dst"
  # copy files, excluding nested .git metadata
  ( cd "$src" && find . -path ./.git -prune -o -type f -print ) | while read -r f; do
    mkdir -p "$dst/$(dirname "$f")"
    cp -R "$src/$f" "$dst/$f"
  done
  n=$(find "$dst" -type f | wc -l | tr -d ' ')
  echo "SNAP  $name — $n files -> _vendored_snapshot/$name"
done

echo
echo "Done. Review with: git status _vendored_snapshot/"
echo "Commit & push:  git add -A && git commit -m \"snapshot: $(date +%F)\" && git push"
