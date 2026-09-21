# Golden Set Validation for Quality Pipeline

## Purpose
Validate new judges and pipeline components against known good translations before production deployment.

## Scope
- **B-variants:** Controlled degradations of A-variants (golden originals)
- **Blind validation:** Judge B-variants vs A-variants as if original
- **Metrics:** native_preference (should be 1.0), decoy_fp_rate (should be 0.0)
- **Validation threshold:** Only enable if both metrics pass thresholds

## Degradation Recipes
From tools/validate/golden_pairs.py:
- **officialese**: Replace common words with bureaucratic terms (e.g., «метод» → «методология»)
- **passive_chain**: Stack passive participle constructions (e.g., «было проведено исследование»)
- **jargonize**: Swap common words for professional jargon without explanation (e.g., «лекарства» → «препараты»)
- **long_sentence**: Chain clauses into >25-word sentences (complex syntax)
- **which_chain**: Add ≥3 "который" clauses (nested relative clauses)
- **unexplained_abbrev**: Use unexplained abbreviations (e.g., «ОМС без расшифровки»)

## Workflow

### 1. Generate B-variants
```bash
delegate_task(
    goal="Generate B-variants for golden set validation",
    context="Apply degradation recipes from tools/validate/golden_pairs.py to A-variants in tools/digest/golden/*.json. Write to tools/digest/golden_b_*.json. Validate with tools/validate/golden_pairs.py validate"
)
```

### 2. Blind validation
```bash
delegate_task(
    goal="Blind judge validation",
    context="Judge B-variants vs A-variants as if original. Judge should prefer A-variants (native preference) and reject decoys (FP rate). Write metrics to tools/validate/results/blind_validation.json"
)
```

### 3. Metrics evaluation
- **native_preference**: should be 1.0 (judge always prefers original)
- **decoy_fp_rate**: should be 0.0 (no false positives on decoys)
- **Enable threshold**: Only if both metrics pass

## Key Principles
- **Validate-before-enable**: New judges must prove effectiveness on golden set before production
- **Controlled degradations**: Use systematic degradation recipes, not random changes
- **Blind testing**: Judge doesn't know which is original (prevents bias)
- **Metrics-driven**: Quantifiable thresholds for go/no-go decision
- **Adversarial testing**: Include decoys (identical pairs) to test FP rate

## Pitfalls
- **Never skip validation**: Always test new judges on golden set before production
- **Recipe consistency**: Use the same degradation recipes across all validation runs
- **Blind protocol**: Ensure judge doesn't see metadata that could reveal original
- **Metric interpretation**: native_preference < 0.8 indicates judge is broken; decoy_fp_rate > 0.1 indicates poor specificity
- **Update golden set**: When translation quality improves, regenerate golden variants
- **Mutation anchor sync**: When updating chapter text, regenerate mutation anchors to match new text
