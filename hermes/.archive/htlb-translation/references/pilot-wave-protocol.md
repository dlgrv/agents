# Pilot Wave Protocol for Multi-Language Translation

## Overview

The pilot wave protocol ensures translation pipeline integrity before mass translation by testing all components across multiple languages simultaneously.

## When to Use

- New language extension (e.g., Spanish translation)
- Major upstream content deltas requiring retranslation
- Quality gate validation across languages
- Pipeline component testing (digest, assemble, verify, web UI)

## Pilot Wave Structure

### 1. Chapter Selection

- **Chapter 01**: Smallest chapter (36 units) — tests basic pipeline
- **Chapter 13**: Largest chapter (41 units) — tests scale and performance
- **Chapter 33**: New chapter (20 units) — tests fresh content handling

### 2. Language Coverage

For each new language, include all three chapters:
- Russian (existing baseline)
- English (existing baseline) 
- Spanish (new language)

### 3. Task Contract

Each subagent receives:
```json
{
  "field_labels": {
    "ru": ["- Стоимость:", "- Простыми словами:", "- Эффект:", "- Уровень доказательности:", "- Примечания:"],
    "en": ["- Cost:", "- In plain terms:", "- Benefit:", "- Evidence grade:", "- Notes:"],
    "es": ["- Costo:", "- En términos sencillos:", "- Beneficio:", "- Nivel de evidencia:", "- Notas:"]
  },
  "number_format": {
    "ru": "space thousands, no comma",
    "en": "comma thousands, no space", 
    "es": "space thousands, comma decimal"
  },
  "unit_files": ["/path/to/00.md", "/path/to/01.md", ...],
  "chapter_intro_format": {
    "status_line": "> Unofficial translation of ...",
    "back_link": "[← Volver al índice](../../README.md)",
    "heading": "# N. Chapter Title"
  },
  "glossary": "pre-translated terms for ch33",
  "contract": "first tool call = write_file, no analysis, no JSON reports"
}
```

### 4. Critical Success Rules

- **Write-first contract**: First tool call must be write_file, no reading other units
- **No batch analysis**: Subagents must not read all units first (causes timeout)
- **Immediate output**: Each unit translation results in immediate file write
- **No JSON reports**: Work = recorded files only, no summaries

### 5. Quality Gates After Pilot

After pilot wave completion:

1. **Assembly validation**: Run assemble.py ×9 to inject sources and validate structure
2. **Verification gates**: Run verify.py ×9 to check byte-identity, field markers, Chinese leaks
3. **Web UI test**: Verify capitalization and field parsing in index.html
4. **Cross-language consistency**: Check field usage and number formatting across languages

### 6. Wave Planning

- **Success criteria**: All 9 subagents complete without timeout or analysis paralysis
- **Next step**: If pilot succeeds, group remaining chapters by unit count (5 chapters per wave)
- **Failure recovery**: If subagents stall, restart with stricter write-first instructions

## Pitfalls

- **Analysis paralysis**: Subagents reading all units first → timeout before any writes
- **Timeout detection**: Transcript shows many `read_file` calls but 0 `write_file` calls
- **Contract violation**: Subagents returning JSON reports instead of writing files
- **Format drift**: Different field label usage across languages breaking web parser
- **Number format inconsistency**: Different number formatting causing verify.py failures

## Detection and Recovery

### Detection Methods

- **Transcript monitoring**: Look for patterns with >10 read_file calls and 0 write_file calls
- **File timestamp checks**: Last write >15 minutes ago indicates stalling
- **Cron watchdog**: Alerts on stalled chapters (40+ minutes without writes)

### Recovery Protocol

1. **Reset pristine units**: Restore from digest source
2. **Restart with HARD PROCESS RULE**: First tool call = write_file
3. **Steer stalled subagents**: "STOP READING. Write files first."
4. **Prevent recurrence**: Enforce write-first contract in all future tasks

## Quality Assurance

### Assembly Validation
```bash
# For each language and chapter
python3 tools/assemble.py /root/htlb-run-<lang>/<chapter>
python3 tools/verify.py <chapter> --lang <lang>
```

### Web UI Testing
```bash
# Test field parsing and capitalization
python3 -c "import re; md=open('book/<lang>/out-<chapter>.md').read(); print(len(re.findall(r'- (?:成本|Стоимость|Costo|Cost)[：:](.*)', md)))"
```

### Cross-Language Consistency
- Verify field labels match expected patterns per language
- Check number formatting consistency (spaces vs commas)
- Ensure no Chinese characters in visible text (regex scan)

## References

- [Field markers reference](./field-markers.md)
- [Web UI capitalization](./web-ui-capitalization.md)
- [Subagent timeout recovery](./subagent-timeout-recovery.md)
- [Spanish translation specifics](./spanish-translation-specifics.md)
