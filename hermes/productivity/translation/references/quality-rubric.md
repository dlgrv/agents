# Translation quality rubric (MQM-based)

Adapted from MQM / Multidimensional Quality Metrics (themqm.org) — functionalist: quality = accuracy + fluency for the audience and purpose, not 1:1 literalness. Use when reviewing translations.

## Dimensions and weights

| Dimension | Error examples | Weight |
|---|---|---|
| **Accuracy** | altered/lost numbers; dropped or added meaning; flipped negation; distorted HR/RR/OR/CI; "improved" claims not in the source; lost hedging (около / примерно / about) | CRITICAL ×5 |
| **Terminology** | wrong medical/legal/statistical term (e.g. mammogram → generic X-ray, eradicate → treat); term inconsistent across the file | MAJOR ×3 |
| **Fluency** | grammar, punctuation, garbled syntax, calques hard to parse | MINOR ×1 |
| **Style** | tone mismatch (original is restrained, no exclamation marks); titles not verb-first; register breaks | MINOR ×1 |
| **Readability** (project-specific) | plain-language explainer lines must read as natural speech, not calque; takeaway graspable in one pass; no sentence needs re-reading | MAJOR ×3 (those lines only) |

Severity multipliers: critical = 25, major = 5, minor = 1.

## Hard rules — automatic fail regardless of score

1. Any number, DOI, URL, or citation altered or lost.
2. Any HR/RR/OR/CI value or confidence interval wrong.
3. Machine-tag comments not byte-identical.
4. Citation/source lines not byte-identical after the field label.
5. Any invented content (facts, numbers, advice) absent from the source.
6. Missing status line / back-link / item-count mismatch with the source.

## Score

```
score = 100 − (Σ penalty × weight) / (words / 1000)
```

Pass thresholds:
- Accuracy and Terminology: ZERO critical, ZERO major (hard requirement).
- Fluency + Style combined: ≥ 95.
- Readability: ≥ 95, no major.

## Verity (NOT an error)

Facts true only for the source country are not accuracy errors when the country-disclaimer line is present. Do not "fix" them in translation; adaptation is out of scope.

## Review procedure

1. Source item and translated item side by side.
2. Annotate every error: dimension + severity + exact location.
3. Compute the score; list all hard-rule blockers.
4. Output verdict per item (pass / fix) and for the whole file, plus a fix list with CONCRETE suggested wording — never just "awkward".
