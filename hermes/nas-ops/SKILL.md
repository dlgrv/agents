---
name: nas-ops
description: Use when working on the office NAS via SSH.
category: devops
---

# Office NAS operations

Ubuntu NAS (X99M-H, 12 threads, 30 GiB RAM, NVMe 240G system) serving ~10 non-technical employees. Target architecture: personal-cloud Nextcloud AIO in Docker, HTTPS reachable ONLY from the tailnet (office is behind CGNAT, no public ports).

## Storage decision (final, user-approved)

- Keep the EXISTING mdadm RAID1 (`/dev/md127`, ext4, mounted at `/srv/nas`, 2×4TB). NO ZFS, no pool creation, no teardown — the user explicitly cancelled ZFS after learning the tradeoffs.
- Compensations chosen for ext4's lack of snapshots: frequent (daily) borg backup of AIO + offsite copy on the admin's machine. State this honestly in docs: a backup on the same array does not protect against array loss/ransomware.
- Monitoring stack is ext4-native: smartd (scheduled self-tests) + `mdadm --monitor` (MAILADDR alert on array degradation). No zfs-zed/scrub — do not reintroduce ZFS tooling.
- Data dirs on the array: `/srv/nas/nextcloud-data` and `/srv/nas/backups`, `chmod 0770` on the empty datadir (AIO requirement for first launch) — chmod only, never chown.

## Access

- `ssh nas` — alias in `~/.ssh/config` → `kbbs@100.69.213.39` (Tailscale IP). Key `~/.ssh/id_ed25519_crbsit_ldolgirev` has a non-standard name, so SSH does not offer it by default; the alias carries `IdentityFile` — use the alias, not a bare `ssh kbbs@100.x.x.x`.
- `kbbs` has full sudo. The sudo password is typed by the user, never by the agent and never in chat.
- The tailnet is foreign (shared from another account): ACLs, tags and device tagging are edited by the tailnet owner in the admin console, not by us. Plan around this or move the NAS to the user's own tailnet.

## Tailscale connectivity first

- Before any NAS work, confirm `tailscale status` lists the NAS. If it prints `Tailscale is stopped.`, revive the macOS GUI client with `/Applications/Tailscale.app/Contents/MacOS/Tailscale up` — the bare `tailscale` binary is not in PATH; the app bundle CLI is the one that works. Wait ~3s after `up` before ssh.

## Live audit over SSH

- Plain `ssh nas 'sudo ...'` fails with "interactive authentication is required". Batch ALL sudo-needing commands into one `ssh -t nas '...'` session — the first sudo caches the credential, so the user types the password once, not once per command.
- Readable without sudo (do these first, cheap): `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,SERIAL`, `free -h`, `df -h`, `cat /proc/mdstat`, `timedatectl`, `apt list --upgradable`, `snap list`, `systemctl is-active <svc>`.
- `smartctl -H` and `ufw status` need sudo — fold them into the next interactive/install session instead of burning a turn on workarounds.

## Audit BEFORE executing an infra plan

- Audit live disk/filesystem state before executing any deployment plan, even one agreed in a previous session: the plan's assumptions rot. Check `lsblk` + `/proc/mdstat` before touching storage. In practice: the plan assumed creating a storage pool from blank disks, but the disks were already a mdadm RAID1 mounted at `/srv/nas`.
- An existing-but-empty RAID is NOT silently disposable: surface the mismatch (keep mdadm/ext4 vs wipe for something else) to the user as an explicit decision with a recommendation — don't pick a side in the middle of a run.
- If the user overturns a plan decision WHILE a revision subagent is running, queue the reversal via delegation steer immediately — the agent folds it into the same revision instead of producing a stale plan you must re-edit.

## AIO needs a DOMAIN, not an IP (verified upstream, Oct 2026)

- Nextcloud AIO upstream refuses IP-only operation ("No and it will not be added") — the installer stalls at the domain-entry screen. Only the AIO setup panel `:8080` works by IP (self-signed cert; open it by IP deliberately, never by domain due to HSTS). So: install everything domain-free, stall only at the domain screen.
- `nas.tailaf23ba.ts.net` (Tailscale internal domain) is invisible from the internet; MagicDNS + HTTPS certificates give it a free auto-renewing LE cert. MagicDNS+HTTPS by the tailnet owner is the single external blocker.
- Tailnet-side setup is DONE and verified: MagicDNS resolves `nas.tailaf23ba.ts.net` → 100.69.213.39, `tag:nas` is applied to the node, device sharing to employees works (free tier is enough). Verify the tag from the NAS itself: `ssh nas 'tailscale status --json'` → `Self.Tags`. Still to do by the owner before employee rollout: enable HTTPS Certificates and the ACL `autogroup:shared -> tag:nas:443`.
- Tailnet IPs are unroutable through a local HTTP proxy: probe 100.x addresses with `curl --noproxy '*'` or `nc -z -G 3` — a proxied curl hangs/000s and looks like a closed port when the service is actually up. The macOS app-bundle CLI `/Applications/Tailscale.app/Contents/MacOS/Tailscale status` works even when the PATH `tailscale` binary is missing.

