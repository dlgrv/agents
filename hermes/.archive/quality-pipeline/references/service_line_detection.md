# Service Line Detection Logic

## Purpose
Detect and filter service lines in Chinese text for grounding validation.

## Scope
- **Line-based detection**: Entire lines are service lines, not substrings
- **Marker detection**: Specific markers that indicate service content
- **Context preservation**: Non-service lines keep original formatting

## Detection Rules

### Service Line Start Markers
- 来源 (source)
- §SRC§ (source marker)
- 成本标签 (cost tag)
- 证据等级 (evidence level)
- <!-- (HTML comment)

### Detection Logic
```python
def is_service_line(line):
    line = line.strip()
    if line.startswith(('来源', '§SRC§', '成本标签', '证据等级')):
        return True
    if '<!--' in line:
        return True
    return False

def filter_service_lines(text):
    lines = text.split('\n')
    filtered = []
    for line in lines:
        if is_service_line(line):
            continue  # drop service line
        filtered.append(line)
    return '\n'.join(filtered)
```

## Pitfalls
- **Substring vs line**: Never check substrings within lines — service lines are entire lines that start with markers
- **Whitespace tolerance**: Strip whitespace before checking start markers, but preserve original line content
- **Comment markers**: <!-- can appear anywhere in line, not just start
- **Marker variants**: Use exact matches, not regex, for known service markers
- **Context preservation**: Non-service lines must keep original whitespace and formatting
- **Multi-line spans**: When a span touches multiple lines, check EVERY line for service markers
- **Ellipsis handling**: Service line detection applies to original line context, not span fragments
