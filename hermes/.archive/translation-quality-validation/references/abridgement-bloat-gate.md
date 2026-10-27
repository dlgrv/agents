# Abridgement vs Bloat Validation Gate

Gate for validating degradation pairs in HTLB pipeline v2. Ensures abridgement and bloat pairs pass semantic constraints.

## Gate Logic

### Abridgement Pairs
- **Rule**: May only remove text, never add content or change existing numbers/statistics
- **Allowed operations**: Remove sentences, remove clarifications, remove parenthetical notes
- **Forbidden operations**: Add new numbers, change statistics, introduce new concepts
- **Validation**: Check that numeric values and statistical terms (HR/RR/OR/CI) are identical in both variants
- **Error threshold**: Any number change = gate fail

### Bloat Pairs
- **Rule**: May only add text, never remove content or change existing numbers/statistics
- **Allowed operations**: Add bureaucratic phrasing, add redundant explanations, add filler phrases
- **Forbidden operations**: Remove sentences, remove clarifications, change numbers
- **Validation**: Check that all original numbers/statistics are preserved and no new numbers are introduced
- **Error threshold**: Missing original number = gate fail

## Implementation

Gate implemented in `tools/validate/check_degrade.py`:
- `abridgement_directional_gate`: Validates abridgement pairs (numbers can only decrease)
- `bloat_directional_gate`: Validates bloat pairs (numbers can only increase)
- `numeric_change_detection`: Catches invented statistics (e.g., 46% → 64%)

## Pitfalls

- **False positives from source variation**: If original text has multiple numeric representations (e.g., "1,000" vs "1000"), normalize before comparison
- **Unit conversion traps**: Never convert units (e.g., 万 → numeric) in gate logic — that's localization, not degradation
- **URL/DOI preservation**: URLs and DOIs must be byte-identical; gate should not flag URL shortening as number change
- **Statistical term preservation**: HR/RR/OR/CI values must be identical; percentages and confidence intervals unchanged

## Example Failure Cases

```python
# Abridgement FAIL: removes sentence with number
original = "HR 1.2 (95% CI 1.1-1.3)"
abridged = "HR 1.2"  # Missing CI → gate fail

# Bloat FAIL: adds invented statistic
original = "46% of users"
bloat = "64% of users"  # Invented number → gate fail

# Bloat PASS: adds bureaucratic filler
original = "Call 103"
bloat = "In the event of an emergency medical situation, you should call the emergency hotline number 103"  # OK
```