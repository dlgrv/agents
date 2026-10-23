---
name: nas-backup-ops
description: Use for fleet server backups to the NAS (restic).
category: devops
---

# Fleet backups: servers A/C/D/E/F → NAS (restic over WireGuard)

Implemented 2026-10-22, restore-tested 2026-10-23. Human-readable plan:
`~/work/infra/docs/backup-nas-plan.md`; restore runbook: `/srv/nas/backups/RESTORE.md`
(copy at `~/work/infra/docs/RESTORE-nas-backup.md`). If reality and docs disagree, fix BOTH.

## Architecture (as implemented)

- Pull via **sshfs**: NAS mounts each server's staging ro over WG (user `backup-restic`,
  sftp-only chroot `/var/backups`), restic reads locally → `/srv/nas/backups/restic/<host>`.
- One repo + own password per server. Password vars in `/etc/nas-backup/restic.env` have
  NO dashes: `RESTIC_PASSWORD_webmain`, `_crbsitmain`, `_crbsitstandby`, `_primepilotmain`,
  `_primepilotstandby`.
- Back up state+config+secrets ONLY (no code, no public images, no live GitLab dir —
  `gitlab-backup create` instead; `gitlab-secrets.json`+`gitlab.rb` ARE backed up).
- Non-public images → weekly `docker save` into staging (F: img-configurator-backend.tar.gz).
- Encryption: WG ChaChi20 channel + client-side restic AES-256. RAID1 md127 = both disks
  (user decision); off-NAS copy deferred (stage 5).

## Layout & schedule

- NAS: `/srv/nas/backups/{restic/<5 hosts>,etc/nas-backup/nas-backup.sh,logs/,status.json,RESTORE.md}`;
  secrets `/etc/nas-backup/{restic.env,id_ed25519,known_hosts}` 700/600 root (NOT on RAID).
- Servers: `/usr/local/bin/nas-staging.sh` + `/etc/cron.d/nas-staging` (644 root!) +
  `/etc/ssh/sshd_config.d/50-backup-restic.conf` + `/var/backups/nas-staging/`.
- Staging crons: A 01:30, C 02:00, D/E/F 02:30 (server-local). NAS pull 02:40.
  Sat 05:00 `restic check --read-data-subset=10%`; 1st of month 04:00 mdadm scrub md127.
- Retention 7d/5w/6m --prune, strict order backup → forget → prune. RPO ≤24h.

## Commands (on NAS, sudo)

```bash
source /etc/nas-backup/restic.env
export RESTIC_PASSWORD="$RESTIC_PASSWORD_webmain"      # pick host
R="-r /srv/nas/backups/restic/web-main"
restic $R snapshots / ls latest                       # points / contents
restic $R dump latest /mnt/staging/<host>/<file> > /tmp/x   # one file to stdout
```
Deliver to a server (transit via admin Mac): `ssh nas "sudo … dump …" | ssh web-main 'cat > /tmp/x'`.
Force a full cycle: `/usr/local/bin/nas-staging.sh` on each server as root, then
`/srv/nas/backups/etc/nas-backup/nas-backup.sh` on NAS.

## Restore difficulty (tested 2026-10-23)

| What | Status | Notes |
|---|---|---|
| bpm SQL dump → test DB | ✅ tested | 107 tables, users 53/53 |
| GitFlic volumes | ✅ md5 byte-exact | unpack into docker volume mountpoint |
| configurator image | ✅ docker load | 368 MB, loads fine |
| kuma.db | ✅ integrity_check ok | SQLite |
| GitLab full tar | ⚠️ untested | needs SAME version + secrets; quarterly drill |

## Coverage audit (run quarterly, before trusting the chain)

Method: inventory what each service NEEDS to come back up (docker ps -a + volumes,
systemd units, /etc, env files anywhere, PG dbs, root crontab) vs what staging actually
holds (`restic ls latest`); report per service covered/gap. Details: `references/coverage-audit.md`.

## Pitfalls (all hit during rollout)

- Find the HOST source path of container configs with `docker inspect <c> --format
  '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'` before adding them to
  staging — the in-container path is misleading (gitlab-runner config lives in
  /srv/gitlab-runner/config, ls /etc/gitlab-runner on the host fails silently in `tar
  --ignore-failed-read`).
- After ANY edit to nas-staging.sh: `bash -n`, re-run staging, then verify the new file
  exists in /var/backups/nas-staging — a sed that matched nothing still exits 0 and the
  gap stays invisible until the next restore attempt.
- When filtering `restic ls` output through grep, print the raw count first — a wrong
  filter pattern silently returns an empty-looking listing that reads as "repo is empty".
- `chown -R root:backup-restic $S` steals `.ssh` → sshd "Could not open user authorized keys".
  Keep `$S/.ssh` owned by backup-restic.
- sudo -S via ssh eats the first stdin line: write scripts to files, prepend password separately.
- NAS sudo password (user kbbs) ≠ fleet SUDO_PASSWORD; it's NAS_PASSWORD in ~/.hermes/.env.
- cron.d files MUST be 644 root or cron silently ignores them.
- Dashed env var names are invalid bash → generated without dashes.
- "post-quantum" ssh warnings from NAS are harmless; `ufw` needs full path + sudo -S.
- Sequential pulls only: office uplink is narrow.
- Losing a repo password loses the repo forever — NAS env + owner's password manager.

## Open items

- Kuma monitor on status.json age >26h — NOT implemented yet.
- Quarterly GitLab restore drill pending.
- Off-NAS second copy (stage 5) deferred by owner.
- GitFlic compose path on C not yet located (volumes ARE captured; find widened to
  maxdepth 4 across /opt /srv /root /home).
- Audit gaps fixed in staging script (bpm .env, gitlab-runner config, runner-config volume,
  configurator minio+builds volumes) — confirm they landed in the next nightly snapshot.
