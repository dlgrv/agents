---
name: async-python-hot-path
description: Patterns for optimizing high-throughput async Python services — systematic bottleneck analysis, prefetch buffers, backpressure, lazy init, and serialization tricks.
---

# Async Python Hot-Path Optimization

Optimize high-throughput async Python services (~500+ req/sec). Focus on reducing event-loop overhead, I/O round-trips, and per-request allocations while keeping architecture clean.

## When to Use

- High-throughput async service (300+ req/sec) hitting a throughput wall
- Need to identify CPU vs I/O vs event-loop bottlenecks
- Optimizing Redis/HTTP call frequency on the hot path
- Performance/efficiency audit of an existing service (max req/sec per resource) — read the hot path end-to-end before proposing changes
- Reducing per-request object allocations

## 1. Systematic Bottleneck Analysis

Before optimizing, measure where time goes. Three dimensions:

| Dimension | Symptom | Tool |
|-----------|---------|------|
| CPU-bound | High CPU%, low I/O wait | `time.perf_counter()` micro-benchmark |
| I/O-bound | Tasks waiting on `await` | Connection pool stats, Redis MONITOR |
| Event-loop | Throughput drops sharply above N rps | Coroutine count, task creation rate |

**Rule:** benchmark the hot function in isolation (10K iterations). If it's < 5% CPU, it's not the bottleneck — look at I/O or event loop instead.

```python
import time
N = 10_000
t0 = time.perf_counter()
for i in range(N):
    result = hot_function(...)
elapsed = time.perf_counter() - t0
cpu_budget_pct = (elapsed / N * target_rps) / 10_000 * 100
print(f"{elapsed/N*1e6:.1f} µs/call, {cpu_budget_pct:.1f}% CPU at {target_rps} rps")
```

### Audit sequence (efficiency audit of an existing service)

1. Map the hot path by reading the full chain end-to-end (scheduler → request builder → HTTP executor → dependency services → buffers → persistence) before touching anything.
2. Micro-benchmark per-attempt CPU on the project venv (10–20K iterations per op). Calibration anchors (M-series, py3.13): orjson.dumps ~0.4µs, uuid4 ~2µs, gzip level-9 ~8µs, full oRTB request build ~20µs → ~35K req/s/core. When the CPU budget is this small, CPU is not the bottleneck — rank findings by I/O and concurrency instead.
3. Compute the concurrency ceiling: `ceiling_rps = max_concurrency / (mean_primary_RTT + P(secondary) × mean_secondary_RTT)` and compare against the target rps. ×28 headroom means fine; ×1.6 means one slow episode stalls the scheduler.
4. Check deployment topology before ranking round-trip optimizations: N sequential Redis/DB round-trips per request cost ~0.2% of a 300ms attempt when co-located (127.0.0.1), ~10%+ when remote. Read the deployed .env/systemd unit, not repo defaults.
5. Rank external dependencies by recorded stats (response_ms medians, error rates) before blaming code — e.g. residential-proxy RTT usually dominates everything.

## 2. Prefetch Buffer (Redis / remote calls)

**Problem:** calling Redis/remote service on every request (500 rps → 500 calls/sec).
**Solution:** fetch the entire dataset into local memory, serve from there, refill only on drain.

```python
class PrefetchBuffer:
    """Fetch all items from remote in one call, serve locally with swap-remove."""
    def __init__(self, redis, key):
        self._redis = redis
        self._key = key
        self._buffer: list[Item] = []
        self._lock = asyncio.Lock()

    async def pick(self) -> Item | None:
        if not self._buffer:
            await self._refill()
        if not self._buffer:
            return None
        # swap-remove: O(1) random removal
        idx = random.randint(0, len(self._buffer) - 1)
        self._buffer[idx], self._buffer[-1] = self._buffer[-1], self._buffer[idx]
        return self._buffer.pop()

    async def _refill(self):
        async with self._lock:
            if self._buffer:
                return  # double-checked: another task already refilled
            rows = await self._redis.hgetall(self._key)  # or HRANDFIELD -N
            self._buffer = [Item.from_row(r) for r in rows]
            random.shuffle(self._buffer)
```

**Key design decisions:**
- Fetch ALL, not partial batches. Simpler, fewer params, maximum diversity.
- Swap-remove gives O(1) random pick — same entropy as per-request remote call.
- Double-checked locking: only one concurrent refill, no wasted calls.
- Negative count in Redis HRANDFIELD (`-10000`) returns unique fields only.

## 3. Backpressure via Semaphore

**Problem:** `asyncio.Semaphore(attempts_per_min)` at 30K creates 30K waiting coroutines → memory bloat.
**Solution:** cap at physical limit (connector capacity × 1.5).

