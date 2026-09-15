#!/usr/bin/env bash
# Verify a filed GitHub issue by reading it back + re-check dupes.
# Usage: verify-issue.sh <owner/repo> <issue-number>
set -euo pipefail
REPO="$1"; NUM="$2"
gh issue view "$NUM" --repo "$REPO" --json number,title,state,url,author,labels \
  --jq '{number, title, state, url, author: .author.login, labels: [.labels[].name]}'
echo "--- dupe re-check (first words of the title) ---"
KEY=$(gh issue view "$NUM" --repo "$REPO" --json title --jq .title | cut -d' ' -f1-4)
gh search issues --repo "$REPO" "$KEY" --limit 5 \
  --json number,title,state --jq '.[] | "\(.number) [\(.state)] \(.title)"'
