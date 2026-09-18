# CJK False Positive Handling in QA

## Problem
QA tools incorrectly flag legitimate CJK characters in translated content as errors, causing false positives that waste time and undermine confidence in the pipeline.

## Root Cause
CJK characters (`\u4e00-\u9fff`) appear legitimately in:
1. **Source lines** (`- Sources:` or `- Источники:`)
2. **Legal/regulation titles** (e.g., 治安管理处罚法)
3. **Glosses** (e.g., 白户 — people with no credit history)
4. **Localized terms** (e.g., 跑分 — money laundering through payment accounts)

## Solution
Adjust QA regex patterns to exclude source lines when scanning for CJK characters in visible text.

### Implementation
```python
# Example QA filter for CJK in main content only
import re

def check_cjk_in_content(text):
    # Skip source lines and legal titles
    lines = text.split('\n')
    visible_lines = []
    for line in lines:
        if line.strip().startswith('- Sources:') or line.strip().startswith('- Источники:'):
            continue
        # Skip lines with Chinese law/regulation titles
        if re.search(r'[\u4e00-\u9fff]{2,}', line) and '法' in line:
            continue
        visible_lines.append(line)
    
    # Check CJK only in visible content
    visible_text = '\n'.join(visible_lines)
    cjk_matches = re.findall(r'[\u4e00-\u9fff]', visible_text)
    return len(cjk_matches) == 0
```

### Verification Steps
1. After QA, confirm that CJK characters in sources and legal terms are preserved
2. Only unintended CJK in main content should be flagged
3. Test with known false positive cases (document codes, glosses, localized terms)

## Examples of Legitimate CJK
- Document codes: 国食药监办〔2010〕432 号
- Legal terms: 治安管理处罚法, 刑法
- Glosses: 白户 (blank-slate), 跑分 (money laundering)
- Localized terms: 三不一多 (three don'ts and one more)

## Impact
- Eliminates false positive QA warnings
- Preserves legitimate CJK in sources and legal content
- Maintains strict CJK-free requirement for main content
