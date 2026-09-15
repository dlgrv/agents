# Edge-case test recipes for pre-commit review

Condensed, copy-pasteable patterns that surface real bugs during the
`requesting-code-review` Step 0 (expand edge-case tests before review).
These were validated in a real session hardening a debug MCP isolation guard.

## 1. Security boundary — test the ATTACKER cases, not just happy path

A guard with only an "allowed" test is unproven. For any authz/sandbox/validation
gate, write at minimum:

- missing credential/env var → REFUSED
- malformed/partial descriptor (e.g. object missing the key the guard reads) → REFUSED
- dependency throws (simulate the wrapped client throwing) → REFUSED (fail-closed)
- mismatched identity (declared sandbox ≠ realized target) → REFUSED
- exact canonical match → allowed

Node `node:test` shape:

```js
import test from 'node:test'
import assert from 'node:assert/strict'

const fakeCdp = (dataRoot) => ({ eval: async () => dataRoot })
const throwingCdp = (msg = 'eval failed') => ({ eval: async () => { throw new Error(msg) } })

test('refuses when descriptor missing', async () => {
  await assert.rejects(
    () => assertTargetAttested(fakeCdp(null), { expectedHome: '/tmp/sb', defaultHome: '/real' }),
    /no descriptor/
  )
})
test('refuses when cdp.eval throws', async () => {
  await assert.rejects(
    () => assertTargetAttested(throwingCdp('Target closed'), { expectedHome: '/tmp/sb', defaultHome: '/real' }),
    /no descriptor/
  )
})
```

Run: `node --test path/to/file.test.mjs`

## 2. Path canonicalization — `path.resolve` vs `fs.realpathSync`

Pitfall that produced a false REFUSE in review:

- `fs.realpathSync.native(p)` throws `ENOENT` if `p` does not yet exist
  (common for a freshly-created isolated sandbox home).
- `path.resolve(p)` is lexical, never throws, but does NOT collapse symlinks.
- On macOS `/tmp` is a symlink to `/private/tmp`, so
  `path.resolve('/tmp/sb')` (`/tmp/sb`) ≠ `path.resolve('/private/tmp/sb')`
  (`/private/tmp/sb`).

**Rule:** when BOTH ends of a comparison are formed by the same resolver
(typically `path.resolve(env.HOME)` on both sides — e.g. an Electron main
process writing the descriptor and the operator passing the same string),
compare with `path.resolve` on both. Do NOT use `realpath` unless both paths
are known to exist, or you'll get a false mismatch.

```js
export function canon(p) {
  try { return path.resolve(p) } catch { return p }
}
```

If you must realpath, guard the ENOENT:

```js
export function canon(p) {
  try { return fs.realpathSync.native(p) }
  catch { try { return path.resolve(p) } catch { return p } }
}
```
…but note this still mismatches when one side exists and the other doesn't.

## 3. Wrapped CDP/RPC clients — know the return shape

`cdp.eval(expr)` in `scripts/perf/lib/cdp.mjs` calls
`Runtime.evaluate({ expression, returnByValue: true, awaitPromise: true })` and
returns `r.result.value` — the UNWRAPPED value (string / null / object), NOT
`{ result: { value } }`.

So if your guard evaluates `globalThis.__X__ ? globalThis.__X__.key : null`,
the resolved value is directly the `key` (or `null`), and an object form
`{ key: '...' }` arrives as the bare object. Handle both:

```js
const d = await cdp.eval(expr)
const realized = typeof d === 'string' ? d : (d && d.key) || null
```

Assert against the bare value, never a `{ result }` wrapper.
