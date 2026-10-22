---
name: htlb-testing
description: Use when writing tests for HTLB pipeline tools.
---

# HTLB Testing

How to write and run tests for the HowToLiveBetter translation pipeline.

## Architecture

Tests live alongside their tools:
- `tools/validate/tests/test_assemble.py` — assembly integrity tests
- `tools/validate/tests/test_make_digest.py` — chapter digest tests
- `tools/validate/tests/test_check_links.py` — link validation tests
- `tools/llm/tests/test_verify_adversarial.py` — adversarial verify tests
- `tools/validate/tests/test_factcheck.py`, `test_plainness.py`, `test_style_check.py`, `test_check_degrade.py`

## Test Design Rules

1. **Test the REAL tool, not a copy**: Use `shutil.copy2()` to mirror the repo structure in a temp directory, then `subprocess.run()` the real tool. Never inline the tool's code as a string in the test.

```python
def _setup_tmp_repo(tmp):
    tools_dir = os.path.join(tmp, "tools")
    os.makedirs(tools_dir)
    shutil.copy2(
        os.path.join(REPO_ROOT, "tools", "assemble.py"),
        os.path.join(tools_dir, "assemble.py"))
    # ... create mock book/, workdir/, etc.
```

2. **Mock minimal fixtures**: Create only what the tool needs — a minimal CN chapter, a minimal blocks.json, etc. Never use real data files.

3. **Assert on real behavior**: Check returncode, stdout patterns, and output file contents. Read the tool's source code to understand exit codes and error messages.

4. **Cover all error paths**: For every `sys.exit()` and error message in the tool, write a test that triggers it. Test valid paths AND invalid inputs.

## Running Tests

`make test` is the canonical entry (what CI's `test` workflow runs): pytest (translate/validate, translate/llm, forge/site) + all `node --test site/assets/*.test.mjs` files + Go api tests. Keep new test files registered in its `node --test` line in the Makefile — an unregistered test file never runs in CI.

```bash
# Full suite (what CI runs)
make test

# Single pytest file
python3 -m pytest translate/validate/tests/test_assemble.py -v --tb=short

# Single node test file (any file under site/assets/)
node --test <site/assets/FILE.test.mjs>
```

## Site (frontend) tests

The site parser/filter logic lives inline in `site/index.html`; `make web-build` copies it into every `site/<lang>/index.html`. Test it with `node:test` files in `site/assets/`:

- **Extract the logic under test from the BUILT page, not the source**: read each `site/index.html` and `site/<lang>/index.html`, pull the regex/expression out with a targeted `/e\.todo\s*=\s*(\/.*?\/[a-z]*)/`-style exec, compile with `new Function(...)`, and loop tests over every page. This fails both on a source regression AND on a forgotten rebuild of the locale copies.
- Run against realistic field samples in ALL languages, not just zh — the same markup is validated against translated text.
- **LANG is runtime-selected** (URL/localStorage/system) — every page carries the full multilingual branch chain, so test every LANG through every page, not one locale per page.
- **Extracting multi-branch ternary chains** (e.g. `e.dispute = LANG==='en' ? /re/.test(e.note) : ... : /re/.test(e.note);`): a non-greedy regex ending at the first `.test(` cuts inside the chain (branches each contain `.test(e.note)`) and compiles to garbage. Instead `indexOf('e.dispute =')` then slice to the next `;` and compile the whole statement with `var e = {note}; return <stmt>;`.
- To measure a marker/flag change on real data, grep only record fields (`^- ` lines) per language dir: `grep -rhE '^- ' book/<lang>/*.md | grep -cE '<pattern>'` — don't grep whole trees, translation subdirs nest inside `book/`.

## Test Coverage Categories

For EACH pipeline tool, ensure:
- **Happy path**: valid input → valid output, returncode 0
- **Error path**: invalid input → non-zero exit, sensible error message
- **Edge cases**: empty input, single item, maximum items, missing files
- **Language coverage**: tests for all supported languages (ru/en/es) where meaningful
- **Integrity checks**: source mismatch, tag count mismatch, item count mismatch
- **Warning-only**: behaviors that should warn but not fail (e.g. hanzi leftovers)

## Dependencies

```bash
pip install pytest pyyaml
```

`pyyaml` is needed for `tools/pipeline/config.py` (loaded by verify tests).

## Commit Convention

```
test(tool-name): describe what's tested

- test_file.py (N): specific test names
- Real tool execution via shutil.copy2 + subprocess
```

## Pitfalls

- **Never use a case-insensitive marker regex over multilingual text.** `/todo/i` also matches Spanish/Portuguese «todo(s)» («all») and the substring inside Indonesian «metodologi» — hundreds of false 'unverified' flags. Use `\bTODO\b` case-sensitive plus explicit phrase alternatives; the same trap applies to impact-count greps (`grep -i` overcounts identically).
- Never use `monkeypatch.setattr(__main__, '__file__', ...)` — `__file__` doesn't exist under `exec(compile(...))`.
- `sys.exit("msg")` writes to stderr, not stdout — check both in assertions.
- Real tools use `ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — mirror the repo structure in temp so `root` resolves correctly.
- Tests must run without network access — all fixtures are local mock data.
- **Marker filters must list every translated variant of the CN marker.** Translators render «争议» (contested) as different words per language: en `Contested/Disputed/Controversy`, ru `Спорно/Спорный`, es `En disputa/Controversia`, pt `Em disputa/Controverso`, ar `متنازع/خلاف`, id `Kontroversi`. Matching only one variant silently drops entries from the 'contested only' filter (was −114 records). Detect drift by cross-language count parity; find real variants by sampling `^- Примечания/Notes/Notas/...:` lines per language dir.
