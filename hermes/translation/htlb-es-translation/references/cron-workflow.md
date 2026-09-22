# Cron workflow management (HTLB ES translation)

## Rule

Before submitting PRs or merging, pause cron jobs (e.g. `hermes cron pause <job-id>`) to prevent automatic runs that may overwrite local changes or cause conflicts. Use `hermes cron list` to find job IDs and `hermes cron resume` to restore.

## Why

HTLB translation runs cron jobs (e.g. `htlb-es-watchdog` every 5 min) that automatically fetch upstream changes and update local files. If these run during active PR work, they may overwrite local commits, cause merge conflicts, or trigger CI on stale local states.

## Procedure

```bash
# List active cron jobs
hermes cron list
# Pause relevant jobs (e.g. htlb-es-watchdog)
hermes cron pause <job-id>
# ... do PR work (commits, pushes, merges) ...
# Resume after merge
hermes cron resume <job-id>
```

## Pitfall

Never let cron watchdogs run during active PR work — they may fetch upstream changes and overwrite your local commits, especially when working on parser fixes or page regeneration.
