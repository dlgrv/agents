# Golden Set Validation for HTLB Quality Pipeline

End-to-end validation methodology for HTLB translation quality pipeline using golden pairs and judge review.

## Validation Architecture

- **Real pairs**: 18 pairs with controlled degradations (abridgement/bloat)
- **Decoy pairs**: 42 identical-twin pairs (A=B), FP bound ≤0.071
- **Total**: 60 pairs, judge blind run expected to prefer originals ≥100%

## Blind Judge Run Workflow

### Step 1: Prepare Markup File
Generate markup subset for human evaluation:

```python
import json, random
m = json.load(open('tools/validate/results/golden_manifest.json'))
real = sorted(p['id'] for p in m['pairs'] if not p['decoy'])
decoy_ids = sorted(p['id'] for p in m['pairs'] if p['decoy'])
rng = random.Random(77)
sample = decoy_ids[:12]  # Sample 12 decoys for interleaving
ids = real + sample
rng.shuffle(ids)
json.dump({"seed": 77, "ids": ids, "ref": "golden_manifest.json",
           "note": "lite2 markup: 18 real + 12 decoys, shuffled"},
          open('/tmp/lite2_subset.json','w'), indent=1)

python3 tools/validate/render_markup.py --subset /tmp/lite2_subset.json \
  --out /root/htlb-markup-lite2.html --diff-only --title "Золотой сет v2 — 30 пар"
```

### Step 2: Human Evaluation
Format: `g33 1` (1=prefer V1, 2=prefer V2, == for identical twins)

```bash
cat /tmp/human_eval.txt
g33 1
g24 2
g43 ==
...
```

### Step 3: Blind Judge Run
```bash
# Lite run (30 pairs, 4 workers)
python3 tools/validate/judge_blind_run.py --subset /tmp/lite2_subset.json \
  --out tools/validate/results/golden_judge_run_lite --workers 4

# Full run (60 pairs)
python3 tools/validate/judge_blind_run.py --subset tools/validate/results/golden_full_subset.json \
  --out tools/validate/results/golden_judge_run_full --workers 4
```

### Step 4: κ Calculation
```bash
python3 tools/validate/golden_collect.py collect
python3 -c "
import json
data = json.load(open('tools/validate/results/golden_blind_summary.json'))
print('κ:', data['inter_rater_reliability'])
print('native_preference:', data['native_preference'])
print('decoy_fp_rate:', data['decoy_fp_rate'])
"
```

## Validation Criteria

| Metric | Target | Pass/Fail |
|--------|--------|-----------|
| κ (Cohen's kappa) | ≥0.6 | Pass if κ ≥ 0.6 |
| Native preference | ≥1.0 | Judge always prefers original |
| Decoy FP rate | ≤0.0 | No false positives on identical twins |
| Order bias | ~0.5 | No AB/BA order effect |
| Length bias | 0/36 | No preference for shorter (since degradations lengthen) |

## Pitfalls

- **Stale verdicts**: Always archive v1 judge verdicts before v2 runs (they reference old manifest)
- **Subset randomness**: Use fixed random seed (e.g., 77) for reproducible subsets
- **Worker count**: Always use `--workers` to avoid file race conditions in judge_blind_run.py
- **Error files**: Only count files with `decoded` field as completed; `{"error":...}` files are invalid
- **ZAI_API_KEY**: Must be exported before running blind judge (uses GLM-5.3-Flash)

## Implementation Notes

- Judge uses z.ai GLM-5.3-Flash via `judge.py --model glm-5.3-flash`
- Offline judge contract works with `--model mock` (no API key needed)
- Mutation test anchors must be regenerated after manifest changes
- Final validation requires 101/101 unit tests and expert review zero critical findings

## Output Files

- `/root/htlb-markup-lite2.html` — Human evaluation markup (30 pairs)
- `tools/validate/results/golden_judge_run_lite/` — Judge verdicts
- `tools/validate/results/golden_blind_summary.json` — Aggregated metrics
- `tools/validate/results/golden_verdicts_v1_archive/` — Previous run results (archived)
