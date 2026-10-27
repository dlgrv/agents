# Watchdog script for HowToLiveBetter English translation

Monitors delegation logs every 3 minutes and alerts if any subagent stalls.

## Configuration

Set LOGS dict with delegation IDs and chapter numbers to monitor.
Set RUN to the units directory pattern.
Set DIG to the original digest units for comparison.

## Usage

```bash
# Run manually
python3 /root/.hermes/scripts/htlb-en-watchdog.py

# Add to cron (every 3 minutes)
*/3 * * * * /root/.hermes/scripts/htlb-en-watchdog.py
```

## State persistence

Completion status stored in STATE file. Only alerts on chapters not yet complete.
