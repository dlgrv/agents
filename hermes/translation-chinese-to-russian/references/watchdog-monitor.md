# Progress Monitor and Stall Detector

Monitors translation subagent progress and detects stalled or missing work.

## Usage

```bash
python3 tools/watchdog.py /tmp/workdir --stall-min 25
```

- `/tmp/workdir`: Translation work directory with units/
- `--stall-min`: Minutes of inactivity before triggering stall (default 25)

## Exit Codes

- 0: Healthy (all units present, recent progress)
- 1: Stalled (no progress for 25+ minutes)
- 2: Incomplete (missing units)

## Monitoring Logic

- Checks expected vs actual unit count per chapter
- Tracks last modification time of unit files
- Reports chapters with no recent progress
- Detects missing units that stall the pipeline

## Key Features

- Cross-chapter validation using index.json
- Configurable stall threshold
- Clear output for debugging stalled agents
- Prevents infinite waits on dead subagents
