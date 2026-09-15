---
name: algorithm-porting
description: Use when porting/implementing a published algorithm or spec.
---

# Porting published algorithms

Reconstructing a published algorithm from remembered formulas produces code that looks right and fails subtly. In the FSRS-5 session (2026-09) a memory-based port mixed FSRS-4.5 and FSRS-5 semantics → 5 failing tests, fixed only after porting strictly from the canonical repo. The tests were right; memory was wrong.

## Workflow

1. **Find the canonical implementation** — the repo the algorithm's author maintains (e.g. py-fsrs / ts-fsrs for FSRS, not blog posts). Check the spec version explicitly; adjacent versions (FSRS-4.5 vs FSRS-5) differ materially in parameter count and formulas.
2. **Pin the exact version** in the plan (e.g. `py-fsrs v5.1.3`) — "latest" drifts.
3. **Tests FIRST with concrete values from the reference** (D0/S0 constants, weight vectors, a worked example from the reference's own test suite). RED before any implementation code.
4. **Port faithfully** — same formulas, same clamps, same ordering of operations. Deviate only for the host language, and note each deviation.
5. **Verify** — all reference-value tests green; if one fails, suspect the port, not the test.

## Anti-patterns

- Writing tests with values you *computed from your own implementation* — circular, catches nothing.
- Grabbing a random Medium article's formula set instead of the reference repo.
- Trusting an older reference (found first) when the plan specifies a newer spec version.

## Session detail

- `references/case-fsrs-5-flashcards.md` — FSRS-5 constants, grading mapping, deck-building sources, and the verification pattern from the dlgrv.com/english flashcards session.
