# Debug MCP isolation guard — target attestation (post-P1 review)

## Why the guard changed shape

The first design, `assertSandboxed()`, only compared the caller-supplied
`DESKTOP_DEBUG_MCP_EXPECTED_HOME` against the operator's default `~/.hermes`.
A reviewer (PR #95781, `andrexibiza`) flagged it as a *qualified-identity*
defect: the coordinate describes intent but is not authority over the thing
actually connected. Exact adversarial case:

1. real Hermes Desktop runs on `~/.hermes` at CDP :9333
2. MCP launched with `EXPECTED_HOME=/tmp/fake-sandbox` + `ALLOW_ACT=1`
3. `connect()` finds the real target; `assertSandboxed()` sees
   `/tmp/fake-sandbox !== ~/.hermes` → passes
4. act tools hit the REAL target

So `assertSandboxed()` was replaced by `assertTargetAttested(cdp)`.

## The corrected design (target-derived authority)

`apps/desktop/electron/dev-cdp.ts`:
- `resolveDevCdpInstance({env, isPackaged, devServer})` → `{ nonce, dataRoot }`
  or `null` (null when CDP port closed). `dataRoot` is the canonical Hermes
  home the process actually runs against.

`apps/desktop/electron/main.ts`:
- Computes `DEV_CDP_INSTANCE` next to `DEV_CDP`.
- On `mainWindow.webContents` `did-finish-load`, when `DEV_CDP_INSTANCE` is
  set, runs `executeJavaScript('globalThis.__DEBUG_MCP_INSTANCE__ = <json>')`.
  The descriptor is written by the MAIN process (the CDP authority), never the
  renderer or a caller.

`apps/desktop/mcp/guard.mjs` (extracted from server.mjs so it is unit-testable):
- `assertTargetAttested(cdp, { expectedHome, defaultHome })`:
  - throws REFUSED if `expectedHome` unset
  - reads `globalThis.__DEBUG_MCP_INSTANCE__?.dataRoot` from the **connected
    target** via `cdp.eval(...)`
  - throws REFUSED if target exposes no descriptor (cannot prove sandbox)
  - throws REFUSED if `canon(realized) !== canon(expectedHome)`
- `canon(p)` = `path.resolve(p)` (canonicalize before compare).

Server dispatch calls `await assertTargetAttested(live, { expectedHome,
defaultHome })` for read tools AND act/flow tools (reads also disclose live
chat state, so they are gated too).

## P1-2 — ui_screenshot is read-only, no disk write

Old `screenshot()` did `fs.writeFileSync(path)` with a caller-supplied `path` →
arbitrary file overwrite (e.g. `ui_screenshot({path:'/home/me/.bashrc'})`) while
sitting in `readTools` (bypassing `ALLOW_ACT` + guard). Fix: return the capture
as MCP image content — `{ type:'image', data: shot.data, mimeType:'image/png' }`
+ a text block with `bytes`. Schema `path` property removed. Caller persists the
returned bytes if it needs a file.

## Test expectations (negative coverage the reviewer required)

`apps/desktop/mcp/server.test.mjs` (node:test) should cover:
- A) declared `/tmp/sandbox` but target proves `~/.hermes` → REFUSED
- B) exact match → allowed
- C) target exposes no descriptor → REFUSED
- D) incident shape (only USER_DATA_DIR set, target fell back to real home) → REFUSED
- P1-2: screenshot returns image content and writes no file; arbitrary `path`
  is ignored / refused.

## Honest residual risk (state it in the PR reply)

A CDP-attached attacker can `Runtime.evaluate` and overwrite
`globalThis.__DEBUG_MCP_INSTANCE__` in the renderer, because the descriptor lives
in renderer globals. The reviewer allowed the "target-derived path" shape
("compare canonicalized target-derived paths—not a second caller declaration"),
so this is acceptable for the dev-only threat model (#73121: CDP access already
equals arbitrary code execution). Stronger guarantee would need a main-signed
nonce over a side channel — flagged as future work, not blocking P1.

## Round 3 (2026-08-27, head 2931f2c7da) — the load-bearing P1: home authority

