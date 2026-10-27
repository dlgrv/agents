# Subagent Timeout Recovery

## Timeout Pattern Recognition

- **Symptoms**: Transcript shows many `read_file` calls (≥10) but 0 `write_file` calls; file timestamps show no writes for >15 minutes; subagent status is 'running' but idle
- **Root cause**: Subagents get stuck in analysis/reading loops — they read all units first, then timeout before writing anything
- **Detection**: Watchdog script monitors for silence ≥6 min + reads-without-writes pattern; manual check via transcript tail and file mtime

## Recovery Procedure

1. **Kill stalled subagent** (delegate_task action=stop)
2. **Reset pristine units** from digest source:
   ```bash
   rm -rf /root/htlb-run-en/13/units
   cp -r /root/github/HowToLiveBetter/tools/digest/13/units /root/htlb-run-en/13/units
   ```
3. **Restart with HARD PROCESS RULE**:
   - Task prompt: "your FIRST tool call must be a write_file of the translated NN.md. You may NOT read any unit other than the one you are currently translating in this same step."
   - Enforce: "One step = read unit NN.md → translate to English → translate to English → write_file the SAME path with the translation → next unit"
   - No batch reading, no analysis, no planning — write immediately

## Prevention

- **Task prompt engineering**: Always include "do NOT re-read conventions or reference files — everything is in this task; start writing immediately"
- **First-tool-call rule**: Explicitly require first tool call to be `write_file` of the translated unit
- **Watchdog integration**: Use 3-minute interval cron that alerts on reads-without-writes pattern
- **Unit size control**: Keep units under 2KB to prevent analysis overload

## Example Recovery Task Template

```
HARD PROCESS RULE (violated by previous runs): your FIRST tool call must be a write_file of the translated 00.md. You may NOT read any unit other than the one you are currently translating in this same step. One step = read unit NN.md → translate to English → write_file the SAME path with the translation → next unit.

LOOP (repeat N times): read /root/htlb-run-en/13/units/NN.md → translate to English → write_file the SAME path with the translation → next unit.

CONVENTIONS (inline, complete — no other reference needed):
- Field labels: 成本→`- Cost:`, 说人话→`- In plain terms:`, etc.
- Numbers byte-for-byte; 万 → numeric conversion
- China-specific terms: transliteration + gloss on first use
- No invented facts; restrained tone; item titles start with verb
- "In plain terms" = natural spoken English, no new numbers
- Write each translated file immediately (overwrite in place)

After writing all files, reply with: 'done ch13, files written: N'
```