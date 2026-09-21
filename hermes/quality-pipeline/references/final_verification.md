# Final Verification Protocol

## Purpose
End-to-end pipeline test with regression guard and smoke test.

## Verification Workflow

### 1. Regression Guard
```bash
# Compare against verify.py baseline
python3 tools/validate/verify.py --chapters 01,13,24 --lang ru --baseline tools/validate/results/baseline.json
```

### 2. Smoke Test
```bash
# Run all validation passes with minimal data
python3 tools/validate/smoke_test.py --chapters 01,13 --lang ru
```

### 3. End-to-End Test
```bash
# Execute full pipeline on sample chapters
python3 tools/validate/final_verification.py --chapters 01,13,24 --lang ru
```

### 4. Output Validation
```bash
# Check JSON outputs are valid and consistent
python3 -m json.tool tools/validate/results/final_report.json
python3 -m json.tool tools/validate/results/regression_guard.json
python3 -m json.tool tools/validate/results/smoke_test.json
```

### 5. Error Handling
```bash
# Test graceful degradation when components missing
export QE_VENV_MISSING=1
python3 tools/validate/final_verification.py --chapters 01 --lang ru
unset QE_VENV_MISSING
```

## Expected Outputs

### Final Report
```json
{
  "pipeline_version": "1.0.0",
  "chapters_tested": ["01", "13", "24"],
  "languages_tested": ["ru"],
  "passes": {
    "A": {"status": "passed", "units": 3},
    "B": {"status": "passed", "units": 3},
    "C": {"status": "passed", "units": 3},
    "D": {"status": "passed", "units": 3},
    "E": {"status": "passed", "units": 3},
    "F": {"status": "skipped", "units": 0, "reason": "venv missing"},
    "G": {"status": "passed", "units": 3},
    "H": {"status": "passed", "units": 3},
    "I": {"status": "passed", "units": 3},
    "J": {"status": "passed", "units": 3}
  },
  "consensus": {
    "kappa": 0.52,
    "threshold": 0.5,
    "needs_review": []
  },
  "regression": {
    "baseline_match": true,
    "deviation": 0.0
  }
}
```

### Regression Guard
```json
{
  "baseline_version": "2026-09-18",
  "chapters_compared": ["01", "13", "24"],
  "deviation": 0.0,
  "match": true,
  "details": {
    "01": {"old_score": 0.85, "new_score": 0.85},
    "13": {"old_score": 0.92, "new changes": []},
    "24": {"old_score": 0.78, "new_score": 0.78}
  }
}
```

### Smoke Test
```json
{
  "test_duration": 45.2,
  "passes_executed": 10,
  "passes_passed": 10,
  "passes_skipped": 0,
  "errors": [],
  "warnings": []
}
```

## Pitfalls
- **Regression guard first**: Always compare against verify.py baseline; changes must be intentional
- **Smoke test with minimal data**: Use 1-2 chapters, not full corpus, to catch interface errors
- **Graceful degradation required**: Missing components should SKIPPED, not FAIL
- **Output validation**: Check JSON syntax, required fields, and logical consistency
- **Error propagation**: Ensure errors in early passes don't break later passes
- **Component independence**: Each pass should work standalone; failures shouldn't cascade
- **Performance baseline**: Measure execution time; significant slowdowns indicate inefficiency
- **Memory usage**: Monitor memory consumption; large batches should not cause OOM
- **Parallel execution**: Verify parallel subagent dispatch works correctly
- **File cleanup**: Ensure transient directories are properly cleaned up