Reviewer accepted the screenshot fix but kept the identity P1 open:

- `dev-cdp.ts` derived `dataRoot` from `env.HERMES_HOME` alone while the app's
  real authority `main.ts::resolveHermesHome()` also honours
  `HERMES_DESKTOP_USER_DATA_DIR` (sandbox → `<userData>/hermes-home`), the
  Windows registry, and `%LOCALAPPDATA%`. Deterministic miss: USER_DATA_DIR-only
  launch → descriptor said `~/.hermes`, app used `<userData>/hermes-home`.
  "A proof emitted by the target is not sufficient if it is computed from a
  weaker coordinate than the one the target actually consumes."
- `guard.mjs` read `opts.defaultHome` but never used it →
  `expected === realized === ~/.hermes` passed, violating the contract.
- Should-fix: `desktop_ui_status` routed through connect+attest, so
  `cdpAlive:false` was unreachable.

Repair (required shape: ONE home authority; commits `55ec02a664`→`68a76633d1`):

1. `electron/hermes-home.ts` — `resolveHermesHomeFromInputs()`: pure, all inputs
   injected (`env, isWindows, appHome, userDataOverride, readWindowsUserEnvVar,
   directoryExists, pathModule`); ladder unchanged. `main.ts` = thin adapter.
   Cross-platform gotcha: `path.join` on macOS mangles Windows paths — inject
   `pathModule` (pass it through to `normalizeHermesHomeRoot` too) and use
   `path.win32` + win-style appHome in Windows test cases.
2. `dev-cdp.ts` consumes `DevCdpInput.resolvedHermesHome`; no env reading in
   the descriptor path. `main.ts` computes `HERMES_HOME` BEFORE
   `DEV_CDP_INSTANCE` (the old order was itself a bug).
3. `guard.mjs` — protected set = `{ defaultHome, os.homedir()/.hermes }`
   (second term covers a containerized server with no HERMES_HOME env; open
   question to reviewer whether an explicit config list is better), checked
   AFTER descriptor presence, BEFORE identity match. "Agreement is not
   permission." Never prove protected-home refusal against a live real-home
   instance — unit tests only.
4. Status preflight — early branch in `dispatch.mjs`; the ONLY tool bypassing
   the gate; negative test pins `ui_inspect` still refusing under dead CDP.

Reviewer's four deterministic regressions, all pinned RED-first:
USER_DATA_DIR-only launch → descriptor = `<userData>/hermes-home`; default
resolution cannot diverge from descriptor; protected triple-equal → REFUSED;
isolated exact match → allowed.

## Self-audit pass (2026-08-27 late, head 68a76633d1)

- A1 (HIGH): `invalidate()` documented as "must be called on socket close" but
  never called — renderer reload poisoned the cached handle until server
  restart. Fix: `connect()` subscribes `handle.ws` close with identity guard
  (`thisHandle`) so a stale socket's late close can't null a newer handle.
  Test-fake pitfall: store close listeners PER-SOCKET (a fake keeping only the
  latest fires the fresh socket's close when the test means the stale one).
- A2: `evalBounded` on `undefined` — `JSON.stringify(undefined)` is `undefined`
  → TypeError; fix `?? 'null'`.
- A3: act tools skipped the friendly selector guard (raw renderer SyntaxError);
  `requireSelector` exported from `tools/read.mjs`, applied before any CDP send
  (test spies zero sends/evals).
- A5: `CDP.eval` `r.result?.value` (malformed response → undefined, not throw).
- Cleared: console-ring wall-clock cutoff (same process); close-handler reject
  path (wrapped reject, no timer leak, no double-reject).

## Test-fake recipes worth reusing

- `countingCDP()`: per-socket close listeners + `closeSocket(n)` — enables both
  auto-invalidate and stale-guard tests.
- Silent WS + hand-rolled message pump: `new CDP(ws)` does NOT register the
  message listener (that's `CDP.open()`'s job) — tests must register the pump
  themselves before `send()` can resolve.
- Selector-guard spy: `sends.length === 0 && evals.length === 0` proves the
  guard fires before any CDP traffic, not just that the message is nice.
