---
name: core-coding-guidelines
description: Core behavioral guidelines to reduce common coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.
license: MIT
---

# Core Coding Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from observations on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Performance Proposals: Architecture First

**When proposing optimizations, lead with clean patterns — not micro-changes.**

The user's standard for performance work is: best practices, readable architecture, proper design patterns. Optimizations that make the code hackier or harder to follow are wrong, even if they're faster.

Before proposing an optimization:
- Is the fix a proper pattern (Factory Method, Lazy Init, Prefetch Buffer, SRP, Tell Don't Ask) — or a hack (swap one global for another, remove a safety wrapper, inline a constant)?
- Does the code become more readable or less? "Less code" is not the same as "cleaner code."
- Are you separating concerns (business logic vs infrastructure limits, I/O client vs buffer) or mixing them?
- If a one-liner would save 5% but obscure intent, skip it. A 5-line refactor that improves the design is worth more.

**Pitfall:** Proposing micro-optimizations (change a constant, remove a wrapper, swap a library) before examining the architecture. The user will redirect with "best practice, clean architecture, readable code" — skip to the architecture-level proposal immediately.

**Good proposal shape:**
```
| # | Было | Стало | Паттерн |
|---|---|---|---|
| 1 | Side-effect in __post_init__ | Lazy property + Factory Method | Lazy Init + Factory Method |
```

**Bad proposal shape:**
```
| # | Оптимизация | Строк кода | Прирост |
|---|-------------|-----------|---------|
| 1 | Убрать asyncio.wait_for | -5 | +3% |
```

### Pitfall: optimize before measuring

Never claim a bottleneck until you've measured it. Intuition is wrong more often than right. A component that looks expensive (macro rendering, JSON parsing) may be <2% CPU while the real bottleneck is elsewhere (event-loop overhead, I/O round-trips). Always run a micro-benchmark of the hot path in isolation before proposing changes.

**Concrete async patterns** (backpressure, prefetch buffers, lazy init, timeout-at-boundary, Tell-Don't-Ask) are catalogued in `references/async-performance-patterns.md`. Load that file when working on async Python throughput problems.

## 6. Ad-Hoc Verification

**When the project has no canonical test/lint/build command, verification is still mandatory.**

Create a focused temporary script:
- Write to `tempfile.gettempdir() / hermes-verify-<topic>.py`
- Number checks (`1.`, `2.`, ...), print `OK`/`FAIL` per check, exit non-zero on failure
- Cover: backward compat, new behavior, edge cases, imports
- Run it, confirm `ALL N PASSED`, delete the script

Good shape:
```python
failed = 0
def ok(desc, cond):
    global failed
    if cond: print(f'  OK  {desc}')
    else:    print(f'FAIL  {desc}'); failed += 1

print('1. Topic')
ok('check description', actual == expected)
...
print(f'\n{"ALL N PASSED" if not failed else f"FAILED {failed}"}')
sys.exit(0 if not failed else 1)
```

This proves correctness before declaring work done — even without an existing test suite.

### Pitfalls

**macOS /var/folders write restriction:** `write_file` refuses to write to `/var/folders/.../T` (system path guard). Instead, run the script inline via terminal:
```bash
/path/to/venv/bin/python -c "
... verification code ...
"
```
Do not waste turns fighting the path — pivot to inline on first refusal.

**Substring false positives:** When checking that a symbol was removed from source, a plain `'old_symbol' not in content` check can falsely match if `old_symbol` appears as a substring of the replacement (e.g., `'json.dumps'` inside `'orjson.dumps'`). Use a regex with a negative lookbehind: `not re.search(r'(?<!or)json\.dumps', content)` — or check for the exact standalone pattern.

**Inherited VIRTUAL_ENV pollution:** The Hermes agent's own venv (`~/.hermes/hermes-agent/venv`) leaks `VIRTUAL_ENV` and `PYTHONPATH` into subprocess environments. Even when invoking the project's venv Python binary, inherited env vars can redirect imports to the wrong site-packages. Always unset them:
```bash
env -u VIRTUAL_ENV -u PYTHONPATH /path/to/project/.venv/bin/python -c "..."
```

**`write_file` overwrites the ENTIRE file, not a partial slice:** `write_file` always overwrites the whole file — it is NOT a partial-line replacement tool. If you read a file with `offset`/`limit` and pass only the first N lines as content, everything else is silently deleted. Always re-read the full file without pagination before `write_file`, or prefer `patch(mode='replace')` for targeted edits. Reserve `write_file` for new files or when you have the verified complete content.

**Recovery from `write_file` data loss:** If you accidentally truncated a file, restore it immediately with `git checkout -- <file>` (discards uncommitted changes). Then re-apply your edits using `patch(mode='replace')` — never retry with `write_file`.

**Stale file reads after external modification:** If a file is modified externally (e.g., `git checkout`), the agent's cached read may be stale. When a `patch` diff shows success but the file content is unchanged, re-read the file and retry. If the same region fails twice, rewrite the function using verified complete content.

**Frontend-specific pitfalls** (Vite HMR caching after structural refactors, `patch` silent-failure recovery with `sed`, stale browser snapshots, CSS Grid `1fr` maxWidth illusion, flex centering patterns, `vite build` terminal rejection, design token audit workflow, chart null-value zero baseline rendering, `sed` producing broken template literals in single-quoted strings, root font-size inheritance on `<p>` containers, table padding compactness vs detail row height) are cataloged in `references/frontend-pitfalls.md`. Additional frontend references: `references/react-feature-removal.md` (tracing orphan chains when removing a cross-cutting feature like collapse/toggle), `references/duplicate-block-nesting.md` (eliminating double-wrapped title/border when migrating to CollapsibleSection). Load those files when working on frontend restructuring tasks.