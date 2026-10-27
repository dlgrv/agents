# Mutation Test Specification

## Purpose
Define mutation testing for translation quality validation.

## Mutation Types

### Major Issues (FAIL gates)
- **reversed_logic**: Inverts cause-effect relationships (e.g., «лекарство снижает давление» → «давление снижает лекарство»)
- **invented**: Adds unsupported claims (e.g., «препарат одобрен FDA» without evidence)
- **dropped_condition**: Omits critical constraints (e.g., «только для взрослых» omitted)

### Minor Issues (WARN only)
- **softened_claim**: Weakens assertions (e.g., «100% эффективен» → «часто эффективен»)
- **added_advice**: Inserts unsolicited recommendations (e.g., «обязательно проконсультируйтесь с врачом»)
- **subject_swapped**: Changes subject without altering logic (e.g., «пациенты» → «люди»)
- **cross_unit_contradiction**: Contradicts other chapters (e.g., chapter 01 says X, chapter 02 says not X)

### Valid (ok)
- **ok**: No detectable issue
- **unknown**: Issue not covered by taxonomy

## Test Structure

### Anchors
- **RU anchors**: chapters 01, 13, 24 (3 chapters)
- **EN anchors**: chapter 13 (1 chapter)
- **Total anchors**: 4 chapters × 5 mutants each = 20 mutants
- **Controls**: 20 identical pairs (decoys)
- **Total test cases**: 40 pairs

### Mutation Implementation
- **tools/validate/results/mutations_seed42.json**: Mutation anchors
- **tools/validate/mutation_test.py**: Test runner
- **tools/validate/tests/test_mutation_spec.py**: Specification validation

## Catch Rate Protocol
- **Major issues**: E must flag ≥80% of mutants with issue_type in {reversed_logic, invented, dropped_condition}
- **False positives**: FP ≤10% on controls (decoys)
- **Novelty vs verify.py**: ≥70% agreement with existing verify.py logic

## Pitfalls
- **Anchor regeneration**: When updating chapter text, regenerate mutation anchors to match new text
- **Service-line detection**: Spans sitting ON service lines (来源/§SRC§/成本标签/证据等级) are dropped; spans merely containing service markers are kept
- **Whitespace normalization**: Collapse whitespace before span position lookup in CN text
- **Ellipsis handling**: Split spans with …/.../…… into fragments; each fragment must ground in order
- **Multi-line spans**: Check EVERY line touched by span for service lines, not just first/last
- **Error verdict handling**: Broken verdicts are gated as `error`, not silently dropped
- **Contract schema sync**: Factcheck gate expects `status` field, not `ru_ok`/`en_ok`
- **Hardened claim defense**: Assertions with `hardened_claim=true` are immune to major gates
- **Span supports claim**: Assertions with `span_supports_claim=false` are dropped immediately