```python
# The real limit is the TCP connector, not the desired rate.
_MAX_CONCURRENT = 1200  # TCPConnector(limit=800) × 1.5 headroom
semaphore = asyncio.Semaphore(min(attempts_per_min, _MAX_CONCURRENT))
```

This provides true backpressure: when the network/endpoint slows down, the scheduler stops spawning new tasks instead of accumulating them.

**Slot occupancy = every await inside the slot.** A follow-up call awaited inline after the primary I/O (e.g. win-notice after a bid) extends slot hold time by its RTT × its probability. Detach it as its own task (its error handling must not need the slot) or include it in the ceiling formula — never ignore it.

Detached tasks need supervision: register each in the owner's task set (`active_tasks.add(task)` + discard + exception-logging done-callback) and cancel the set in the same `finally` that cancels the main loop — bare `create_task` leaks tasks on shutdown and swallows exceptions. Detaching also changes failure semantics: the follow-up's error no longer degrades the attempt's recorded outcome (a failed win-notice leaves the bid a WIN); make that explicit in docstrings/logs so nobody "restores" the inline degradation.

## 4. Timeout at the Boundary

**Problem:** `asyncio.wait_for()` wrapped around business logic creates timers per request and mixes concerns.
**Solution:** timeouts belong at the I/O client, not the orchestrator.

```python
# HTTP: aiohttp.ClientTimeout(total=..., connect=..., sock_read=...)
# Redis: socket_connect_timeout on the connection pool
# Business logic (CPU): no timeout needed — it can't hang
```

Remove `asyncio.wait_for` wrappers from task launchers. If worried about hangs, add `total` timeout to the HTTP client instead.

## 5. Thin Wrapper for Serialization

**Problem:** mixing `json.dumps` and `orjson.loads` — two JSON engines without reason.
**Solution:** single module as the project's JSON entry point.

```python
# app/utils/jsonlib.py
import orjson

def dumps(obj) -> bytes:
    return orjson.dumps(obj)

def loads(data: str | bytes) -> dict:
    return orjson.loads(data)
```

Benefits: one-line switch to `msgspec` later, consistent behavior, no import confusion.

## 6. Lazy Init (avoid allocations on cold path)

**Problem:** `__post_init__` always creates expensive objects (e.g. `random.Random()`).
**Solution:** lazy property + factory method for the hot path.

```python
@dataclass(slots=True)
class Context:
    seed: int | None = None
    _rng: Random | None = field(init=False, repr=False, default=None)

    @classmethod
    def for_attempt(cls, **kwargs) -> "Context":
        return cls(**kwargs)  # no RNG creation

    @property
    def rng(self) -> Random:
        if self._rng is None:
            self._rng = Random(self.seed)
        return self._rng
```

## Patterns Summary

| Pattern | Use when | Antipattern |
|---------|----------|-------------|
| Prefetch Buffer | Remote calls on hot path | Partial batches with watermark params |
| Backpressure Semaphore | Concurrency >> actual capacity | Semaphore = desired rate |
| Timeout at Boundary | Orchestrator wraps I/O | `wait_for` around business logic |
| Thin Wrapper | Multiple libs for same format | Direct lib usage scattered across files |
| Lazy Init | Expensive objects often unused | `__post_init__` side-effects |
| Swap-Remove | Random pick from buffer | `random.choice()` without removal |
| Double-Checked Lock | Concurrent refill safety | Lock without pre-check |

## Pitfalls

1. **Premature batching.** Don't add batch_size/watermark params unless measured and needed. "Fetch all" is simpler and often faster.
2. **Over-parameterization.** Every configurable knob is a future bug. Default to zero-config.
3. **Measuring wrong thing.** Always benchmark the hot function in isolation before optimizing it. Macro rendering at 26µs/call is NOT a bottleneck at 500 rps (1.3% CPU).
4. **Removing safety nets blindly.** If removing `wait_for`, ensure each I/O client has its own timeout configured.
5. **Post-await failure overwrite.** After awaiting I/O, a failure may already be recorded downstream (buffer flushers flush concurrently). Clear or flag the attempt state dirty before the success path assigns a final status — don't rely on call order within one coroutine.
6. **Long-lived jobs vs worker slots.** A worker whose jobs never exit (scheduler loops) silently caps at `max_jobs` — extra jobs are never picked up and no error is raised. Set `max_jobs` above the count of long-lived jobs, or run them outside the job system.
7. **gzip.compress defaults to level 9.** Pass `level=6` on per-request paths — level 9 triples CPU for a size delta that RTT doesn't notice.
8. **Trusting hand-rolled fakes for client response shapes.** A fake/mock written against imagination validates only itself, not the client. Before code depends on a mocked response shape (e.g. `HRANDFIELD key 1 WITHVALUES` → `[field, value]`, empty hash → `[]`), probe the real client once in a throwaway `docker run redis:7-alpine` and match the fake to what it actually returns — a MagicMock-based test passes while production raises.