## Sudo staging pattern

- Sudo work goes as one script scp'd to the NAS home (`nas:~/nas-stage1.sh`), run by the USER via `ssh -t nas 'sudo bash ~/nas-stage1.sh'` — agent prepares and verifies (`bash -n`), user types the password once, agent never sees it. Do not offer/accept the sudo password in chat even when the user offers; NOPASSWD sudoers is available but user wisely declined for now.
- Stage 1 content = apt upgrade + ufw/smartmontools/unattended-upgrades + SMART long test + data dirs + Docker from the official repo. If a kernel upgrade lands, reboot only AFTER the SMART long test finishes (it runs hours in the background); check later with `smartctl -l selftest`.
- Script pitfall: `LOG=~/...` inside a script run via `sudo bash` expands to `/root/`, not the user's home — read logs from `/root/nas-stage1.log` (or hardcode an absolute path). Leftover `apt list --upgradable` entries phased out for GNOME packages arrive on their own — not an error.
- Stage 2 content = UFW + smartd schedule + mdadm health cron + `usermod -aG docker kbbs` + AIO mastercontainer run. Concrete UFW policy that survived review: default deny incoming; `ufw limit in on tailscale0 to any port 22`; `allow in on tailscale0 to any port 443`; LAN break-glass SSH from RFC1918 ranges (UFW is interface-aware — scope rules to `tailscale0`, a plain `allow 22` would expose SSH to the office LAN).
- After `usermod -aG docker kbbs`, a plain `ssh nas 'docker ps'` can still fail with "permission denied ... docker.sock" — a reused/multiplexed SSH session keeps the pre-usermod group set. Verify with `sudo docker` or a fresh connection before blaming the script.
- AIO mastercontainer flags (domain-free phase): `--publish 100.69.213.39:8080:8080` (bind to the Tailscale IP, never 0.0.0.0), `--env NEXTCLOUD_DATADIR=/srv/nas/nextcloud-data`, `--env APACHE_PORT=11000` + `APACHE_IP_BINDING=127.0.0.1` (tailscale serve path later), `--env SKIP_DOMAIN_VALIDATION=true`, volumes `nextcloud_aio_mastercontainer:/mnt/docker-aio-config` + docker.sock read-only, `--restart always`. The passphrase does NOT reliably appear in `docker logs` after first startup — read `/root/aio-passphrase.txt` via interactive `ssh -t nas 'sudo cat ...'` (plain `ssh nas 'sudo -n cat'` fails: no cached credential over a non-tty session), or have the user read it in the setup panel and save it into `~/aio/passphrase.txt` (chmod 600). Verify such user-saved secrets only by metadata (`wc -c`, `ls -l`) — never cat them into chat; a placeholder like «ВСТАВЬ ...» is ~20 bytes, so size alone can't tell real from stub, ask the user to eyeball it.

## tailscale serve (final HTTPS layer, verified working)

- With APACHE bound to `127.0.0.1:11000`, the public-in-tailnet entry is `sudo tailscale serve --bg http://127.0.0.1:11000` on the NAS — needs `ssh -t` (`sudo -n` fails: no cached credential in a non-tty session).
- First run prints "Serve is not enabled on your tailnet" plus a per-node enable link (`https://login.tailscale.com/f/serve?node=...`). The tailnet owner must open that link in a browser (it authorizes Serve+HTTPS for that node); no ACL text needed. Re-running the serve command after the owner clicks through prints `Available within your tailnet: https://nas...` — done.
- Verify from the admin's Mac: `curl --noproxy '*' https://nas.tailaf23ba.ts.net/status.php` (must return JSON with `installed:true`) and `openssl s_client ... | openssl x509 -noout -issuer -dates` (issuer must be Let's Encrypt, ~90-day auto-renewing — not the self-signed panel cert). `/` 302s to `/login` — that is success, no need to chase redirects.
- Do NOT also expose :8080 by domain — the AIO panel stays IP+self-signed-only (HSTS trap); serve covers only the app.

## Deployment project

