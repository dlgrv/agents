# Publication Merge Conflict Resolution

## Purpose
Handle merge conflicts during quality pipeline publication to main branch.

## Scope
- **Conflict types**: add/add conflicts in shared files (e.g., factcheck.py)
- **Resolution strategy**: prefer version with expert review fixes
- **Post-merge testing**: ensure pipeline functionality after conflict resolution

## Conflict Resolution Workflow

### 1. Identify Conflicts
```bash
git merge main --no-commit
# Inspect conflicted files: git status
```

### 2. Resolve add/add Conflicts
**Rule**: Prefer version with expert review fixes (our version is typically a superset)

**Example**: factcheck.py conflict
```bash
# Our version: 348 lines with expert review fixes
# Main version: 181 lines (older version)
# Resolution: Keep our version (contains: parse_error, ellipsis-grounding, span_supports_claim, hardened_claim)
```

### 3. Test Post-Resolution
```bash
git commit
python3 -m unittest discover -s tools/validate/tests  # should pass
python3 tools/validate/verify.py --chapters 01,13,24 --lang ru  # regression guard
```

## Expected Outputs

### Clean Merge
- No conflicts remaining after resolution
- All tests pass (126+ unit tests OK)
- Regression guard matches baseline

### Post-Merge Verification
```json
{
  "merge_status": "clean",
  "tests_passed": 126,
  "regression_match": true,
  "conflicts_resolved": ["factcheck.py"]
}
```

## Pitfalls
- **Never merge dirty branches** — ensure all transient files are removed before squashing
- **Squash after all tests pass** — don't squash if Task 13 fails; fix first
- **MR title must be descriptive** — include 'quality-pipeline' and scope (e.g., 'quality-pipeline: HTLB validation tier')
- **MR body should summarize changes** — list all validation tasks completed and key findings
- **Post-merge verification mandatory** — pipeline must work after squash; test on main branch
- **Transient file cleanup** — tools/judge/ and tools/validate/results/ must be gitignored and removed
- **Branch name convention** — use quality/pipeline-v2 (or similar descriptive name) for tracking
- **Squash preserves content** — don't squash until all files are properly committed; squash only combines commits, doesn't lose content
- **Review before merge** — if possible, have another agent review the MR for completeness
- **Publication is final** — once merged, changes go live; ensure all quality gates are passed before publishing
- **Expert review priority** — when conflicts occur, prefer the version with expert review fixes (typically our branch); our version is usually a superset of main's version
- **Test fixture refresh** — after merge, update test fixtures to match new main branch baseline (e.g., localized docs links in chapter 08 EN)
- **Golden manifest sync** — regenerate golden_manifest.json if chapter text changes after merge
