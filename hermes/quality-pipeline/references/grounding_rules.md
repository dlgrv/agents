# Grounding Validation Rules

## Purpose
Validate that spans (claims) are grounded in the source text after filtering service markers.

## Scope
- **CN text filtering**: Remove service lines and markers before validation
- **Span position checking**: Verify spans exist in filtered CN text
- **Service-line detection**: Spans sitting ON service lines are dropped

## Filtering Rules

### Service Lines to Remove
- Lines starting with: 来源, §SRC§, 成本标签, 证据等级
- Lines containing: <!-- (comment markers)
- **Positional rule**: Remove entire lines, not just markers

### Service Markers to Keep
- Text containing service markers but not starting with them (e.g., 出资来源 = source of funds)
- **Context detection**: Use line context, not substring matching

## Span Validation Protocol

### 1. Normalize CN Text
```python
collapsed_whitespace = re.sub(r'\s+', ' ', cn_text)
```

### 2. Filter Service Lines
```python
filtered_lines = []
for line in cn_text.split('\n'):
    if line.strip().startswith(('来源', '§SRC§', '成本标签', '证据等级')):
        continue  # drop service line
    if '<!--' in line:
        continue  # drop comment
    filtered_lines.append(line)
filtered_text = '\n'.join(filtered_lines)
```

### 3. Validate Span Positions
```python
for span in spans:
    # Check each fragment for ellipsis spans
    fragments = span['text'].replace('…', ' ').replace('...', ' ').replace('……', ' ').split()
    for i, fragment in enumerate(fragments):
        pos = span['start'] + (sum(len(f) for f in fragments[:i]) + i)  # approximate
        if fragment not in filtered_text[pos:pos+len(fragment)]:
            return False  # fragment not grounded
    return True  # all fragments grounded
```

## Pitfalls
- **Whitespace drift**: Collapse whitespace before position lookup, but use original line context for service-line rule
- **Multi-line spans**: Check EVERY line touched by span for service lines, not just first or last
- **Ellipsis spans**: Split into fragments; each fragment must ground in order (ellipsis spans as a whole are not expected to sit verbatim)
- **Conservative filtering**: Better to drop slightly too many spans than to hallucinate grounding
- **False positive catch**: Mutation controls catch overly aggressive filtering
- **Hardened claims**: Assertions with `hardened_claim=true` bypass grounding validation
- **Span supports claim**: Assertions with `span_supports_claim=false` are dropped immediately
- **Error handling**: Broken verdicts are gated as `error`, not silently dropped
