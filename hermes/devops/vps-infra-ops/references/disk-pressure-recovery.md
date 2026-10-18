# Disk-pressure recovery on a VPS with Postgres (validated recipe)

Symptoms of a full disk on a DB host: Postgres dies on WAL write (systemd
unit shows failed), app services/ workers crash-loop, monitoring alarm fires
while memory looks fine. Work top-down; never delete blind.

## 1. Triage the writers
`df -h` → `du -x -d1 / | sort -h` → descend level by level into the biggest
dir. Typical offenders: docker build cache + dangling images, rotated logs,
journald, app log dirs, one bloat table in Postgres.

## 2. Fast safe reclaims (before any DB surgery)
- Docker: `docker image prune -af` + builder cache prune (deployer/docker-
  group user needs no sudo). Do NOT `--volumes` blindly.
- Logs: delete rotated (`*.gz`, `*.1`); truncate active files with `: > file`
  only while the writing service is stopped (truncating a live writer is safe
  with `truncate -s 0` for most appenders, but stopping first is always safe).
- journald: `journalctl --vacuum-size=500M`.

## 3. Postgres bloat diagnosis
Compare `pg_relation_size(t)` (heap) vs `pg_total_relation_size(t)` (total):
a small heap under a huge total = TOAST bloat (large jsonb/text columns) or
swarms of dead tuples — indexes stay small either way. Check row counts per
day (`SELECT date_trunc('day', ts), count(*) … GROUP BY 1`) to size a
retention window. Check outbound FKs (`pg_constraint`) — nobody may reference
the table before the rebuild.

## 4. Swap-rebuild (stop writers/API first = safe window)
```sql
CREATE TABLE t_new (LIKE t INCLUDING ALL);
INSERT INTO t_new SELECT * FROM t WHERE ts > now() - interval 'N days';
ALTER TABLE t_new ALTER COLUMN id DROP DEFAULT;   -- default pins old sequence
DROP TABLE t;
ALTER TABLE t_new RENAME TO t;
CREATE SEQUENCE ... ; SELECT setval(seq, max(id)) ; ALTER COLUMN id SET DEFAULT;
ALTER TABLE t_new ADD PRIMARY KEY / CREATE INDEX ...;  -- AFTER copy: 2–3× faster
GRANT ... ;  -- re-grant: recreated by superuser → app rights are GONE
```
Pitfalls:
- **Free-space ≥ 2× the copy size.** One big `INSERT … SELECT` roughly doubles
  its footprint via WAL; a failed INSERT rolls back but leaves dead pages —
  `TRUNCATE` the half-filled new table to reclaim before retrying with a
  smaller window.
- Start with the SMALLEST acceptable window and grow only if space allows;
  a second rollback costs another cycle.
- The new table's DEFAULT referencing the old sequence blocks `DROP TABLE old`
  — `DROP DEFAULT` first, rebuild the sequence after rename (`setval` to max(id)).
- Recreated-by-superuser tables lose app GRANTs: workers then silently fail
  INSERTs while everything "looks up". Watch worker logs for permission
  errors after restart and verify actual row growth, not just service status.

## 5. Close the loop
Restart services, verify live flow (row growth / app metrics), then install
retention: nightly cron `DELETE WHERE ts < now() - interval 'N days'` plus
periodic `VACUUM (ANALYZE)` — without retention the bloat returns on the same
timescale it took to accumulate.
