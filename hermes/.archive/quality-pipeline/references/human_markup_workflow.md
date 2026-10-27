# Human-in-the-Loop Markup for Quality Validation

## Purpose
Create human evaluation sessions for validating judge performance and quality thresholds.

## Scope
- **Golden set markup**: Human evaluation of known good vs degraded translations
- **Compact presentation**: Only show differing lines between variants
- **Batch management**: Split pairs into manageable batches (10 pairs/batch)
- **Diff highlighting**: Visual highlighting of differences without bias

## Workflow

### 1. Generate Markup Session
```bash
python3 tools/validate/render_markup.py \
  --subset tools/validate/results/golden_lite_subset.json \
  --out /root/htlb-markup-lite.html \
  --diff-only \
  --title "Золотой сет ЛАЙТ — только различия"
```

### 2. Human Evaluation
Present pairs with differences highlighted:
- **Variant 1**: Left column with highlighted differences
- **Variant 2**: Right column with same highlights (neutral)
- **Instructions**: "1 = Variant 1 more natural, 2 = Variant 2 more natural, = equal"

### 3. Batch Processing
- **Batch 1**: 10 pairs (g01-g23)
- **Batch 2**: 10 pairs (g24-g48)
- **Response format**: Space-separated numbers (e.g., "1 2 = 2 1 1")

### 4. Metrics Calculation
```bash
python3 tools/validate/human_metrics.py \
  --labels golden_labels_lite.json \
  --judge-results golden_blind_summary.json \
  --output agreement_metrics.json
```

## Compact Mode (--diff-only)

### Features
- **Only differing lines**: Show only lines where variants differ
- **Aligned replacements**: Word-diff shows exact changes side-by-side
- **Whole-line inserts/deletes**: Marked with em-dash on opposite side
- **Identical pairs**: Labeled as "(варианты идентичны)"

### Example Output
```html
<div class="pair">
<h3>g01</h3>
<div class="var"><div class="lab">ВАРИАНТ 1</div>
<div class="txt"><mark>больше</mark> информации</div></div>
<div class="var v2"><div class="lab">ВАРИАНТ 2</div>
<div class="txt"><mark>большей будет сумма, которую</mark> информация</div></div>
</div>
```

## Pitfalls
- **Bias avoidance**: Highlight differences neutrally (same color in both variants)
- **Batch management**: Reset labels between batches to avoid carryover effects
- **Response format**: Use strict format to ensure consistent parsing
- **Markup validation**: Verify all pairs are presented correctly before evaluation
- **Diff algorithm**: Use word-level diff, not line-level, for precise change detection
- **Encoding**: Always use UTF-8 with BOM for text files, explicit charset for HTML
- **Markup persistence**: Save human labels for future validation and improvement
