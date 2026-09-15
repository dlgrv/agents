#!/bin/bash
# skills-sync: bidirectional skills sync between this machine and dlgrv/agents (hermes/ subtree)
# Installed on both Mac (launchd) and server (cron). Run every 15 min.
set -uo pipefail

HUB="${HUB_DIR:-$HOME/.agents}"          # mac: ~/.agents ; server: /root/github/agents
SKILLS="${SKILLS_DIR:-$HOME/.hermes/skills}"
HOSTNAME_TAG="$(hostname -s)"
LOG="${LOG_FILE:-$HOME/.hermes/logs/skills-sync.log}"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [$HOSTNAME_TAG] $*" >> "$LOG"; }

cd "$HUB" || { log "FATAL: hub dir $HUB missing"; exit 1; }

# Fetch remote first
git fetch origin main 2>>"$LOG" || { log "WARN: fetch failed (offline?)"; exit 0; }

LOCAL_AHEAD=$(git rev-list --count origin/main..main 2>/dev/null || echo 0)
REMOTE_AHEAD=$(git rev-list --count main..origin/main 2>/dev/null || echo 0)

# 1) Pull remote changes (rebase local commits on top)
if [ "$REMOTE_AHEAD" -gt 0 ]; then
  if git pull --rebase --autostash origin main >> "$LOG" 2>&1; then
    log "pulled $REMOTE_AHEAD commit(s) from origin"
  else
    log "ERROR: rebase conflict — left for manual resolution"
    git rebase --abort 2>/dev/null
    exit 1
  fi
fi

# 2) Mirror working skills into the repo (server/mac wins on content — last writer commits)
RSYNC_EXIT=0
rsync -a --delete \
  --exclude '.bundled_manifest' --exclude '.curator_ledger.jsonl' --exclude '.curator_state' \
  --exclude '.hub/' --exclude '.usage.json' --exclude '.usage.json.lock' \
  "$SKILLS/" "$HUB/hermes/" || RSYNC_EXIT=$?
if [ $RSYNC_EXIT -ne 0 ]; then log "ERROR: rsync failed ($RSYNC_EXIT)"; exit 1; fi

# 3) Commit + push if anything changed
if [ -n "$(git status --porcelain -- hermes/)" ]; then
  git add hermes
  if git commit -m "auto: skills sync from $HOSTNAME_TAG" >> "$LOG" 2>&1; then
    if git push origin main >> "$LOG" 2>&1; then
      log "pushed changes from $HOSTNAME_TAG"
    else
      log "WARN: push failed — will retry next cycle"
    fi
  fi
else
  log "no changes"
fi
