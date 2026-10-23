# Proxy pool / fill / lease — seams and invariants

Five proven timing-seam bugs (all found by adversarial tests, all fixed) plus the invariants that keep them closed. The seam CLASS: components sync through Redis at fill cadence (fill_interval seconds) while the bid hot path runs per-attempt — unit tests mock the neighbour and never see the window; any change here needs a REAL `_fill_one_pool` cycle → immediate `acquire` integration test.

## Invariants (break any of these and the old bug returns)

1. **Lease map is a fast path, not the source of truth.** `profile_lease_keys` is written only by the fill process; the bid worker builds its own registry WITHOUT it. Live-lease protection must therefore be self-sufficient in the acquiring process: on the discard path, re-check the lease at its source (one HGETALL, liveness by value `expires_at`, never by key TTL alone — a hash with expired values but no TTL looks live). Zero new Redis calls on the healthy pick path — the extra check lives ONLY on the rare discard branch.
2. **A full pool must never die before the next fill is allowed.** Entry age (`ENTRY_MAX_AGE_SECONDS`, 240) vs fill_interval (200): a stationary full pool's entries age out ~40s after a skip-fill, leaving a deterministic ~160s empty window (masked on lease-enabled pools by lease protection; visible on lease-less pools). Fill writes `entries_fresh_until = now + fill_interval` to meta when `to_probe == 0`; acquire lets confirmed-fresh entries serve until the next fill.
3. **drop_stale must re-check liveness at delete time** — the `protected_ips` snapshot was taken before the drop window; at 1000 rps a lease can appear between snapshot and delete. Pipeline-recheck each candidate before removing.
4. **The free-set mirrors the pool**, never add-only: `_forget_free_ip` (SREM) on every discard/drop path, or dead IPs stay "free" and the Lua walk mints profiles for nonexistent IPs (quota waste, manifest pollution).
5. **Meta-key TTL ≥ interval, not = ttl_seconds**: `max(ttl_seconds, fill_interval + 60)`, written AFTER `refresh_ttl` (which would shrink it back). Otherwise with ttl < interval `last_filled_at` evaporates mid-interval and the skip-gate dies → probes on every 10s timer tick. No config validation exists for ttl < interval — check before assuming it's safe.

## Test environment

- Standalone Redis for worktree/isolated runs: `redis-server --port 6380 --daemonize yes`, then `REDIS_PORT=6380 REDIS_DB=15 pytest tests -q`; kill it when done. Compose-stack runs use the repo convention (live lowbid_redis db15).
- `tests/fake_redis.py` is a hand-rolled double — extend it (sets/srem/pipeline ops) BEFORE writing gate/TTL tests; `fakeredis` is not in deps.
- The seam tests live in `backend/tests/test_timing_seam_bughunt.py` (BUG-1..BUG-5 + refutations) — keep green.
