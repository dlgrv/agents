---
name: vps-infra-ops
description: "Use before VPS work: migrations, failover, DNS, backups."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [devops, vps, failover, dns, backups, selectel, wireguard]
    related_skills: [plan, gitflic-selfhosted-ops]
---

# VPS Infrastructure Ops (user's estate)

Class skill for planning, migrating, and operating the user's self-hosted
servers (primebpm/primegit/gitflic/PrimePilot). READ
`references/infra-inventory.md` FIRST — it holds the full estate (all
IPs/services/repos), the target architecture, the decision log, and open
questions. Never ask the user to re-state any of it.

## Hard user decisions — do NOT re-litigate
- **Cloudflare is NOT used** (user rejected it). DNS = **Яндекс DNS**
  (user's existing provider); TTL → 60 за сутки до переезда.
- **ONE Selectel account.** Product isolation is technical (firewall rules,
  not separate accounts).
- **S3 removed entirely** (decision 2026-09-02): backups = mutual dumps on
  the paired server (web ↔ gitflic cross-dump), retention/prune по cron.
  GitLab RPO 1ч / RTO 30мин accepted. **GitLab Geo is Premium — never propose it.**
- Admin panels (admin.primepilot.tech) — **WireGuard only**, never public.
- **PrimePilot is isolated from all other products:** zero permitted connections
  between PP nodes and the main group (verify `nc -zv` both ways), own S3 key
  restricted to its bucket only, separate WireGuard addressing.

## Sizing philosophy (user-checked — do NOT pad)
- Light-load services («для галочки» — docs, rare CI) get **NO RAM headroom**:
  size to the real component table + swap, never «+ запас на вырост».
  User pushes back on padding every time.
- GitFlic (2 instances + 1 shared runner, всё в docker) = 4 vCPU / 8GB /
  80GB: JVM heap cap 1–1.5G/instance, runner CONCURRENCY=1, swap 4G как
  страховка. Revisit only if CI becomes regular/heavy.
- Disk: сетевой HDD (Selectel, 8.17₽/ГБ) fine for light load; NVMe only
  where a DB writes actively (GitLab, Postgres под нагрузкой) — там не
  экономим.
- Runner: user prefers ONE shared runner for both GitFlic instances, not
  per-instance.

## Geographic distribution (user-checked — design gate)
- **Не концентрировать большинство VM в одном городе**, even when the
  provider menu pulls that way: user rejects any layout where one city holds
  the majority of VMs. Standby/copies (GitLab-standby, DB-replica) разносить
  в другие города/провайдеров даже у того же хостера — это дёшево и снимает
  возражение.
- Before defaulting everything to one location, show the full DC map of RU
  regions (см. references/infra-inventory.md → ACTIVE PLAN: Selectel ru-8
  NSK — единственное крупное облако на востоке; Adman NSK; EKACOD Екб — свои
  2× Tier III; RUVDS-гермозоны Казань IT Park / Екб / Самара / Владивосток;
  CloudX Казань/НН) и предложить раскладку по городам до финального плана.
- Технические ограничения держать в голове при раскладке: LB-пара
  (keepalived/VRRP) живёт только в одной L2-сети = один пул/город; etcd-судью
  можно накладывать на существующую VM другого региона (standby-роль), чтобы
  не плодить договоры с мелкими хостерами.

## Planning workflow for infra tasks
1. **Inventory first** — references/infra-inventory.md; verify live state
   via user-pasted SSH output (audit mode: no direct SSH except the
   direct-access exceptions listed in the inventory).
2. **Options + recommendation BEFORE the final plan** (user's standing
   preference). Collect decisions with clarify; don't finalize on guesses.
3. Write plan to `.hermes/plans/` (see `plan` skill); open an
   «Этап 0 — решения» block marking each decision **✔ решено / ⏳ открыт**.
4. Infra plan structure: ASCII topology → decisions → DNS/domains →
   staged rollout (Этап 1..N; old servers stay up until new ones verified) →
   cost table ₽/мес → honest risks (what still fails + compensation).
5. Every migration keeps a rollback path: old server alive until new one is
   proven; final dumps → S3 → сверка before decommission.

## SSH access discipline (user directive — applies to EVERY server)
- **One failed SSH auth attempt = full stop.** Never retry with a second key, password, or user — sequential failures trip fail2ban and ban the user's IP, locking THEM out of their own server. Diagnose why the first attempt failed (wrong key path? wrong user?) before any second attempt, or hand back to the user.
- Use only the key the user named for that server (e.g. a per-server `~/.ssh/<name>_id` key); `BatchMode=yes` so a missing key errors instead of hanging on a password prompt.
- **Non-default key name = ssh never offers it on its own.** After `ssh-copy-id -i ~/.ssh/<custom>_key` succeeds, a plain `ssh user@host` still fails with `Permission denied (publickey)` — ssh only tries default-named keys. Immediately add a `Host <alias>` block to `~/.ssh/config` (HostName/User/IdentityFile) and verify with `ssh -o BatchMode=yes <alias> '<echo ok>'`; use the alias forever after. Never conclude "the key didn't install" from one failed plain `ssh` — the key may be installed fine and just never offered.
- sudo without exposing the password: read it from the user-designated secrets file into a protected env (never print/echo it), then run remote commands as `sudo -A` with an SSH_ASKPASS-style helper script that reads that env var. The password never enters chat, command lines, or terminal scrollback. If the user hasn't provided a secrets file — ask them to run the privileged steps, don't improvise.

## GitHub Actions deploy pattern (deployer user)
Established on the games/adtech server (krutilka, then copied for ssp) and reusable anywhere: dedicated `deployer` user (docker group, owns `/home/deployer/<project>`), a deploy-only SSH keypair named `<project>_github_actions` whose pubkey sits in deployer's `authorized_keys` with comment `github-actions@…`, manual `workflow_dispatch` CD job that SSHes in and runs compose build + up. Env-specific compose overrides MUST live in the repo — the CD job's checkout replaces the working tree and silently reverts any override file that existed only on the server. Same rule generalizes to every repo-owned file CD copies to the server (compose files, systemd units, cron files): a manual server-side edit of a repo-owned file survives only until the next deploy — fix in the repo, and pin the invariant with a CI lint gate (e.g. grep failing the build) where the failure class is known. The same mechanism bites services: gate host-port-conflicting services (Caddy/Traefik on 80/443 when host nginx owns the ports) behind an INACTIVE compose `profiles:` entry in the BASE file, never by deleting them from a server-side copy — the CD checkout restores the stock base file, the service comes back and fights for the port, and the rollout step dies on 'driver failed programming external connectivity'. When a CD run fails, read the run log (`gh run view <id> --log | grep -iE 'error|FATAL'`) — the failing compose step names the conflicting container. Two more invariants for privileged installs: (a) a repo-owned file copied by CD to a root-owned path needs its own per-file NOPASSWD sudoers entry — sudoers matches exact `cp <src> <dst>` command lines, so a new file without one fails the cp with 'a password is required'; (b) the remote script must propagate errors (`set -e`) — an ssh heredoc returns the LAST command's exit code, so an early failed sudo/silent skip reports a green run. Verify the installed file's CONTENT on disk, never the run conclusion. The end state of this pattern: every server config (cron.d, rsyslog, logrotate, docker daemon.json, nginx, sudoers) lives in the repo under `deploy/server/` with an idempotent installer and a scheduled drift-check that diffs normalized copies (normalize away secrets/tokens and comment lines) and pushes status to the monitoring system — the manual 'fix in the repo, not on the server' rule enforced by automatic detection. Secrets stay out of the repo: placeholder in the template, real value in a root-only env file the installer reads at install time. Idempotent installers never repair an existing BROKEN file ('skip if exists') — rm + reinstall to fix, and verify content (grep for the variables) after installing, never the installer's output.

## Pitfalls
- Disk 100% on a server with Postgres: follow the validated recovery recipe
  (writer triage → safe reclaims → TOAST-bloat diagnosis → swap-rebuild →
  retention cron) — `references/disk-pressure-recovery.md`.
- DNS failover is a **1–5 min window**, not instant (TTL 60 + healthcheck
  cadence). Seconds-level needs VRRP/IP Failover — paid, same-DC only.
- WAL-архив (WAL-G → S3) = point-in-time recovery; hourly dump = simpler,
  1h loss ceiling. Recommend WAL for money-adjacent DBs (PrimePilot),
  dumps for internal tools.
- RU hosting context: zones at RU registrar; Selectel gives free L3/L4 DDoS
  only, no L7 — compensate with nginx limit_req + fail2ban.
- Static files (downloads) → Object Storage + CDN survives any single server
  death, near-free.

## Postgres HA patterns
- **Streaming replication**: B-standby, promote by playbook — RTO ~2–5 min;
  simple, but risk split-brain if promote without fencing. Test quarterly.
- **Patroni + etcd**: auto-failover in 10–30 sec; requires 3-node etcd quorum
  (E, F + third node; B acceptable, office NAS forbidden). Quorum loss →
  demote primary; acceptable trade-off against split-brain. Use for
  critical DBs (PrimePilot).
- **Fencing mandatory before promote**: poweroff, iptables DROP, or reboot
  old primary. No fencing = risk data corruption; patroni watchdog handles
  this automatically.
- **RPO/RTO**: streaming replication + daily dump = RPO up to 1 day, RTO 2–5 min;
  WAL-archiving + pgBackRest = RPO 5–15 min, RTO 30–60 min. Document
  targets per service (GitLab: RPO 1h, PrimePilot: RPO 5–15 min).

## Draw.io schema best practices
- **Always show WireGuard mesh** as a logical subnet with internal addressing
  when any internal service (etcd, Patroni, replication) relies on it.
- **etcd quorum must be drawn as edges** between the 3 nodes — no isolated labels.
- **Patroni agents are separate from etcd nodes** (even if colocated): label as
  'Patroni (agent)' on DB nodes, 'etcd1/2/3' on etcd-only nodes.
- **Break monolithic blocks** (e.g. NAS → split into 'Monitoring' + 'Backup storage').
- **Draw failover arrows** from LB to primary, then to backup, with labels like
  'failover → B' or 'при отказе A' — do not leave arrow endpoints unlabeled.
- **Static sync (rsync) should be shown** if present (e.g. C→D for landing static).
- **DNS domains must be on the arrow** not floating text (e.g. 'crbsit.ru' on
  DNS→LB arrow, not standalone box).
- **Avoid crossing dashed lines** — route dump arrows to NAS without intersections.
- **Color standby servers with yellow/orange**, not red (red = error state).
- **Include a legend** listing all servers and their roles for clarity.
- **Label planned features** as 'plan' (e.g. rsync git-data A→B).
- **Publication copy = sanitized copy.** A schema that carries real IPs,
  names, handles, or model names must not leave the machine: strip them via
  regex sweep over `mxCell` values (IP pattern + known names/handles) and
  replace with generic labels — the technique lives in the
  `drawio-diagram-editing` skill ("Preparing a diagram for publication").
