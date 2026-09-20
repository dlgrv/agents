# Docker Desktop VM on macOS: resources, restarts, virtiofs hazards

The VM layer under every container. Covers changing VM CPU/RAM safely, recovering when the VM
fails to come back up, and virtiofs bind-mount failure modes that masquerade as disk or app bugs.
For per-container and stack-level slimming see `resource-slimming.md`.

## Changing VM CPU/RAM

- Docker Desktop's VM defaults are conservative (~4 CPUs, ~half host RAM) — a tiny slice of an
  Apple Silicon host. For stacks with heavy in-container writers (ML inference, thumbnailing,
  transcoding) raise it; ~6 CPUs / 8 GB is a proven balance: more parallelism mostly buys I/O
  wait on virtiofs, not throughput.
- Settings file: `~/Library/Group Containers/group.com.docker/settings-store.json`. It is
  TCC-protected — an agent process may get `Operation not permitted`; if so, direct the user to
  Docker Desktop → Settings → Resources sliders instead of fighting the permission. Verify
  afterwards regardless of who applied it.
- Resource changes apply only on VM restart. Always verify with
  `docker info --format '{{.NCPU}} cpus / {{.MemTotal}} bytes'` — old numbers mean the VM never
  restarted, not that the edit failed.

## VM does not come back after a restart ("no route to host")

Symptoms: every container call fails with `no route to host` / `Cannot connect`; the backend log
pings a stale 192.168.65.x IP; `pgrep -fl com.docker.virtualization` finds nothing;
`Data/log/vm/console.log` mtime is minutes stale. The backend can sit in this state for half an
hour — do not wait it out. Bounce Docker Desktop fully:

```bash
osascript -e 'quit app "Docker"'; sleep 12; pkill -f com.docker.backend 2>/dev/null; sleep 5; open -a Docker
```

Wait 60–90 s, then verify BOTH `pgrep -l com.docker.virt` returns a process AND `docker info`
answers. `restart: unless-stopped` containers come back unattended — check `docker ps -a` before
starting anything by hand.

## virtiofs hazards on external-disk bind mounts

- **Bogus filesystem numbers.** `df` inside a container on a virtiofs mount reports garbage
  (absurd bsize → TiB-scale used/total on a small disk). Cross-check with `stat -f <path>` inside
  the container and host `df` before diagnosing a real disk problem. Apps that surface fs stats
  (e.g. the immich storage widget) will show the bogus numbers; a storage quota does NOT fix the
  display (known upstream issue) — don't burn time re-applying quotas.
- **Writes that reopen an existing file fail → 0-byte files at scale.** Docker Desktop's
  virtiofs (default container-data sharing) breaks on the SECOND open of an already existing
  file for write: the open returns ENOENT pointing at a directory that exists. Any in-place
  overwrite/update pattern — thumbnail regeneration, atomic write-then-replace, log rewrites —
  silently produces 0-byte files and crash-loops the writer. First writes to NEW files work
  fine, which is why the corruption looks like random flakiness instead of a filesystem bug.
- **Probe before blaming the disk:** in-container, `f=<mount>/.wtest; echo one > $f; echo two
  >> $f; cat $f` — two lines and non-zero size = write layer healthy; ENOENT / 0-byte = the
  virtiofs reopen bug. Run this BEFORE any disk-health work: a plain write test passes even
  when the reopen path is broken.
- **The fix is a sharing-implementation switch, not concurrency tuning.** Docker Desktop →
  Settings → General → Virtual Machine Options → "Choose file sharing implementation for your
  container data" → gRPC FUSE (needs a VM restart; the settings file is TCC-protected, see
  above, so the user usually flips this themselves — verify afterwards with the probe). After
  the switch: re-run the probe, regenerate the corrupt artifacts via the app's own re-queue
  job, and re-run dependent queues that failed on missing inputs.
- **If the host stays on virtiofs** (user's call), cap heavy job concurrency (~3) — parallelism
  amplifies the reopen bug into crash-loops. Treat this as damage control, not a fix. The
  switch can also change performance feel for bind-mount-heavy dev (HMR) workloads; re-verify
  the primary workload after switching.
- **Disk-health checks.** SMART is usually unavailable through USB bridges — don't chase
  `smartctl`. Instead scan the system log for I/O errors on the device and run a write test
  (`dd if=/dev/zero of=<mount>/.wtest bs=64k count=4; sync`) inside the container — then follow
  with the reopen probe above, because a first-write dd test passes even on the broken sharing
  layer. No I/O errors plus a clean probe = disk is fine; the corruption is the sharing layer,
  not the disk → try a full Docker bounce (above) first, and if the probe still fails with
  ENOENT, switch to gRPC FUSE (above) — a bounce alone does not cure the reopen bug.

## Controlling a heavy writer's job queue over its API (immich as the case)

- Auth: `x-api-key` header on every call.
- Queue control: `GET /api/jobs` lists all queues; `PUT /api/jobs/<name>` with
  `{"command":"pause"|"resume"}`. Sample `jobCounts.waiting` twice ~90 s apart → per-minute
  rate → ETA for the remaining backlog.
- Per-job concurrency: `GET /api/system-config` → `job.<jobName>.concurrency`, then PUT the whole
  config object back (thumbnailGeneration defaults to 1 — usually the bottleneck).
- Before and after load changes verify the writer isn't crash-looping:
  `docker inspect <server> --format '{{.RestartCount}} {{.State.StartedAt}}'`.
- A paused queue rejects start commands: `PUT /api/jobs/<name>` with `start` (even `force`)
  returns 400 while the queue is paused — send `resume` first, then start.
- After repairing inputs (e.g. regenerating thumbnails), re-run the dependent queues that
  failed on the missing files (faceDetection, smartSearch, ocr) — resume + start with force,
  then watch RestartCount. The definitive artifact-health metric is a zero-size scan inside
  the container (`find /data/thumbs -type f -size 0 | wc -l`); jobCounts shows queue state,
  not file health — a drained queue with zero-size files still means broken output.
- `failed` counters are historical, not live health: they persist in the queue until each job
  is re-run, so "N failed" long after the underlying cause is fixed means "not retried yet",
  not "still broken". Re-run with `PUT /api/jobs/<name>` `{"command":"start","force":true}` —
  once the write layer is fixed, previously-failed jobs pass immediately. Note that force on
  thumbnailGeneration re-sweeps EVERY asset missing artifacts (can re-enqueue thousands of
  jobs), not just the failed handful — that full sweep is usually the desired repair.
- After any repair, verify SERVER-side before chasing UI reports: sample preview/thumbnail
  URLs directly (curl + `x-api-key`, expect 200 + non-trivial body) across the library range,
  plus the zero-size scan. If everything answers healthy but the user still sees "Error
  loading image", the browser has cached the old zero-byte responses — a hard refresh may not
  evict them; have the user clear the cache (Ctrl+Shift+Del → cached images) instead of
  digging further server-side.
- "Server Offline" in the UI during heavy background job load is usually the API process
  saturating, not a crash: check `docker inspect` RestartCount/health and recent logs before
  restarting anything — it typically recovers on its own, and restarting mid-write adds churn.
