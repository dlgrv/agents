# Backup audit — fleet A/C/D/E/F + NAS (2026-10-22)

Fleet facts: **server B does not exist** (dropped from all plans). sshd on E/F
(and any new server) is `prohibit-password` — password auth over SSH is
impossible; `SUDO_PASSWORD` from `~/.hermes/.env` works ONLY as remote sudo
piped over key-based SSH (`echo "$PW" | ssh host "sudo -S -p '' ..."`).
sshpass exists on the Mac but is useless for these hosts.

## What to back up (restic, pull from NAS over WireGuard)

| Server | Paths / sources | Size |
|---|---|---|
| A web-main 109.236.57.134 | `/srv/backups` (gitlab-backup tars) + `/srv/gitlab/config` (gitlab-secrets.json, gitlab.rb — backup tar excludes them); pg_dump of `bpm` DB (70 MB); `/opt/prime-bpm`; Kuma docker volume; `/etc/nginx` | ~9.2 GB |
| C crbsit-main | GitFlic docker volumes: `gitflic_data` (1.3G), `repository-a7502f7d-…` (1.5G — the repos), `gitflic_etc`, `gitflic_cert`; pg_dump from the `postgres` container (pg_data 87 MB) | ~2.9 GB |
| D crbsit-standby | `/var/www/crbsit.ru` (594 MB) + `/etc/nginx`; no DB, no etcd, static lands via CI deploys directly | ~0.6 GB |
| E primepilot-main 94.26.229.45 | pg_dump `prime_service` (9 MB; deployer sudo is restricted — connect over TCP 127.0.0.1 with creds from `/opt/license-service/backend/.env`, source it with `set -a` — naive `cut -d=` breaks on values with `=`); `/opt/license-service` (+.env); `/var/www/license-service`; `/etc/opendkim/keys/primepilot.tech` (mail breaks without it); postfix+nginx config | ~0.15 GB |
| F primepilot-standby | `/var/www/configurator` (468 MB), `/opt/builds` (1.7 GB — firmware/releases, ONLY copy in existence), configurator-backend compose config | ~2.2 GB |

**Excluded (never back up):** GitLab runner cache volumes (~14 GB, recreate),
`/srv/gitlab/data` live dir (42 GB — use `/srv/backups` tars instead, best
practice), redis, `/srv/gitlab/logs`.

## Sizing / retention
- First full snapshot ≈ **15 GB** (~20 GB with slack).
- Retention 7d/5w/6m with restic dedup → ceiling ≈ **50 GB**. NAS 2×2 TB —
  trivial fit; nightly incrementals are tens–hundreds of MB.
- Pattern: restic **pull** from NAS (sftp-only users per server), not push.
- Cron prerequisites: pg_dump jobs on A (bpm) and E (prime_service);
  gitlab-backup schedule already produces `/srv/backups` tars on A.

## Gotchas
- F has **no Postgres** — E→F replication not set up yet; the only primepilot
  DB copy is E's dump, which raises its priority.
- Existing `/srv/backups` on A (8.3 GB) already holds ready GitLab tars —
  back that dir up, not the live data dir.
- D has `/etc/cron.d/uptime-kuma-host` (host-check pusher, not a backup job).
- nginx sites on F live outside `sites-enabled/` (grep came back empty) —
  back up `/etc/nginx` wholesale.