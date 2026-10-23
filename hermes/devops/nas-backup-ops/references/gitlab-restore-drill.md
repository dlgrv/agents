# GitLab restore drill (quarterly)

Full `gitlab-backup restore` is destructive on prod (it wipes the live DB), so drill on a
throwaway container. Run it on the NAS: the repo is local there, zero network transit, and
prod on A is untouched. Never run this against the live GitLab.

## Procedure (NAS, sudo)

1. Pull artifacts from the snapshot into a tmp dir (NOT /srv/nas/backups):
   `gitlab_backup.tar`, `gitlab-secrets.json`, `gitlab.rb` via
   `restic -r /srv/nas/backups/restic/web-main dump latest /mnt/staging/web-main/<f>`. Fixate md5 of the tar.
2. `docker pull gitlab/gitlab-ce:<EXACT-PROD-VERSION>-ce.0` — restore between versions fails;
   read the version from the tar filename (`<ts>_<date>_<ver>_gitlab_backup.tar`).
3. Run a throwaway container with NO published ports (verification is CLI-only):
   volumes `.../config:/etc/gitlab`, `.../data:/var/opt/gitlab`, `--shm-size 256m`.
4. Wait for `gitlab-ctl status puma` to show `run:` (first boot reconfigures ~5–10 min),
   then `docker cp` gitlab-secrets.json into /etc/gitlab/ — without prod secrets (db_key_base)
   passwords still work but 2FA secrets, CI variables and runner tokens decrypt to garbage.
5. Place the tar in /var/opt/gitlab/backups/, `chown git:git`, stop puma+sidekiq,
   `gitlab-backup restore BACKUP=<ts>_<date>_<ver> force=yes` (~15–30 min for ~10 GB).
6. `gitlab-ctl reconfigure && gitlab-ctl restart`, wait, then verify:
   - `gitlab-rails runner 'puts Project.count; puts User.count'` vs prod counts — users and
     bcrypt password hashes live in the restored DB, everyone logs in with their old password;
   - per-project `p.full_path` + `p.statistics.repository_size` vs prod;
   - live read: `git log` and `count-objects -vH` inside a restored bare repo under
     /var/opt/gitlab/git-data/repositories — proves the code base, not just metadata.
7. Teardown: `docker rm -f <c>`, delete container volumes and tmp dir — the tar plus the
   unpacked git-data is ~30 GB. Do not leave the test GitLab running (it eats RAM the
   Nextcloud/Kuma containers need).

Known gap covered by this drill: CI variables and runner tokens only survive if step 4's
secrets.json is present; if a restore drill skips it, runners re-auth fails and CI configs
read empty — that is a secrets-backup failure, not a restore failure.
