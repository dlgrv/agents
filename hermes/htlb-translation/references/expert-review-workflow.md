# Expert Review Workflow

## Overview

Independent adversarial evaluation of the HTLB quality pipeline to validate statistical soundness, code quality, and translation QA science alignment. Produces actionable findings that improve pipeline robustness before publication.

## Execution Pattern

### 1. Adversarial Test Case Generation

**Goal**: Create test cases that exercise edge cases and attack vectors
**Implementation**:
- Generate reverse-engineered attack vectors (e.g., malformed JSON verdicts, edge-case spans, broken field markers)
- Create 3–5 adversarial test suites covering:
  - Contract schema violations (missing fields, wrong types)
  - Grounding edge cases (ellipsis spans, multi-line spans touching service lines)
  - Mutation control failures (false positive mutants)
  - Golden set contamination (duplicate pairs, broken degradations)
- Write test suites to `tools/validate/tests/adversarial/`

### 2. Multi-Rater Expert Evaluation

**Goal**: Obtain independent assessment of pipeline components
**Implementation**:
- Dispatch 3–4 subagents with different expertise:
  - **Code quality expert**: Review architecture, test coverage, error handling
  - **Translation QA expert**: Review mutation taxonomy, judge prompts, golden set design
  - **Statistical validation expert**: Review κ calculation, catch-rate methodology, FP rate auditing
  - **Infrastructure expert**: Review deployment patterns, performance, scalability
- Each expert writes report to `tools/validate/results/expert_review_<expert_type>.md`
- Focus areas:
  - Statistical validation soundness
  - Code quality and maintainability
  - Translation QA science alignment
  - Edge case handling
  - Performance bottlenecks

###  reviews

**Goal**: Batch-fix multiple issues efficiently
**Implementation**:
- Aggregate all findings from expert reports
- Categorize by severity: critical (break pipeline), major (affect quality), minor (cosmetic)
- Batch-fix issues in logical groups:
  - Critical: Fix immediately, test locally (101/101 unit tests OK)
  - Major: Group related fixes, test as batch
  - Minor: Fix in separate commit if needed
- **Pitfall**: Never merge dirty branches — ensure all transient files are removed before squashing
- **Pitfall**: Test all fixes locally before committing (manifest valid, no test failures)
- **Pitfall**: Batch fixes that share root causes (e.g., schema sync + contract validation)

### 4. Publication Protocol

**Goal**: Merge validated improvements with confidence
**Implementation**:
- Squash all quality-pipeline commits into one clean commit
- Create MR with descriptive title including 'quality-pipeline'
- Include summary of all expert reviews and fixes applied
- Post-merge verification: Run full pipeline test on main branch
- **Pitfall**: Post-merge verification mandatory — pipeline must work after squash
- **Pitfall**: Branch name convention — use quality/pipeline-v2 (or similar descriptive name)
- **Pitfall**: Publication is final — ensure all quality gates are passed before publishing

## Key Metrics

- **Critical findings count**: Should be 0 after fixes
- **Major findings count**: Should be minimized (<5 per review)
- **Test coverage**: All fixes must pass 101/101 unit tests
- **Manifest validity**: Golden pairs and mutation cases must be valid
- **Catch rate**: ≥80% on mutants after fixes
- **False positive rate**: ≤10% on controls after fixes

## Pitfalls

**Adversarial test design**: Test cases must be realistic, not contrived — focus on real-world failure modes.
**Expert bias**: Rotate expert types and ensure diverse perspectives.
**Fix validation**: Every fix must be tested locally before committing — no "it should work" assumptions.
**Merge hygiene**: Never merge transient files (tools/judge/, tools/validate/results/) — they are gitignored.
**Over-engineering**: Don't fix findings that are theoretical but not practically impactful.

## Integration with Pipeline

Expert reviews are scheduled:
- Before major pipeline version releases
- After significant architecture changes
- When adding new validation passes
- Quarterly for ongoing quality assurance

## Output Artifacts

- `tools/validate/tests/adversarial/` — test case suites
- `tools/validate/results/expert_review_<expert_type>.md` — detailed findings
- `tools/validate/results/expert_review_code.md` — aggregated code issues
- `tools/validate/results/expert_review_statistics.md` — aggregated statistical issues
- `tools/validate/results/expert_review_translation.md` — aggregated translation QA issues
- Git commit with all fixes applied
- Merge request with review summary
