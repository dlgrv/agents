# Server-run batch translation pipeline (survives local-machine shutdown)

Use when a book-scale translation must keep running while the local Mac is closed or shut down. The rule: the driver lives on the worker machine (the user's Hermes server); the Mac is used only to kick off the run and collect results. Driving per-chapter work with `a2a_call` from the Mac makes the Mac a required participant for the whole run — every call originates locally, so the run dies with the Mac.

## Components (all on the server)

1. **Repo worktree** with the `translation/<lang>` branch checked out; rules files (TRANSLATION.md, quality rubric) present in the worktree.
2. **Driver script** (`pipeline.sh`):
   - Loops over chapter files; per chapter: skip if the state file marks it done (log `skip NN (done)`); else log `START chapter NN (<file>, <N> items)`, run the worker, log `DONE chapter NN` on verified success or `HERMES-FAIL chapter NN rc=$?`.
   - Chapter list and per-chapter item counts come from grep on the originals, never from a remembered table.
   - Continues to the next chapter after a failure (one bad chapter must not stall the run); re-running the script is idempotent — done chapters are skipped.
3. **State file** — one chapter number per line, appended only after that chapter's verification passed.
4. **Append-only log** — timestamped START/DONE/FAIL lines; the only progress UI needed.

## Worker invocation (per chapter)

```bash
timeout 5400 hermes -z "<PROMPT>" --in <repo-dir> --yolo
```

- The ENTIRE prompt is ONE quoted argument; flags (`--in`, `--yolo`) come strictly after it. A split or mis-ordered prompt fails with `hermes: error: argument -z/--oneshot: expected one argument` (rc=2) in about a second — the driver will happily burn through every chapter producing instant failures.
- `timeout 5400` (90 min) — whole-chapter generation plus self-verification needs headroom.

### The prompt must be self-contained

The oneshot agent sees NOTHING but this prompt. Include, in this order:

1. Task + source path + item count + target path.
2. Rules file path ("follow exactly").
3. Quality bar in one paragraph: living target language, no calque, tone, heading style.
4. Byte-faithful zones (numbers, source/citation lines with label mapping, machine tags, DOIs/URLs), field order, status line, back-link with re-adjusted relative depth.
5. Build technique: assemble the file with a python script from the original's lines, copying tags/sources programmatically — excludes typos.
6. The verification checklist as concrete python assertions: heading count, tag-comment count, doi.org-line count vs original, byte-identity of source lines (label-stripped), zero source-language characters outside allowed zones — plus "if it fails, fix and re-verify".
7. The exact git add/commit command (repo's commit convention).
8. Reply contract: one line of JSON — `{"chapter":N,"items":N,"status":"done"}` or `{"chapter":N,"status":"failed","why":"..."}`.

## Launch and control

```bash
# start (or restart) as a systemd transient unit — survives SSH disconnect and Mac shutdown
ssh <server> 'systemctl reset-failed <unit> 2>/dev/null; systemctl stop <unit> 2>/dev/null; \
  systemd-run --unit=<unit> --collect /bin/bash <path>/pipeline.sh'

# progress check
ssh <server> 'systemctl is-active <unit>; grep -E "START|DONE|FAIL" <log> | tail; \
  ls <repo>/<out-dir>/ | wc -l'
```

- `systemd-run`, not `nohup ... &` over SSH: the unit outlives the SSH session cleanly and is visible to `systemctl`.
- Before re-launching, `systemctl stop` + `reset-failed` the same unit name, or systemd refuses with "already loaded".
- A hermes update warning in the output ("previous update pulled new code…") is cosmetic; judge progress by DONE lines and translated-file counts, not by warnings.

## Autonomous-server caveat

A `--yolo` server agent handed open-ended prep tasks will execute them to completion and may go further (translating chapters during "setup"). Either scope the task explicitly ("set up only; do not translate yet") or verify the unsolicited output with the same scripted checks and keep it.
