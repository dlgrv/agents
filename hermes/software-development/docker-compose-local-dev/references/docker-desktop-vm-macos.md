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
- **Parallel writes can corrupt.** Many concurrent writers against a virtiofs-mounted external
  disk can produce thousands of 0-byte files and crash-loop the writer process. Cap heavy job
  concurrency (~3) even when CPUs are plentiful.
- **Disk-health checks.** SMART is usually unavailable through USB bridges — don't chase
  `smartctl`. Instead scan the system log for I/O errors on the device and run a write test
  (`dd if=/dev/zero of=<mount>/.wtest bs=64k count=4; sync`) inside the container. No I/O errors
  plus a clean write = disk is fine; the corruption is VM/mount state → full Docker bounce
  (above), then re-run the job/artifact regeneration and verify new writes are non-zero.

## Controlling a heavy writer's job queue over its API (immich as the case)

- Auth: `x-api-key` header on every call.
- Queue control: `GET /api/jobs` lists all queues; `PUT /api/jobs/<name>` with
  `{"command":"pause"|"resume"}`. Sample `jobCounts.waiting` twice ~90 s apart → per-minute
  rate → ETA for the remaining backlog.
- Per-job concurrency: `GET /api/system-config` → `job.<jobName>.concurrency`, then PUT the whole
  config object back (thumbnailGeneration defaults to 1 — usually the bottleneck).
- Before and after load changes verify the writer isn't crash-looping:
  `docker inspect <server> --format '{{.RestartCount}} {{.State.StartedAt}}'`.
