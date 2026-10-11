---
name: tdd-red-phase-pitfalls
description: Use when writing failing-first tests or executing TDD plans.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [testing, tdd, code-review]
    related_skills: [test-driven-development, requesting-code-review, plan]
---

# TDD RED-Phase Pitfalls

## When to Use

Load this skill when writing failing-first (RED) tests, faking CDP/IPC/async
boundaries, executing a TDD-shaped plan, or updating tests after a
move-to-module refactor. Each entry here cost a debugging round in a real
session.

## 1. A failing test can fail for the wrong reason

A test whose bug is "this promise never resolves" shows up as
`cancelledByParent` / harness timeout, not a clean assertion failure. That IS
a legitimate RED — recognize it instead of assuming the test itself is broken.
When possible, prefer an assertion that fails cleanly.

## 2. Assert observable state, not fake internals

Call-counters on fakes (`discover.calls`) produce confusing `0 !== 1`
failures when the code under test catches and rewrites the error before the
counter matters. Prefer state the production code actually maintains:

```js
assert.equal(client.handle, null, 'handle must reset on failure')
```

## 3. A fake must mirror the real wiring

`new CDP(fakeWs)` has no `message` listener — the real factory registers one.
Tests then time out for reasons unrelated to the bug under test. Copy the
listener/handler setup the real construction path performs, or route through
the factory with the fake socket injected.

## 4. Fakes must return the shape the real caller produces

If production does `JSON.stringify(out)` or `.filter(...)`, a fake returning
`undefined` fails downstream with `Cannot read properties of undefined` —
unrelated to the bug. Have fakes return realistic values (`'[]'` for an
eval-based query).

## 5. Cross-platform path assertions: inject the path module

Don't assert literal `C:\...` strings in tests running on macOS/Linux.
Inject `pathModule` (`path.win32` / `path.posix`) into the function under
test. Check whether the repo already has a `{pathModule}` seam (many helpers
do) and reuse it rather than inventing a second one.

## 6. Negative pins catch what signatures hide

When asserting "output must equal the injected value, never re-derived"
(descriptor attests the realized home, resolver owns the value), also add a
decoy test: a plausible-looking env/input must NOT leak into the output. The
signature change alone doesn't prove the derivation is gone.

## 7. Static-source tests break on move-to-module refactors — update them first

Tests that grep a source file (`!src.includes('fs.writeFileSync')`,
`src.includes("type: 'image'")`) fail with misleading messages after the code
moved to a new module. When a plan extracts code, add a step: update every
static-source test to read the new module (and keep checking the old wiring
file if the constraint still applies there).

## 8. Extracting code from a giant file: order-of-init traps

Pulling a function out of a huge main file often requires moving its const
UP, above consumers that were previously later (e.g. a descriptor that now
needs the resolved home). Verify each new consumer's initialization order,
and grep for now-unused imports (`os`, the old helper) before committing.

## 9. Mock-hidden ctx contract drift — pin with the REAL handler

When a dispatcher builds a ctx/opts object and hands it to handler modules,
unit tests hide drift in two ways: handler tests inject their own ctx (with
whatever members they like), and dispatcher tests mock the handler entirely.
A handler that starts reading a ctx member dispatch never provides then ships
broken (`ctx.ensureCdp is not a function` reached production this way).

Pin the contract with an integration-shaped test: import the REAL handler
module, run it through the real `dispatchTool(...)`, mock only the transport
boundary (a recording fake CDP), and assert actual side effects (a CDP send
happened). On the old code it fails with the handler's own TypeError — the
exact production symptom. Add one such test per handler path (act AND flow),
so any future ctx member rename fails loudly with a pointer to the path.

## 10. Platform-assuming stub paths break on other OSes

A test stubbing a binary path hardcodes the Linux layout at its peril:
`/bin/true` does not exist on macOS (`/usr/bin/true`), so the stub yields
rc=127 and the test fails with `'127' !== '0'` — passing on Linux CI, so it
looks green until someone runs the suite on a Mac. Pick stub paths per
platform (`process.platform === 'darwin' ? '/usr/bin/true' : '/bin/true'`),
or resolve via `command -v`. Related macOS gaps to expect: no `setsid`
(code must take its nohup fallback), `/tmp` → `/private/tmp` symlink.

## 11. Regex escaping is eaten by template literals — lock it with a test

Code shipped inside a template literal (e.g. an expression string sent to
CDP eval) has its escapes interpreted once more: a single-escaped `\s` in a
JS template becomes `s` in the evaluated string (`/s+/g` — silently wrong),
while the correct source form is `/\\s+/g`. This broke in BOTH directions
while refactoring: the original had `\\s`, a rewrite "simplified" it to
`\s` and ate the backslash. Lock the wire format with a test asserting the
sent expression contains `/\\s+/g` (single backslash at the wire) and does
NOT contain the double-escaped form. Never "clean up" remote-expression
escaping by eye — the test is the only reliable reader.

## 12. A TypeError RED proves the test exists, not that it tests behavior

A RED that fails with `TypeError: object MagicMock can't be used in 'await'
expression` only proves the mocked method is absent — a stub returning the old
behavior would still pass it. When the plan's RED expectation is a TYPE error,
weaken the mock dependence before trusting the RED: make the assert a
behavioral one (`assert_awaited_once_with` on the real call shape, or an
outcome-value assert) so the failing line is about BEHAVIOR, not mock
plumbing. Squash commits hide RED phases from git history entirely — preserve
the RED output in the implementer's report/transcript as the evidence of
discipline instead of relying on history to show it.

## 13. Strict-xfail is the ledger for adversarial bug-hunting waves

When the goal is "find bugs with tests" (not TDD for a known feature), delegate test-writer agents that create ONLY new test files and never touch product code — a bug found and fixed by the same agent is unverified and unreviewable. Pin each reproduced bug as `xfail(strict=True)` with a BUG-id in the marker reason: the suite stays green, the bug cannot silently "pass" later, and XPASS-on-fix is the fix wave's acceptance criterion (remove the marker in the same commit as the fix). Record bugs in the report as file:line + repro + expected-vs-actual, not prose. Property/fuzz/chaos tests (boundary values, garbage input, concurrency stress, seeded randomness) find an order of magnitude more real bugs than coverage-chasing tests on legacy code — do not sell the user coverage numbers.

## 14. A probability gate in product code flakes deterministic tests

Any `random.uniform(...) >= chance` gate in a flow makes every deterministic test downstream flaky at rate (1-chance) — a default below 100% means ~1 in N runs fails with no code change. In tests, force the probability to a fixed endpoint (0 or 100) via the config seam, or seed the RNG; to test the gate itself, assert the AGGREGATE property over seeded runs (e.g. "50 seeded runs, zero fully-empty cascades at chance=95 with 2+ levels"), never a single run's outcome.

## 15. MagicMock(spec=...) returns Mocks for un-stubbed seam methods

A spec'd mock satisfies attribute checks but every un-stubbed method returns a Mock — code doing `len()`, iteration, or truthiness on the result fails with confusing Mock errors far from the seam. Old seam tests built on spec'd registries break when new production code calls a seam method the mock never stubbed. When adding a call to an existing seam, grep the test tree for spec'd fakes of that seam and stub the new method explicitly — do not assume spec protects you.

## See also

- `test-driven-development` (bundled) for the RED-GREEN-REFACTOR cycle itself.
- `requesting-code-review` for the review pass that typically surfaces the
  security/isolation pins referenced above (protected-home refusal, target
  attestation).
