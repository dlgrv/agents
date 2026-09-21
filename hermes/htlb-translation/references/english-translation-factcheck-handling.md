# English Translation Fact-Check Gate (Pass E) Handling

## Overview

The fact-check gate (pass E) uses source-grounded verification to detect meaning changes between Chinese source and English translation. Unlike verify.py, it focuses on semantic fidelity, not formatting.

## Judge Workflow

### Judge Prompt Structure

Judges compare Chinese source and English translation, returning strict JSON:

```json
{
  "assertions": [
    {"cn_span": "verbatim substring of the CHINESE source, ≥4 contiguous chars, copied exactly",
     "claim": "what the source asserts, one short sentence",
     "status": "ok | issue",
     "issue_type": "dropped_condition|hardened_claim|reversed_logic|softened_claim|added_advice|subject_swapped|cross_unit_contradiction|invented|other",
     "span_supports_claim": true,
     "detail": "what exactly is wrong in the failing language translation(s)"}
  ]
}
```

### Issue Types (Severity)

- **Critical**: reversed_logic, invented, dropped_condition (meaning changes)
- **High**: hardened_claim, softened_claim (strength changes)
- **Medium**: added_advice, subject_swapped (participant changes)
- **Low**: cross_unit_conduction, other

## Running Fact-Check Judges

### Manual Judge Dispatch

```bash
cd /tmp/htlb-vw
# Run 4 judges in parallel (one per article)
delegate_task tasks=[...]
```

Each judge processes one article, returning JSON verdict.

### Fact-Check Gate Runner

```python
# Run verdicts through tools/validate/factcheck.py
import subprocess
import json

# Example for one article
cmd = [
    "python3", "tools/validate/factcheck.py",
    "--chapter", "90-marriage",
    "--lang", "en",
    "--cn-unit", "docs/结婚划不划算.md",
    "--tr-unit", "docs/en/结婚划不划算.md",
    "--stdin-verdict", verdict_json,
    "--outdir", "tools/validate/results/factcheck"
]
result = subprocess.run(cmd, capture_output=True, text=True)
output = json.loads(result.stdout)
print(f"Grounded: {output.get('grounded')}")
```

## Common False Positives

### 1. Legal Regulation Titles
**Pattern**: `The General Office of the State Council measures in April 2026 on accelerating the building of pooling region (统筹地区 — the locality where you are insured)`
**Status**: Valid — CJK in parentheses with English explanation
**Exclusion**: Lines matching `\([^)]*\u4e00-\u9fff[^)]*—[^)]*\)` are glosses, not translation errors

### 2. Emergency Numbers
**Pattern**: `Call 120 (for China — 112/103, for RF — 103)`
**Status**: Valid — localization in parentheses
**Exclusion**: Emergency numbers remain as realia with localized equivalents noted

### 3. Document Codes and Legal IDs
**Pattern**: `国食药监办〔2010〕432 号`
**Status**: Valid — preserved byte-for-byte as per TRANSLATION.md
**Exclusion**: Chinese legal/administrative identifiers are not translated

### 4. Numeric Conversions
**Pattern**: `610.6 万 → 6.106 million`
**Status**: Valid — pure numeric conversions are out of scope
**Exclusion**: Only report if conversion flips meaning (e.g., "up to X" → "at least X")

## Quality Gate Logic

### Pass E Gate Logic
- **Major issues**: reversed_logic, invented, dropped_condition → FAIL
- **Minor issues**: hardened_claim, softened_claim, added_advice, subject_swapped → WARN/advisory
- **Grounding check**: Each cn_span must be verbatim from CN source after normalization
- **Exclusions**: Numeric conversions, translator headers, parenthetical first-use glosses

### Running the Gate

```bash
# Prepare worktree with CN articles as pseudo-chapters
cp "docs/结婚划不划算.md" book/90-marriage.md
cp "docs/家庭应急装备清单.md" book/91-emergency-kit.md
cp "docs/遇到陌生人出事该不该停.md" book/92-stranger.md
cp "docs/做平台要book/93-platform.md

# Run verify.py (may show FAIL due to CJK in legal titles)
for n in 90 91 92 93; do python3 tools/verify.py $n --lang en --file "docs/en/$(python3 -c "print(['结婚划不划算','家庭应急装备清单','遇到陌生人出事该不该停','做平台要办哪些证'][$n-90])").md"; done

# Run factcheck judges and gate runner
python3 /tmp/run_pass_e.py
```

## Pitfalls

### 1. Verify.py vs Fact-Check Scope
- **verify.py**: CJK formatting, numbers, field markers, calques
- **factcheck.py**: Semantic meaning changes, source-grounded assertions
- **Legal titles**: CJK in English text is valid for factcheck but may trigger verify.py FAIL

### 2. Grounding Check Failures
- **Issue**: cn_span doesn't match normalized CN text
- **Fix**: Ensure cn_span is copied verbatim, no paraphrasing
- **Prevention**: Include in judge prompt: "cn_span MUST be verbatim from the CN file; if you cannot ground a claim in a span, omit the claim"

### 3. Timeout Pattern in Judges
- **Issue**: Judges stall in analysis loop, no JSON output
- **Fix**: Restart with strict instruction: "FIRST tool call must be write_file with JSON verdict"
- **Prevention**: Include in judge prompt: "Do NOT re-read or analyze — return JSON immediately"

## Integration with Pipeline

Fact-check gate is pass E in the pipeline order:
1. translate → assemble → verify(FAIL)
2. **factcheck E** (FAIL for majors, advisory for minors)
3. style A (WARN only)
4. QE B (advisory)
5. judge C/D (advisory)
6. MQM (human priority)
7. MR + squash

## Quality Standards

- **Major issues**: 0 allowed (reversed_logic, invented, dropped_condition)
- **Minor issues**: Acceptable with review (hardened_claim, etc.)
- **Grounding**: 100% of assertions must be source-grounded
- **CJK handling**: Legal titles with glosses are valid

## Example Workflow

```bash
# 1. Run factcheck judges
delegate_task tasks=[4 judges]

# 2. Run gate runner
python3 /tmp/run_pass_e.py

# 3. Review results
# - If majors found: fix and re-run
# - If minors only: proceed with advisory note
# - If grounded=true: pass E gate

# 4. Continue with pipeline
```