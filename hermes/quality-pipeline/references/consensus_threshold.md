# Consensus Threshold Calculation

## Purpose
Calculate inter-rater agreement (κ) and derive consensus verdicts.

## κ Calculation

### Fleiss' Kappa for Multiple Raters
```python
from statsmodels.stats.inter_rater import fleiss_kappa

# Load judge verdicts
judges = ['judge1', 'judge2', 'judge3']
units = ['unit1', 'unit2', 'unit3']
ratings = [
    [0, 1, 0],  # unit1: 0=ok, 1=issue
    [1, 1, 0],  # unit2
    [0, 0, 1],  # unit3
]

kappa = fleiss_kappa(ratings)
print(f"Fleiss' kappa: {kappa:.3f}")
```

### Threshold Interpretation
- κ < 0: Chance agreement
- 0-0.2: Slight agreement
- 0.21-0.4: Fair agreement
- 0.41-0.6: Moderate agreement (our threshold)
- 0.61-0.8: Substantial agreement
- 0.81-1: Almost perfect agreement

### Consensus Workflow

1. **Load verdicts**: All judge results from tools/judge/
2. **Calculate agreement matrix**: Pairwise Cohen's kappa between all judge pairs
3. **Compute Fleiss' kappa**: Overall agreement across all judges
4. **Apply threshold**: κ ≥ 0.5 → consensus, κ < 0.5 → needs_review
5. **Majority vote**: For consensus units, vote on issue_type
6. **Tie-breaking**: Use severity order (critical > major > minor)

## Agreement Matrix

```python
from sklearn.metrics import cohen_kappa_score

judges = ['judge1', 'judge2', 'judge3']
pairs = [(judges[i], judges[j]) for i in range(len(judges)) for j in range(i+1, len(judges))]

for judge1, judge2 in pairs:
    kappa = cohen_kappa_score(judge1_ratings, judge2_ratings)
    print(f"{judge1} vs {judge2}: κ = {kappa:.3f}")
```

## Consensus Rules

### Quorum Requirement
- Minimum 3 judges per unit for meaningful κ
- Units with <3 judges are excluded from consensus

### Disagreement Resolution
- **Majority vote**: If ≥50% agree on issue_type, use that verdict
- **Tie-breaking**: Use severity order (critical > major > minor)
- **No consensus**: If <50% agree, mark as needs_review

### Output Format
```json
{
  "consensus": {
    "unit1": {
      "issue_type": "reversed_logic",
      "agreement": 0.67,
      "judges": ["judge1", "judge2"]
    }
  },
  "kappa": 0.52,
  "threshold": 0.5,
  "needs_review": ["unit3"]
}
```

## Pitfalls
- **Fleiss' kappa required**: Not Cohen's kappa (for 2 raters only)
- **κ threshold is 0.5**: Not 0.7; moderate agreement sufficient
- **Majority vote required**: Cannot force consensus without agreement
- **Tie-breaking by severity**: Critical issues override minor disagreements
- **Agreement matrix is symmetric**: Calculate once, reuse for all comparisons
- **Low κ is data**: Don't force consensus; indicates genuine ambiguity
- **Quorum enforcement**: Units with insufficient judges cannot reach consensus
