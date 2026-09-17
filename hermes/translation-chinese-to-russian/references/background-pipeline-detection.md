# Background Pipeline Interference Detection Script

## Purpose
Detect and resolve conflicts between background translation pipelines and current translation work.

## Detection

```bash
# Check for running hermes -z processes (background pipeline)
ps aux | grep 'hermes -z' | grep -v grep | wc -l

# Check pipeline logs for recent activity
tail -20 ~/github/htlb-pipeline/pipeline.log | grep -E '(START|HERMES-FAIL|chapter)' | tail -5

# Check if background processes are using outdated prompts
ps aux | grep 'hermes -z' | grep -v grep | head -1 | xargs cat | grep -E '(slug|README.ru|MQM)' || echo 'No current conventions found in background process'
```

## Resolution Options

### Option 1: Stop Background Pipeline

```bash
# If the pipeline is systemd-managed
sudo systemctl stop htlb-pipeline
sudo systemctl disable htlb-pipeline

# Or if running as script
pkill -f 'pipeline.sh'  # Careful: kills all matching processes
```

### Option 2: Let It Run, But Verify

If the background pipeline is running with outdated prompts:

```bash
# Let it finish, but verify its output against current standards
cd ~/github/htlb-ru
for chapter in $(ls book/ru/*.md | sed 's/.*\([0-9][0-9]-.*\)\.md/\1/' | sort -V); do
  echo "Verifying $chapter..."
  python3 htlb_verify.py book/$chapter.md book/ru/$chapter.md --normalize
done

# If verification fails, overwrite with correct version
git checkout HEAD -- book/ru/
```

### Option 3: Update Background Pipeline Prompt

If you control the pipeline script, update its prompt to include:
- Russian slug naming convention
- README.ru.md back-links
- MQM review rules
- Current TRANSLATION.md rules

## Prevention

Before starting new translation work:

```bash
# Check for background processes
if ps aux | grep -q 'hermes -z' | grep -v grep; then
  echo "WARNING: Background translation pipeline detected"
  echo "Current PID: $(ps aux | grep 'hermes -z' | grep -v grep | awk '{print $2}')"
  echo "Pipeline log: ~/root/github/htlb-pipeline/pipeline.log"
  echo "Decide: stop background work or proceed with verification"
fi
```

## Integration

Add this check to the beginning of the translation workflow:

```bash
# In translation workflow script
if [ -f "~/github/htlb-pipeline/pipeline.log" ] && tail -1 ~/github/htlb-pipeline/pipeline.log | grep -q 'START chapter'; then
  echo "Background pipeline active. Checking for conflicts..."
  # Run detection script
  # Decide whether to stop or verify
fi
```