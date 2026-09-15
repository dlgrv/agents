# Postgres HA Options

## Streaming replication + manual promote
**Best for:** Non-critical DBs, single-admin teams

- **Setup:**
  - Primary: A (Postgres primary)
  - Standby: B (Postgres standby, streaming replication from A)
  - LB: healthcheck → A; if A dead → redirect to B (read-only)
  - Manual promote: playbook with fencing (poweroff/iptables) + promote B

- **RPO/RTO:** Up to 1 day (nightly dump) / 2–5 min (promote time)
- **Pros:** Simple, no extra services, easy to understand
- **Cons:** Split-brain risk, manual intervention, no auto-failover
- **Test:** Quarterly promote演习 with full clone verification

## Patroni + etcd
**Best for:** Critical DBs, automated recovery

- **Setup:**
  - Patroni agents on both nodes (E/F for PrimePilot)
  - etcd cluster: 3 nodes (E, F + third; B acceptable, office NAS forbidden)
  - HAProxy on LB routing to Patroni primary (REST API 8008)
  - Watchdog (softdog) required on both nodes

- **RPO/RTO:** 5–15 min (WAL) / 10–30 sec (failover)
- **Pros:** Auto-failover, no split-brain, built-in fencing
- **Cons:** etcd quorum dependency, tuning complexity, third node required
- **Quorum loss:** Primary demotes automatically (acceptable trade-off)

## etcd placement rules
- **Never on office NAS** — unstable network → false elections, demotes
- **Prefer B (Selectel)** if available — separate DC from E/F, stable
- **Third node options:**
  - Independent VPS (1 vCPU/2GB) — ideal, no DC dependency
  - Existing server (B) — acceptable, but DC failure affects both
  - Never colocate with primary/standby pair

## Fencing requirements
- **Before manual promote:** poweroff old primary or iptables DROP port 5432
- **Verify unavailability** before promote (ping, port check, pg_isready)
- **Patroni does this automatically** via watchdog and DCS consensus

## Monitoring
- Replication lag (seconds/bytes) → alert if > 60 sec or slot full
- etcd cluster health → alert if quorum lost
- Patronictl cluster status → check leader/health
- Heartbeat every 5–10 min (not hourly) for quick failure detection