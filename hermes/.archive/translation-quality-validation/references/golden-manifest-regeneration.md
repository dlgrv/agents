# Golden Manifest Regeneration and Pair Pinning

Strategy for regenerating HTLB golden manifest while preserving specific pairs for quality validation.

## Problem
When regenerating golden manifest (e.g., to increase decoy count from 10 to 36), fresh pairs shift and some original pairs may become decoys, breaking the mapping of degradation pairs.

## Solution: Hybrid Manifest Structure

Combine fixed pairs from previous manifest with fresh decoys from new selection.

### Step 1: Identify Target Pairs
- Load previous manifest with 18 target pairs (g01-g43, abridgement/bloat)
- Record original chapter/lang/stratum of each target pair

### Step 2: Regenerate Base Manifest
- Run `python3 tools/validate/golden_pairs.py select` to generate new 60-pair manifest with 36 decoys
- This creates fresh anchor and decoy pairs with new IDs

### Step 3: Reinsert Target Pairs
- For each original target pair, find matching chapter/lang/stratum in new manifest
- Replace the fresh pair with the original target pair (preserving degradation)
- Ensure original pair is marked as non-decoy with recipe assigned

### Step 4: Top Up Decoys
- Count remaining decoy slots needed to reach 36
- Randomly select non-target pairs from new manifest to convert to decoys
- Set variant_b = variant_a and recipe = None for these decoys

## Implementation

```python
# Pseudocode for reinsertion
original_pairs = load_previous_manifest("/tmp/old_manifest.json")
new_manifest = load_manifest("tools/validate/results/golden_manifest.json")

# Map original pairs to new manifest by content
for orig in original_pairs:
    if not orig["decoy"] and orig["id"] in TARGET_PAIRS:
        match = find_by_content(new_manifest, orig["variant_a"])
        if match:
            replace_pair(new_manifest, match["id"], orig)

# Top up decoys
decoy_count = sum(1 for p in new_manifest["pairs"] if p["decoy"])
if decoy_count < 36:
    candidates = [p for p in new_manifest["pairs"] 
                 if p["id"] not in TARGET_PAIRS and not p["decoy"]]
    to_convert = random.sample(candidates, 36 - decoy_count)
    for p in to_convert:
        p["decoy"] = True
        p["variant_b"] = p["variant_a"]
        p["recipe"] = None
```

## Pitfalls

- **Content collision**: If original pair content appears multiple times in new manifest, use first exact match
- **ID preservation**: Target pairs retain their original IDs (g01, g04, etc.) for consistent referencing
- **Recipe inheritance**: Original degradation recipes must be preserved when reinserting pairs
- **Fresh pair contamination**: Ensure no original target pairs are accidentally converted to decoys during top-up

## Validation

After regeneration:
1. Verify all 18 target pairs are present with correct degradations
2. Confirm decoy count is exactly 36
3. Check that target pair variants are not identical (non-decoy)
4. Run `python3 tools/validate/golden_pairs.py validate` to pass manifest validation