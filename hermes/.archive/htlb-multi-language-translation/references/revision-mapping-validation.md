# HTLB Revision Mapping Validation

## Purpose

Validate that revision tasks actually target units that changed between Chinese source versions, not just units with high alignment ratios based on headings.

## When to Use

- Before dispatching revision subagents
- When alignment ratios seem suspicious (r=1.0 for units that should have changed)
- When subagents report fewer units completed than expected
- When verify.py shows content mismatches despite high alignment

## Validation Process

### 1. Extract Pre and HEAD Units

```bash
cd /root/github/htlb-ru
# Get pre-version units
pre_units=()
for i in {1..18}; do
  pre_units+=("$(git show fe33acf^1:book/04-不要浪费时间.md | grep -A 20 "### $i\. " | head -20)")
done

# Get HEAD units
head_units=()
for i in {1..18}; do
  head_units+=("$(git show HEAD:book/04-不要浪费时间.md | grep -A 20 "### $i\. " | head -20)")
done
```

### 2. Calculate Actual Content Similarity

```python
import difflib

# Compare actual content, not just headings
for i, (pre, head) in enumerate(zip(pre_units, head_units), 1):
    ratio = difflib.SequenceMatcher(None, pre.strip(), head.strip()).ratio()
    if ratio < 0.95:  # Threshold for significant change
        print(f"Unit {i}: ratio={ratio:.3f} → NEEDS REVISION")
    else:
        print(f"Unit {i}: ratio={ratio:.3f} → NO CHANGE")
```

### 3. Verify Alignment Map Accuracy

```python
import json

# Load alignment map
with open('/tmp/align_map.json') as f:
    align_map = json.load(f)

# Check actual content vs alignment claims
for chapter, pairs in align_map.items():
    for pre_n, head_n, claimed_ratio in pairs:
        pre_content = pre_units[pre_n - 1]
        head_content = head_units[head_n - 1]
        actual_ratio = difflib.SequenceMatcher(None, pre_content.strip(), head_content.strip()).ratio()
        
        if abs(actual_ratio - claimed_ratio) > 0.1:
            print(f"{chapter} pre#{pre_n}→HEAD#{head_n}: claimed {claimed_ratio}, actual {actual_ratio:.3f}")
```

## Common Pitfalls

### Alignment Based on Headings Only

- **Problem**: Alignment tools may match only headings (r=1.0) while content changed significantly
- **Solution**: Always verify actual content similarity with `difflib.SequenceMatcher`
- **Example**: ch04 pre#10 vs HEAD#15 had r=1.0 but actual content ratio was 0.58

### Missing Revision Units

- **Problem**: Task specifications may exclude units that actually changed
- **Solution**: Include all units with content ratio < 0.95 in revise lists
- **Fix**: Use actual content diff, not alignment map, to determine revision scope

### Slot Numbering Changes

- **Problem**: New units shift existing slot numbers (e.g., pre#10 → HEAD#15)
- **Solution**: Use git history to locate original content and verify mapping
- **Command**: `git show fe33acf^1:book/04-不要浪费时间.md | grep -A 20 "### 10\. "`

## Validation Commands

```bash
# Quick check for units with significant changes
cd /root/github/htlb-ru
for ch in 04 12 20 23 31; do
  echo "=== Chapter $ch ==="
  for i in {1..20}; do
    pre=$(git show fe33acf^1:book/${ch}-不要浪费时间.md 2>/dev/null | grep -A 10 "### $i\. " | head -10)
    head=$(git show HEAD:book/${ch}-不要浪费时间.md | grep -A 10 "### $i\. " | head -10)
    if [ -n "$pre" ] && [ -n "$head" ]; then
      diff=$(diff -u <(echo "$pre") <(echo "$head") | grep -E "^[+-]" | grep -v "^---" | grep -v "^+++" | head -5)
      if [ -n "$diff" ]; then
        echo "  Unit $i: CHANGED"
      fi
    fi
  done
done
```

## Integration with Task Generation

When generating task specifications:

1. Load alignment map as initial guidance
2. Validate actual content similarity for all pairs
3. Include units with content ratio < 0.95 in revise lists
4. Exclude units with high actual content similarity (r > 0.95) from revision tasks
5. Document any discrepancies between alignment map and actual content

## Sample Validation Output

```
ch04 pre#10 → HEAD#15: claimed 1.0, actual 0.58 → NEEDS REVISION
ch04 pre#11 → HEAD#16: claimed 1.0, actual 0.91 → REVISE
ch04 pre#12 → HEAD#17: claimed 1.0, actual 0.86 → REVISE
ch04 pre#13 → HEAD#18: claimed 1.0, actual 0.87 → REVISE
```

## Decision Flow

1. **Load alignment map** from automated tool
2. **Validate actual content similarity** for each pair
3. **If actual ratio < 0.95**: include in revise list
4. **If actual ratio ≥ 0.95**: exclude from revision (fresh translation only)
5. **If claimed ratio >> actual ratio**: flag alignment tool issue for investigation
6. **Generate task specifications** with validated revise lists
