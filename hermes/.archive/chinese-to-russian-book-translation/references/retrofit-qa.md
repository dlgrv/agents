# QA workflow for inserted [рус. «…»] in source lines

## Purpose
This workflow is used for quality assurance after inserting Chinese source names in Russian translation source lines (`[рус. «…»]`). It replaces slow whole-chapter checks with efficient unit-based QA.

## Problem solved
Whole-chapter QA by subagents regularly times out (50+ minutes per chapter) due to large file sizes (100–200 KB). Unit-based QA completes in 1–3 minutes per unit and scales linearly.

## Procedure

### 1. Prepare QA units
- Extract all source lines with `[рус. «…»]` from all Russian markdown files
- Pair each RU line with its corresponding ZH original (by chapter and position)
- Split into units of 10–15 lines each
- Write each unit to a separate markdown file with clear instructions

### 2. Dispatch subagents
- Assign 4–5 units per subagent (adjust based on expected duration)
- Each subagent reads only its assigned unit files
- Subagents write JSON verdicts ONLY to designated verdicts directory
- **Critical:** Subagents must NOT edit any files in the book/ directory

### 3. QA checks per unit
For each ZH/RU pair in the unit, verify:
1. **Translation accuracy:** Is `[рус. «…»]` a correct translation of the Chinese name?
2. **Position correctness:** Is the insertion placed correctly (after title, before parentheses, not breaking DOI/URL/author lists)?
3. **Payload integrity:** After removing all `[рус. «…»]`, does the RU line match the ZH line byte-for-byte (except field labels: `来源：` → `Источники:`)?

### 4. Verdict format
Each subagent writes a JSON file immediately after completing its unit:
```json
{
  "unit": N,
  "checked": N,
  "issues": [
    {
      "file": "book/ru/filename.md",
      "line": NN,
      "problem": "Brief description in Russian"
    }
  ]
}
```
Empty issues array = no problems found.

### 5. Centralized fix application
- Aggregate all verdict JSON files
- Apply fixes using exact string matching with `patch` tool
- Re-run verification scripts after fixes to ensure no unintended changes

## Directory structure
```
/root/htlb-run/qa-retrofit/
├── units/          # QA unit files (unit-01.md, unit-02.md, ...)
├── verdicts/       # JSON verdicts from subagents
└── batches.json    # Metadata for unit distribution
```

## Pitfalls
- **Never let subagents edit book/ files:** Use isolated verdict-only workflow to prevent conflicts in shared worktrees
- **Aggregate before fixing:** Collect all verdicts before applying fixes to avoid partial updates
- **Verify after fixes:** Run structure verification scripts again after applying QA fixes
- **Unit size balance:** Too small = too many files; too large = timeout risk. 10–15 lines is optimal

## Time comparison
- Whole-chapter QA: 50+ minutes per chapter (frequent timeout)
- Unit-based QA: 1–3 minutes per unit, scales with line count
- Speedup: ~20x for typical chapters (100+ lines)
