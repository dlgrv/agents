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

```bash
# From repo root with venv activated
python3 -m pytest tools/validate/tests/ tools/llm/tests/ -v

# Single file
python3 -m pytest tools/validate/tests/test_assemble.py -v --tb=short

# Verbose with stdout
python3 -m pytest tools/validate/tests/test_assemble.py -v -s
```

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

- Never use `monkeypatch.setattr(__main__, '__file__', ...)` — `__file__` doesn't exist under `exec(compile(...))`.
- `sys.exit("msg")` writes to stderr, not stdout — check both in assertions.
- Real tools use `ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — mirror the repo structure in temp so `root` resolves correctly.
- Tests must run without network access — all fixtures are local mock data.
