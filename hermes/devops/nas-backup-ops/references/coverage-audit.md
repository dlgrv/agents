# Backup coverage audit: live services vs restic snapshots

Run quarterly or after any new service. Goal: prove every service can be restored from
`/srv/nas/backups/restic/<host>` alone (plus git registries).

## 1. Inventory per server (what restore actually needs)

```bash
PW=$(grep -E "^SUDO_PASSWORD=" ~/.hermes/.env | cut -d= -f2- | tr -d '"')
printf '%s\n' "$PW" | ssh <host> "sudo -S -p '' bash -s" <<'EOS'
docker ps -a --format '{{.Names}} | {{.Image}}'
docker volume ls -q
ls /etc/systemd/system/*.service | xargs -n1 basename
sudo -u postgres psql -t -c 'select datname from pg_database where not datistemplate'
ls /etc/nginx/sites-enabled/ /var/www/ /opt/
crontab -l | grep -v '^#'
EOS
```
For F: `ssh -i ~/.ssh/id_ed25519_crbsit_ldolgirev ldolgirev@94.26.228.62`.

## 2. Diff against staging

On NAS: `restic -r /srv/nas/backups/restic/<host> ls latest` (see SKILL.md for password
vars). Compare file-by-file against step 1.

## 3. Checklist of commonly missed items

- **.env / secrets files OUTSIDE /etc** — e.g. app dirs under /opt. Code is in git, its
  env is not; without it the service will not start after restore.
- **Container configs**: resolve real host paths via `docker inspect ... Mounts` (see
  pitfall in SKILL.md), then check they are in the /etc tar or staged explicitly.
- **Docker volumes holding DATA** (not cache): tar them into staging like the GitFlic
  volumes. Tiny volumes (a few hundred KB) are still state.
- **Compose files / launch units** for docker stacks — without them nobody knows how the
  stack starts. If not found by find, record as open item.
- Consciously-excluded (fine): redis/rabbitmq state, runner caches, registry images
  (CI rebuilds), code in git. List them in the report as "accepted", not "gap".

## 4. Report shape

Table: service | covered items | gaps. Then fix gaps in /usr/local/bin/nas-staging.sh
(edit → `bash -n` → re-run → verify file appears in staging), update backup-nas-plan.md
and this skill in the same pass.
