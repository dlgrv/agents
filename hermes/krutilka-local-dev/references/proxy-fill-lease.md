# Proxy pool / fill / lease — seams and invariants

Five proven timing-seam bugs (all found by adversarial tests, all fixed) plus the invariants that keep them closed. The seam CLASS: components sync through Redis at fill cadence (fill_interval seconds) while the bid hot path runs per-attempt — unit tests mock the neighbour and never see the window; any change here needs a REAL `_fill_one_pool` cycle → immediate `acquire` integration test.

## Invariants (break any of these and the old bug returns)

1. **Lease map is a fast path, not the source of truth.** `profile_lease_keys` is written only by the fill process; the bid worker builds its own registry WITHOUT it. Live-lease protection must therefore be self-sufficient in the acquiring process: on the discard path, re-check the lease at its source (one HGETALL, liveness by value `expires_at`, never by key TTL alone — a hash with expired values but no TTL looks live). Zero new Redis calls on the healthy pick path — the extra check lives ONLY on the rare discard branch.
2. **A full pool must never die before the next fill is allowed.** Entry age (`ENTRY_MAX_AGE_SECONDS`, 240) vs fill_interval (200): a stationary full pool's entries age out ~40s after a skip-fill, leaving a deterministic ~160s empty window (masked on lease-enabled pools by lease protection; visible on lease-less pools). Fill writes `entries_fresh_until = now + fill_interval` to meta when `to_probe == 0`; acquire lets confirmed-fresh entries serve until the next fill.
3. **drop_stale must re-check liveness at delete time** — the `protected_ips` snapshot was taken before the drop window; at 1000 rps a lease can appear between snapshot and delete. Pipeline-recheck each candidate before removing.
4. **The free-set mirrors the pool**, never add-only: `_forget_free_ip` (SREM) on every discard/drop path, or dead IPs stay "free" and the Lua walk mints profiles for nonexistent IPs (quota waste, manifest pollution).
5. **Meta-key TTL ≥ interval, not = ttl_seconds**: `max(ttl_seconds, fill_interval + 60)`, written AFTER `refresh_ttl` (which would shrink it back). Otherwise with ttl < interval `last_filled_at` evaporates mid-interval and the skip-gate dies → probes on every 10s timer tick. No config validation exists for ttl < interval — check before assuming it's safe.
6. **Normalize encodings before comparing a pool entry against config.** The probe/maxmind path writes `geo.country` as ISO alpha-3, campaign config carries alpha-2 — a raw `==` marks EVERY entry «changed» on every fill tick, mass `drop_ip` wipes the free-set, and at load rate the result is a `profile_preferred_unavailable` storm (each lookup for a wiped IP fails closed per attempt). Any cross-source comparison (country codes, units, id types) goes through the shared normalizer (`app.services.proxy.geo.iso3166`) first.
7. **Lease has a quota budget, not just a correctness contract.** Capacity = pool_count × profiles_per_ip × shows_per_profile_hour must exceed the campaign's ACQUIRE rate (attempts, not wins — quota is consumed on acquire) with ≥1.3× headroom, because the effective pool shrinks as per-IP hourly quotas saturate. Compute it before enabling lease on any campaign; the main 60k/min campaign was ~9× short (enable there only after raising the budget — larger pool or ppi). Sizing example: a 50 rps campaign over a ~2000-entry pool needed ppi=10 × hour=12 (120/IP/h → ~66 rps budget); the originally suggested ppi=2 × hour=6 gave ~6.7 rps — a guaranteed quota storm.

## Quota ramp and post-enable verification

- **A clean first 10 minutes proves nothing.** Per-IP hourly quotas fill over the first hour; saturated IPs SREM out of the free-set (`profile_pool:<pool>:free` shrinks) and refusals ramp gradually — a tight budget degrades as a slow ramp, not an instant storm. Watch 30+ min.
- **Health probes**: `redis-cli scard profile_pool:<pool>:free` (stable, not draining toward 0), lease-key count (`redis-cli --scan --pattern 'profile_pool:*' | wc -l`), `journalctl -u lowbid_bid_worker --since '-5 min' | grep -c profile_preferred_unavailable` (bounded window), and `bid_stats` grouped by (status, error_type) for the campaign over the last 5 min.
- **Lease keys carry 7–14-day TTLs** — their mere existence is NOT proof of a live lease; check free-set movement or fresh fill activity instead.

## Storm triage (one error class hitting many attempts at once)

- **A storm that survives a code revert is config/state-driven** — check campaign settings in the DB (a SQL-flipped flag) and Redis free-set/pool state before re-deploying more code. Kill the trigger at the data layer, verify the per-minute error rate hits 0, only then diagnose code.
- **Measure the storm RATE, not the count**: probe with a bounded recent window (last 2–3 min of journal) each time — a cumulative grep count keeps growing during diagnosis and reads as «still storming» when the storm has already stopped.
- **Onset lags the trigger by up to a pool turnover/warmup (several fill ticks)** — build the timeline (flag flip, deploys, first storm line) before attributing cause; a revert that «didn't help» may predate the storm entirely.

## Test environment

- Standalone Redis for worktree/isolated runs: `redis-server --port 6380 --daemonize yes`, then `REDIS_PORT=6380 REDIS_DB=15 pytest tests -q`; kill it when done. Compose-stack runs use the repo convention (live lowbid_redis db15).
- `tests/fake_redis.py` is a hand-rolled double — extend it (sets/srem/pipeline ops) BEFORE writing gate/TTL tests; `fakeredis` is not in deps.
- The seam tests live in `backend/tests/test_timing_seam_bughunt.py` (BUG-1..BUG-5 + refutations) — keep green.
