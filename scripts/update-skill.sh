#!/usr/bin/env bash
# Refresh one inlined skill from its upstream repo.
# Usage: ./scripts/update-skill.sh <skill-name> [subpath-in-upstream-repo]
#
# Reads the upstream URL from the README attribution table, clones it shallow,
# copies the skill subfolder over skills/<name>/ and leaves the rest to you.
#
# Examples of subpath:
#   ./scripts/update-skill.sh karpathy-guidelines skills/karpathy-guidelines
#   ./scripts/update-skill.sh shadcn skills/shadcn
set -euo pipefail

name="${1:?usage: update-skill.sh <skill-name> [subpath-in-upstream-repo]}"
subpath="${2:-}"

# 1) find upstream URL in the README attribution table
repo_url=$(awk '/^## Attribution/,/^## [^A]/' README.md | grep "skills/$name" | grep -o 'https://github.com/[^) ]*' | head -1)
if [ -z "$repo_url" ]; then
  echo "error: no upstream URL found for '$name' in README attribution table" >&2
  exit 1
fi

# 2) shallow-clone upstream to a temp dir
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git clone --depth 1 --quiet "$repo_url" "$tmp/repo"
echo "cloned: $repo_url -> $tmp/repo"

# 3) copy the skill subfolder over the inlined copy
if [ -z "$subpath" ]; then
  echo
  echo "skill subfolder path inside the upstream repo is repo-specific;"
  echo "copy it manually, then commit:"
  echo "  rsync -a --delete <path-in-$tmp/repo>/ skills/$name/"
  echo "  git add skills/$name && git commit -m 'update $name from upstream'"
  exit 0
fi

src="$tmp/repo/$subpath"
if [ ! -d "$src" ]; then
  echo "error: $src does not exist in $repo_url" >&2
  exit 1
fi

rsync -a --delete "$src/" "skills/$name/"
echo "updated skills/$name from $repo_url ($subpath)"
echo "now: git add skills/$name && git commit -m 'update $name from upstream'"
