# Style Corpus Analysis

## Purpose
Analyze translation corpus for style patterns and markers.

## Scope
- **Corpus frequencies**: Scan entire translation for recurring patterns
- **Banned terms**: Reject specific phrases with regex patterns
- **Labels**: Mark translation style (plain/literary/technical)
- **False positive audit**: Sample chapters to verify markers are real issues

## Analysis Workflow

### 1. Corpus Frequency Analysis
```bash
python3 tools/validate/style_markers.py --lang ru
```

### 2. Banned Terms Detection
```python
import re

banned_terms = [
    r'осуществля',
    r'в рамках',
    r'данный',
    r'указанный'
]

text = "данный метод осуществлялся в рамках исследования"
matches = []
for pattern in banned_terms:
    found = re.findall(pattern, text, re.IGNORECASE)
    matches.extend(found)
```

### 3. Style Labeling
```python
LABELS = {
    'ru': {
        1: 'plain',      # простые слова
        2: 'literary',  # литературный
        3: 'technical'  # технический
    }
}

# Determine style by dominant pattern
style = LABELS[lang][1]  # default to plain
if banned_count > threshold:
    style = LABELS[lang][3]  # technical
elif literary_markers > threshold:
    style = LABELS[lang][2]  # literary
```

### 4. False Positive Audit
```bash
python3 tools/validate/style_fp_audit.py --samples 5
```

## Expected Outputs

### Style Markers Report
```json
{
  "lang": "ru",
  "corpus_size": 1250,
  "frequencies": {
    "данн": 240,
    "является": 26,
    "осуществля": 1,
    "в рамках": 4
  },
  "banned_terms": {
    "осуществля": 1,
    "в рамках": 4
  },
  "style": "plain",
  "recommendations": [
    "Replace 'данн' with 'данные' for consistency",
    "Avoid bureaucratic phrases like 'в рамках'"
  ]
}
```

### False Positive Audit
```json
{
  "sample_size": 5,
  "markers_found": 12,
  "false_positives": 2,
  "accuracy": 0.83,
  "issues": [
    {
      "chapter": "05-ru",
      "marker": "осуществля",
      "context": "метод осуществлялся",
      "verdict": "false_positive",
      "reason": "technical term in medical context"
    }
  ]
}
```

## Pitfalls
- **Corpus frequency drift**: Normalize text (collapse whitespace) before counting
- **Banned terms are regex**: Compile with re.IGNORECASE to catch inflected forms
- **Labels determine style**: plain=1, literary=2, technical=3; verify.py uses this for gating
- **False positive sampling**: Use random chapters; 10-15 chapters per subagent
- **Style markers are advisory**: Not gating unless explicitly configured
- **Language packages must be loaded**: Fall back to built-in if package is empty
- **Style audit is separate**: Style issues don't trigger major gates unless configured
