# gh CLI gotchas (observed, cost real failed attempts)

## `gh repo edit --visibility` requires an explicit consequences flag
On `gh` ≥ 2.94, changing a repo's visibility fails with a wall of usage text and:
```
use of --visibility flag requires --accept-visibility-change-consequences flag
```
**Fix:** add `--accept-visibility-change-consequences` to the command.

## Bulk repo edits: the naive loop silently no-ops
A pattern like
```bash
gh repo list dlgrv --json name,visibility --jq '.[] | select(.visibility=="public") | .name' | while read repo; do ...; done
```
returned 0 lines and did nothing — because `--json` exposes the `visibility` field in
**UPPERCASE** (`"PUBLIC"` / `"PRIVATE"`), not lowercase. The `select(.visibility=="public")`
filter matched nothing.
**Fix:** filter on `.visibility=="PUBLIC"` (uppercase). Also: `gh` may interleave
stderr warnings into stdout; capture stdout only: `json=$(gh ... 2>/dev/null)`.

## `mapfile` is unavailable
`mapfile`/`readarray` are bash-4 features; macOS ships bash 3.2, so `mapfile: command not found`.
**Fix:** use `while read` loops or process substitution into a temp file.

## `gh api user` does not expose private-contributions write
`gh api user --jq '.private_contributions'` returns `null` and cannot be written via token.
The "Include private contributions on my profile" toggle is **web-only**
(Settings → Profile). Do not try to flip it via API.

## Repo name cannot start with a dot
GitHub rejects repository names beginning with `.` (e.g. `.agents`). Use `agents`,
`agent-skills`, or `dot-agents` instead. A local dir named `~/.agents` still works fine;
only the *remote repo name* is restricted.
