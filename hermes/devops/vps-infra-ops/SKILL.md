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

## Planning workflow for infra tasks
1. **Inventory first** — references/infra-inventory.md; verify live state via
   user-pasted SSH output (audit mode: we never SSH ourselves).
2. **Options + recommendation BEFORE the final plan** (user's standing
   preference). Collect decisions with clarify; don't finalize on guesses.
3. Write plan to `.hermes/plans/` (see `plan` skill); open an
   «Этап 0 — решения» block marking each decision **✔ решено / ⏳ открыт**.
4. Infra plan structure: ASCII topology → decisions → DNS/domains →
   staged rollout (Этап 1..N; old servers stay up until new ones verified) →
   cost table ₽/мес → honest risks (what still fails + compensation).
5. Every migration keeps a rollback path: old server alive until new one is
   proven; final dumps → S3 → сверка before decommission.

## Pitfalls
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
