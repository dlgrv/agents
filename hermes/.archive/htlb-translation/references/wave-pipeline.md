# Wave Pipeline Tool

## Overview

The wave pipeline tool (`tools/wave_pipeline.py`) provides automated validation for complete translation waves across multiple languages.

## Usage

```bash
# Validate a single chapter (for testing)
python3 tools/wave_pipeline.py 13

# Validate multiple chapters in a wave
python3 tools/wave_pipeline.py 02 05 06 23 04 12 31
```

## Workflow

For each specified chapter and language:

1. **Assembly**: Run language-specific assemble script (assemble.py, assemble_en.py, assemble_es.py)
2. **Verification**: Run verify.py with language flag
3. **Output**: Print status table with OK/FAIL indicators
4. **Summary**: Print overall verdict (GREEN if all pass)

## Output Format

```
ru ch13: OK: headings=41 tags=41 sources=41 numbers=494 (lost=0, extraneous=0)
es ch13: OK: headings=41 tags=41 sources=41 numbers=494 (lost=0, extraneous=0)
en ch13: OK: headings=41 tags=41 sources=41 numbers=494 (lost=0, extraneous=0)
---
VERDICT: GREEN
```

## Integration with Translation Waves

- **After each wave**: Run pipeline to validate all chapters in the wave
- **Before publication**: Ensure all chapters pass verification
- **Error handling**: Pipeline identifies specific failures for targeted fixes

## Implementation Details

- Scripts called: `tools/assemble_<lang>.py`, `tools/verify.py`
- Output files: `book/<lang>/<chapter>-<title>.md`
- Exit codes: 0 = GREEN, 1 = any failures

## References

- [Wave planning](./wave-planning.md)
- [Pilot wave protocol](./pilot-wave-protocol.md)
- [Field markers reference](./field-markers.md)
