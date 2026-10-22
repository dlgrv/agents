---
name: nas-backup-ops
description: Use for fleet server backups to the NAS (restic).
category: devops
---

# Fleet backups: servers A/C/D/E/F → NAS (restic over WireGuard)

Canonical detailed plan: `~/work/infra/docs/backup-nas-plan.md`. If this file and the plan disagree after implementation starts, update BOTH in the same run — the plan is the human-readable source, this skill is the operating procedure.

## Architecture (fixed decisions)

- restic, pull model: the NAS (10.0.0.4, behind office NAT) initiates sftp over wg0 with keepalive; hub A (10.0.0.1) forwards to C/D/E/F. Transport verified working.
- One restic repo per server under `<RAID>/backups/restic/<server>/` — isolation: a compromised host only endangers its own repo.
- Back up state+config+secrets ONLY. Never back up code (lives in git), docker images/containers, runner caches, redis, live GitLab data dir (use `gitlab-backup create` instead).
- Retention `--keep-daily 7 --keep-weekly 5 --keep-monthly 6 --prune` → 18 restore points per repo. No date-named directories: a snapshot's timestamp IS the date (`restic snapshots`); restoring to a date = `restic restore <snapshot-id>`.

## Restore difficulty map (before designing anything new, know this)

| Service | Ease | Critical dependency |
|---|---|---|
| PG dumps (bpm, prime_service) | легко | pg_restore; minutes |
| GitLab | средне | restore requires the SAME GitLab version as the backup tar AND `gitlab-secrets.json`/`gitlab.rb` — a tar without secrets is unusable |
| GitFlic | средне | volumes back + compose up; check rabbitmq/redis state assumptions |
| Static sites (D, configurator www) | легко | rsync back |
| F configurator-backend image | НЕВОЗМОЖНО из бэкапа | the image exists ONLY as local docker on F — if F dies, the image is gone unless rebuilt from source or pushed to a registry. Push it to a registry or back up `docker save` output |

## Pitfalls

- Losing a repo's restic password loses that repo's backups permanently — password copy lives on the NAS (root:0600) AND in the owner's password manager. Verify the off-NAS copy exists at init time.
- Sequential fetches only (A→C→D→E→F one after another): the office uplink is narrow; parallel pulls saturate it and stall every server's backup.
- RAID1 is not an independent copy: both disks share one enclosure. It survives one disk dying, not ransomware/fire/`rm -rf`. Monthly `mdadm` scrub is mandatory anyway (RAID1 silently tolerates divergence until scrub).
- `gitlab-backup create` skips the container registry by default — images are assumed rebuildable from source.
- F has no agent SSH access — commands there go through the owner (hand him ready-to-paste blocks).

## Implementation stages

1. Access: sftp-only user `bkp-restic` on A/C/D/E/F (internal-sftp, no shell, NAS's key only); firewall: allow tcp/22 from 10.0.0.4 on wg0 (C/D/E/F).
2. Staging crons on A (01:30 pg_dump bpm + gitlab-backup create), C (02:00), E (02:30) — dumps to `/var/backups/nas-staging/` with dates in filenames.
3. restic on NAS: install, init 5 repos, `nas-backup.sh`, first full pull (~14 GB, ceiling ~36 GB).
4. TEST RESTORE before declaring done: restore a bpm dump and a GitFlic volume into /tmp and verify they load.
5. Nightly cron (02:40 backups, Sat 05:00 `check --read-data-subset=10%`), `status.json` + Kuma alert if last success >26 h; close the PrimeBPM task.

## Open items at plan time

- The plan file's NAS paths/size are unverified (`/mnt/raid`, «2×2 ТБ»): the real array per nas-ops is mdadm `/dev/md127`, ext4, 2×4 TB mounted at `/srv/nas`. Fix the plan file at implementation start and pick the final root (do not collide with the Nextcloud borg dir `/srv/nas/backups`).
- Are `/opt/builds` firmwares in git/registry? If yes, drop 1.7 GB from F's scope.
- Is `/var/www/configurator` on F CI-deployed? If yes, it is droppable.
- Optional stage 2: weekly `restic copy` to a medium outside the RAID (USB or F's md44, 388 GB free).
