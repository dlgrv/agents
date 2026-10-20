# Uptime Kuma — two-instance monitoring (validated procedure)

Layout: primary Kuma (docker, port 3001, WG-only via ufw) on the main server;
standby clone on the NAS (docker `--restart unless-stopped`, bound ONLY to
the WG IP and the Tailscale IP — never 0.0.0.0). Same users/passwords by
design: the standby's DB is a full clone of the primary's `kuma.db`.

## DB clone to a standby instance
1. On the primary: `docker cp $(docker ps -qf name=kuma):/app/data/kuma.db /tmp/k.db && chmod 644 /tmp/k.db` (needs root/docker — the agent's account usually is NOT in the docker group: stage via scp and hand one short root command block, as with any /tmp-staged file).
2. On the standby: `docker stop` → `docker cp /tmp/k.db <container>:/app/data/kuma.db` → `docker start`; verify healthy + HTTP (root path 302s to /login — that is success).
3. Verify by pulling the db back and querying: user count, active monitor count, and that heartbeats flow (`COUNT(DISTINCT monitor_id) FROM heartbeat WHERE time > datetime('now','-2 minutes')`).

## Cloned-instance monitors that can NEVER go green — pause, don't debug
- **push-type monitors** receive metrics only from agents configured to push to the PRIMARY's URL — they stay down on the clone forever.
- **monitors targeting 127.0.0.1** test the PRIMARY's local services; on the clone 127.0.0.1 is the clone itself.
- Fix: `UPDATE monitor SET active=0 WHERE type='push' OR hostname='127.0.0.1' OR url LIKE '%127.0.0.1%'` on the CLONE only. Reversible (active=1); never delete.

## No REST API — manage monitors via sqlite surgery
Kuma (v1 and v2) has no usable REST API for monitor CRUD. Procedure:
`docker cp` the db out → modify with python sqlite3 → `docker stop` → copy back → `docker start`. Never edit the db under a running container.
- **Insert a monitor by copying an existing row of the same type as a template** and overriding only name/url/active/created_date (and `id`→None for autoincrement). Many columns are NOT NULL with quirky defaults ('null' strings, empty strings) — building a row from all-None values trips IntegrityError. Set `accepted_statuscodes_json='["200-299"]'` for endpoints that redirect (Kuma's `/` 302s to /dashboard) and keep maxredirects default.
- Add one mutual monitor per pair for Kuma↔Kuma watching: each instance gets an http monitor of the OTHER's `http://<wg-ip>:3001/`.

## Version upgrade (validated 1.23 → 2.x)
- The 1.x→2.x DB migration is one-way — a downgrade cannot read the migrated db. Backup first: `docker cp ... kuma.db` off the box (scp to the admin Mac) before touching anything.
- Recreate, don't in-place-upgrade: `docker pull louislam/uptime-kuma:<ver>` → `docker stop && docker rm` → `docker run` with the SAME publish binds and `--restart unless-stopped` and the SAME named volume (the volume carries the db, so config survives). Read `docker logs` for migration lines, then verify via the db-pull queries above and `curl` the port.
- Expect version divergence between primary and standby after upgrading one — harmless (they watch each other over plain HTTP), but note it to the user.
