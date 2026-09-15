# Async Python Performance Patterns

Concrete patterns extracted from optimizing a high-throughput bid worker
(30K+ async HTTP requests/min on 1 core).  Each pattern includes the problem,
the solution, and the code shape.

---

## 1. Backpressure via Bounded Semaphore

**Problem:** `asyncio.Semaphore(business_metric)` — e.g. `Semaphore(30000)` when
the real I/O limit is `TCPConnector(limit=800)`.  Under load the event loop
accumulates thousands of waiting coroutines (50-100 MB wasted memory, GC thrash).

**Solution:** Cap the semaphore at the physical I/O limit × 1.5:

```python
_MAX_CONCURRENT = 1_200  # connector limit (800) × 1.5 for rotation headroom
semaphore = asyncio.Semaphore(min(attempts_per_min, _MAX_CONCURRENT))
```

When the semaphore is exhausted, `await semaphore.acquire()` blocks the scheduler
itself — honest backpressure instead of unbounded task creation.

**Why it's clean:** separates business metric (`attempts_per_min` — "how fast we want
to go") from infrastructure limit (`_MAX_CONCURRENT` — "how fast we can go").  Each
layer owns its constraint.

---

## 2. Timeout at the I/O Boundary

**Problem:** `asyncio.wait_for(business_logic(), timeout=N)` wraps the entire
attempt — mixing I/O timeouts with business logic timeouts and creating N
timer objects per second.

**Solution:** Remove the outer `wait_for`.  Rely on I/O-level timeouts:

```python
# HTTP (already correct)
timeout = aiohttp.ClientTimeout(connect=2.0, sock_read=5.0, sock_connect=2.0)

# Redis — ensure socket_timeout is configured on the connection pool
# RedisSettings(..., socket_timeout=2.0)
```

Hot-path code becomes:
```python
async def _run_attempt(ctx):
    try:
        await run_bid_executor(ctx, campaign)   # no wait_for
    finally:
        semaphore.release()
```

**Why it's clean:** timeout responsibility lives with the I/O client that can
actually enforce it.  Business-layer code stays timeout-free.

---

## 3. Prefetch Buffer (Redis / DB round-trip reduction)

**Problem:** Calling `redis.hrandfield(key, 1)` on every request (500/sec).
Each call is a network round-trip + event-loop cycle on localhost.

**Solution:** Batch-prefetch into a local `deque` with double-checked locking:

```python
class ProxyPool:
    def __init__(self, redis, batch_size=100, low_watermark=20):
        self._redis = redis
        self._buffer = deque()
        self._lock = asyncio.Lock()

    async def pick(self):
        if len(self._buffer) <= self._low_watermark:
            await self._refill()
        return self._buffer.popleft() if self._buffer else None

    async def _refill(self):
        if not self._lock.locked() and len(self._buffer) > self._low_watermark:
            return
        async with self._lock:
            if len(self._buffer) > self._low_watermark:
                return
            rows = await self._redis.hrandfield(KEY, self._batch_size, withvalues=True)
            for ... in (rows or []):
                self._buffer.append(ProxyPick(...))
```

**Result:** 500 Redis calls/sec → 5-10 calls/sec (50-100× reduction).

**Why it's clean:** `ProxyPool` is a dedicated abstraction (SRP).  The public
interface `pick() -> ProxyPick | None` doesn't change — callers are unaffected.
Double-checked locking is a standard lazy-init pattern.

---

## 4. Lazy Initialization (avoid seed-in-__post_init__)

**Problem:** `__post_init__` creates `random.Random(seed)` on every context
creation, even when the template has no RNG macros.

**Solution:** Make the expensive object a lazy property:

```python
@dataclass(slots=True)
class MacroContext:
    _rng: random.Random | None = field(init=False, repr=False, default=None)

    @property
    def rng(self) -> random.Random:
        if self._rng is None:
            self._rng = random.Random(self.rng_seed)
        return self._rng
```

**Why it's clean:** no side-effects in `__post_init__`.  The constructor does
exactly what it says — allocates fields.  The expensive work happens only on
demand.

---

## 5. Tell, Don't Ask (move render to the compiled object)

**Problem:** `render_compiled()` reaches into `CompiledTemplate` to grab
`scalar_names`/`object_names`, resolves them externally, then calls
`compiled.root.build()`.  The knowledge of *how* to render is split across
two objects.

**Solution:** Give `CompiledTemplate` a `render(registry, ctx)` method:

```python
class CompiledTemplate:
    def render(self, registry, ctx):
        scalars = registry.resolve_scalars_ordered(self._scalar_names, ctx)
        objects = registry.resolve_objects_ordered(self._object_names, ctx)
        return self.root.build(scalars, objects)
```

Caller becomes:
```python
return compiled.render(self._registry, ctx)
```

**Why it's clean:** the template owns its render path.  `MacroService` becomes
a thin coordinator — it doesn't need to know about `root.build()`, scalar/object
separation, or resolution order.

---

## 6. Measure Before You Optimize

Every performance claim must be backed by a micro-benchmark.  In this project,
intuition said "macro rendering is the CPU bottleneck" — measurement showed
37K renders/sec (= 26 µs/render, <2% CPU at 500 rps).  The real bottlenecks
were event-loop overhead (scheduling 30K coroutines) and Redis round-trips.

```python
N = 10_000
start = time.perf_counter()
for i in range(N):
    svc.render_compiled(tpl, 1, runtime={...})
elapsed = time.perf_counter() - start
print(f'{N/elapsed:.0f} renders/sec')
```