- Plan and docs live in `/Users/dlgrv/work/infra/nas/`: `README.md` = verified host facts, `docs/` = admin-onboarding, employee-guide, runbook, tailscale-acl example. The phased plan (host prep → disks → Docker → AIO → UFW → ACL → policies → backups → monitoring → docs → go-live) is in `docs/superpowers/plans/`.
- Progress: stages 1–2 done; AIO wizard passed — domain `nas.tailaf23ba.ts.net` accepted (SKIP_DOMAIN_VALIDATION), Hub 26 Summer. Nextcloud 35.0.2 answers `status.php` with `installed:true`; `https://nas.tailaf23ba.ts.net` live with a valid LE cert via tailscale serve. Owner-side tailnet tasks DONE (MagicDNS, tag:nas, sharing, Serve). Extra containers stripped (EuroOffice/Talk/Whiteboard/Imaginary removed; ClamAV kept). Users `ldolgirev` + `asarkisyan` created and added to the `admin` group; personal-folders policies applied (public links off, resharing off, quotas); first file upload verified landing on md127 in real time (RAID1 writes both disks in one write — no 'later sync').
- Remaining rollout: borg backups via the AIO panel (backup dir `/srv/nas/backups`, save the borg encryption key OUTSIDE the panel), offsite copy target, SMART long-test results check, and the owner-side ACL fix (see security audit) — without it every device in BOTH tailnets (owner's allow-all) reaches NAS ports 22/443/8080.
- The service is branded **PrimeCloud** in all user-facing docs (it is Nextcloud underneath) — the brand name comes from the company's PrimePilot brandbook (`брендбук_финал.html` in ~/Downloads; Future Dusk palette: accent `#5B4BC4`, lilac `#9A8CE6`, tints `#F2F1F5`/`#DAD8E2`, dark `#322E54`, grey-violet `#6B6786`).
- Deliverable PDFs CURRENT (`docs/pdf/sotrudnik-dostup.pdf` + `docs/pdf/admin-nastroyka.pdf`), styled with the light Future Dusk accent design via the `pdf-cyrillic` skill (Verdana from /System/Library/Fonts/Supplemental/). Employee guide: real URL, node-sharing flow, color screenshot of the live UI placed after the login steps with a caption; the credentials key/value table is narrow (explicit mm colWidths, hAlign LEFT). Regenerate rather than patching the PDFs; verify text extraction (pypdf probes) before delivering. Old nas-access-management/nas-admin-onboarding drafts deleted.

## Post-deploy security audit (verified procedure)

- Layered probe order: (1) `ssh nas 'ss -tlnp'` — every listening socket must bind ONLY to the Tailscale IP (443/8080) or 127.0.0.1 (11000, CUPS, resolved); anything on 0.0.0.0 besides sshd/tailscale UDP is a finding. (2) From the admin Mac, `nc -z -G 3 $PUBLIC_IP <port>` across 22/80/443/8080/8443/11000 — behind CGNAT all must fail. (3) `openssl s_client -connect host:443 -servername host` — Verify return code must be 0 (ok). (4) ACL effect: probe ALL ports from a THIRD tailnet node (e.g. hermes-vm via `timeout 3 bash -c 'echo >/dev/tcp/100.69.213.39/<port>'`) — the Mac always has full access, so only a non-admin node proves the ACL actually filters.
- PITFALL — the intended `autogroup:shared -> tag:nas:443` ACL restricts only the SHARED side; devices under the admin's OWN account still reach every port on the NAS (22, 443, 8080) while the owner's default allow-all stands. Don't read full access from the admin Mac as 'ACL not applied' — test from a neutral node and check the admin console ACL text before flagging.
- Open finding to close before employee rollout: the AIO panel `:8080` (passphrase-gated but admin-grade) is reachable from the whole tailnet — after the ACL is fixed, deny 8080 on UFW except the admin's own nodes.
- PITFALL — the AIO wizard's office/optional selections did NOT stick: despite choosing 'none', EuroOffice, Talk, Whiteboard and Imaginary started (Talk shows `unhealthy` in a tailnet-only setup — it wants public 3478/udp; cosmetic, not an outage). After the wizard, re-check the config summary BEFORE 'Download and start containers'; fix unwanted extras later via panel: Stop containers → unselect → Save changes → Start (optional containers are only changeable while stopped).
- Remaining rollout: borg backups, first employee user + isolation test, SMART long-test results check.
- Deliverable PDFs live in `docs/pdf/` and follow a two-audience pattern: one plain-language document for management (no commands, tables of who-does-what, focus on privacy/quota/revocation) and one admin instruction (concrete steps, verification checklist, troubleshooting table).
- Before executing the plan: delegate a technical review to a subagent. Give it (a) plan + docs paths, (b) VERIFIED host facts only, (c) a concrete checklist (AIO compose vs upstream repo, UFW rules vs SSH lockout on tailscale0, current Tailscale ACL/grants format, RAM headroom). Steer the reviewer mid-run with fresh audit findings — the review must see the machine's real state, not the plan's assumptions.
- Secrets (Nextcloud admin password, AIO borg key, auth keys) go to a password manager only — never into the repo, docs carry placeholders.
