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
plan-eng-review|_vendor/garrytan__gstack/plan-eng-review
taste-skill|_vendor/taste-skill__taste-skill/skills/taste-skill"

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
