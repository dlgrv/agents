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
- Prepared for the tailnet owner (message drafted, free tier is fine): enable MagicDNS + HTTPS Certificates in admin console; declare `tag:nas` (tagOwners: autogroup:admin) and ACL `autogroup:shared -> tag:nas:443`; employee access later via device Share — the ACL already limits shared users to :443 only.

## Sudo staging pattern

- Sudo work goes as one script scp'd to the NAS home (`nas:~/nas-stage1.sh`), run by the USER via `ssh -t nas 'sudo bash ~/nas-stage1.sh'` — agent prepares and verifies (`bash -n`), user types the password once, agent never sees it. Do not offer/accept the sudo password in chat even when the user offers; NOPASSWD sudoers is available but user wisely declined for now.
- Stage 1 content = apt upgrade + ufw/smartmontools/unattended-upgrades + SMART long test + data dirs + Docker from the official repo. If a kernel upgrade lands, reboot only AFTER the SMART long test finishes (it runs hours in the background); check later with `smartctl -l selftest`.

## Deployment project

- Plan and docs live in `/Users/dlgrv/work/infra/nas/`: `README.md` = verified host facts, `docs/` = admin-onboarding, employee-guide, runbook, tailscale-acl example. The phased plan (host prep → disks → Docker → AIO → UFW → ACL → policies → backups → monitoring → docs → go-live) is in `docs/superpowers/plans/`.
- Deliverable PDFs live in `docs/pdf/` and follow a two-audience pattern: one plain-language document for management (no commands, tables of who-does-what, focus on privacy/quota/revocation) and one admin instruction (concrete steps, verification checklist, troubleshooting table). Generate with the `pdf-cyrillic` skill; verify text extraction (pypdf probes) before delivering.
- Before executing the plan: delegate a technical review to a subagent. Give it (a) plan + docs paths, (b) VERIFIED host facts only, (c) a concrete checklist (AIO compose vs upstream repo, UFW rules vs SSH lockout on tailscale0, current Tailscale ACL/grants format, RAM headroom). Steer the reviewer mid-run with fresh audit findings — the review must see the machine's real state, not the plan's assumptions.
- Secrets (Nextcloud admin password, AIO borg key, auth keys) go to a password manager only — never into the repo, docs carry placeholders.
