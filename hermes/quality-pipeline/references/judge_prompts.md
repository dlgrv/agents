# Judge Prompt Templates

## Purpose
Unified 8-class taxonomy and prompts for all judge types.

## Taxonomy Classes
1. **dropped_condition** - Critical constraint omitted
2. **reversed_logic** - Cause-effect relationship inverted
3. **softened_claim** - Assertion weakened (e.g., "100%" → "often")
4. **added_advice** - Unsolicited recommendation added
5. **subject_swapped** - Subject changed without logic alteration
6. **cross_unit_contradiction** - Contradicts other chapters
7. **ok** - No detectable issue
8. **unknown** - Issue not covered by taxonomy

## Prompt Templates

### Screen Judge
```markdown
# Translation Quality Assessment

**Task**: Evaluate translation quality between two variants.

**Variant 1**: [A-variant text]
**Variant 2**: [B-variant text]

**Instructions**:
1. Compare both variants for translation quality
2. Identify issues using the 8-class taxonomy
3. For each issue, specify:
   - issue_type: One of the 8 classes
   - description: Clear explanation of the issue
   - severity: critical/major/minor
   - evidence: Text snippets supporting the verdict
4. Prefer Variant 1 unless it has clear issues
5. If both variants are equally good, mark as ok

**Output Format**:
{
  "verdict": "prefer_variant_1|prefer_variant_2|equal",
  "issues": [
    {
      "issue_type": "reversed_logic",
      "description": "Cause-effect relationship inverted",
      "severity": "critical",
      "evidence": "Original: 'лекарство снижает давление' → Translation: 'давление снижает лекарство'"
    }
  ]
}
```

### AB Judge
```markdown
# Translation Quality Assessment

**Task**: Evaluate translation quality between two variants.

**Variant A**: [A-variant text]
**Variant B**: [B-variant text]

**Instructions**:
1. Compare both variants for translation quality
2. Identify issues using the 8-class taxonomy
3. For each issue, specify:
   - issue_type: One of the 8 classes
   - description: Clear explanation of the issue
   - severity: critical/major/minor
   - evidence: Text snippets supporting the verdict
4. If Variant A has issues, mark prefer_variant_B
5. If Variant B has issues, mark prefer_variant_A
6. If both have issues, mark the worse one
7. If neither has issues, mark equal

**Output Format**:
{
  "verdict": "prefer_variant_A|prefer_variant_B|equal",
  "issues": [
    {
      "issue_type": "softened_claim",
      "description": "Assertion weakened",
      "severity": "major",
      "evidence": "Original: '100% эффективен' → Translation: 'часто эффективен'"
    }
  ]
}
```

### Factcheck Judge
```markdown
# Fact-Check Assessment

**Task**: Verify that translation claims are grounded in source text.

**Source Text**: [CN text with service markers]
**Translation Claims**: [List of claims to verify]

**Instructions**:
1. Filter source text: Remove service lines (来源, §SRC§, 成本标签, 证据等级)
2. For each claim, check if it exists in filtered source text
3. Classify issues:
   - grounded: Claim found in source text
   - ungrounded: Claim not found in source text
   - error: Malformed claim or source text
4. Major issues (reversed_logic, invented, dropped_condition) fail chapters
5. Other issues warn but don't fail

**Output Format**:
{
  "verdict": "pass|fail|warn",
  "issues": [
    {
      "claim": "препарат одобрен FDA",
      "status": "ungrounded",
      "issue_type": "invented",
      "severity": "critical",
      "evidence": "No FDA approval mentioned in source text"
    }
  ]
}
```

## Pitfalls
- **Prompt consistency**: All templates must use the same 8-class taxonomy
- **Audit fields required**: model_id, timestamp, prompt_hash, unit_sha256
- **Offline contract**: judge.py must work without network access
- **Output format**: Strict JSON structure required for parsing
- **Field mapping**: screen/ab use verdict string, factcheck uses status field
