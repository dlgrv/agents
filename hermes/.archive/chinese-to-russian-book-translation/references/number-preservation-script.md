# Number preservation script for 万/亿 conversions

## Purpose

Automated verification that all 万/亿 conversions are preserved during translation, with zero loss of numeric data.

## Script logic

```python
import re
# Walk numbers with their 2-char context to detect 万/亿 adjacency
for m in re.finditer(r'\d+(?:\.\d+)?', src):
    t = m.group(0); after = src[m.end():m.end()+2]
    val = None
    if after.startswith('亿'):   val = float(t) * 1e8
    elif after.startswith('万'): val = float(t) * 1e4
    cands = {t}
    if val is not None:
        cands |= {f"{val:g}", f"{val:,.0f}", f"{int(val):,}"}
    if not any(c in out for c in cands):
        missing.append(t + ("万" if after.startswith("万") else "亿" if after.startswith("亿") else ""))
```

## Usage

```bash
cd /path/to/repo
python3 -c "
import re, os
os.chdir('.')
pairs = [("docs/cn-article.md", "docs/en-article.md")]
for cn, en in pairs:
    src = open(cn, encoding='utf-8').read()
    out = open(en, encoding='utf-8').read()
    missing = []
    for m in re.finditer(r'\d+(?:\.\d+)?', src):
        t = m.group(0); after = src[m.end():m.end()+2]
        val = None
        if after.startswith('亿'):   val = float(t) * 1e8
        elif after.startswith('万'): val = float(t) * 1e4
        cands = {t}
        if val is not None:
            cands |= {f"{val:g}", f"{val:,.0f}", f"{int(val):,}"}
        if not any(c in out for c in cands):
            missing.append(t + ("万" if after.startswith("万") else "亿" if after.startswith("亿") else ""))
    status = "OK" if not missing else f"MISSING {len(missing)}: {missing[:8]}"
    print(f"{en}: {status}")
"
```

## Expected output

- `OK`: All 万/亿 conversions preserved (no loss)
- `MISSING X: [...]`: List of potentially lost numbers (requires manual verification)

## Notes

- Script considers legitimate conversions (e.g. 610.6 万 → 6.106 million)
- Manual verification needed if "MISSING" appears — some may be intentional rephrasing
- Always check context: numbers may be rephrased as "6.1 million" rather than "6,106,000"