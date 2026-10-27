# HTLB Translation Watchdog Script

Script: `/root/.hermes/scripts/htlb-watchdog.sh`

Purpose: Monitor HTLB translation runs for stalled chapters or completed work.

## Logic

- Silent when all is progressing normally
- Reports only when something is wrong:
  - Chapter stalled: no writes for 40+ minutes
  - Chapter complete: all units translated
- Uses marker files to avoid duplicate notifications

## Usage

```bash
# Run manually (for testing)
bash /root/.hermes/scripts/htlb-watchdog.sh

# Set up as cron job (once per session)
cronjob_manage action=create name=htlb-translation-watchdog no_agent=true script=htlb-watchdog.sh schedule="30m"
```

## Script Implementation

```bash
#!/bin/bash
# Watchdog: HTLB translation subagents at /root/htlb-run/<NN>/units/
# Silent when everything is fine. Reports only:
#  - stall: no writes to a chapter's units for 40+ minutes
#  - complete: all units of a chapter translated (dedup via marker file)
cd /root/github/HowToLiveBetter || exit 0
STATE=/root/htlb-run/.notified
touch "$STATE"
for n in 12 14 16 18 19; do
  d=/root/htlb-run/$n/units
  s=/root/github/HowToLiveBetter/tools/digest/$n/units
  [ -d "$d" ] || continue
  exp=$(ls $s/*.md 2>/dev/null | wc -l)
  done_u=$(grep -L '§TAG§' $d/*.md 2>/dev/null | wc -l)
  if [ "$done_u" -eq "$exp" ] && [ "$exp" -gt 0 ]; then
    if ! grep -q "^$n$" "$STATE"; then
      echo "$n" >> "$STATE"
      echo "ch.$n COMPLETE: $done_u/$exp units translated"
    fi
    continue
  fi
  newest=$(ls -t $d/*.md 2>/dev/null | head -1)
  [ -z "$newest" ] && continue
  age=$(( ($(date +%s) - $(stat -c %Y "$newest")) / 60 ))
  if [ "$age" -ge 40 ]; then
    echo "ch.$n STALLED: $done_u/$exp translated, no writes for ${age} min"
  fi
done
```

## Pitfalls

- Only reports when something is wrong or complete; silent during normal progress
- Uses marker file to avoid duplicate completion notifications
- Expects units to have §TAG§ placeholder; translated units remove it
- Must be run from ~/github/HowToLiveBetter for path consistency