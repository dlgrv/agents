---
name: hermes-agent-contributing
description: "Use when contributing to NousResearch/hermes-agent upstream."
version: 1.0.0
author: dlgrv
license: MIT
metadata:
  hermes:
    tags: [hermes-agent, open-source, contribution, desktop, debugging]
---

# Contributing to Hermes Agent (NousResearch/hermes-agent)

Working setup and durable knowledge for the user's ongoing contributions.
User is a first-time OSS contributor here; prefers small first PRs, issue-first for
behavior changes, fork→branch→PR→review.

## Local setup

- Clone lives at `~/github/hermes-agent` (see dir convention: `~/github/` = OSS forks,
  `~/aezly/` = personal).
- Remotes: `origin` = `dlgrv/hermes-agent` (push PR branches here), `upstream` =
  `NousResearch/hermes-agent` (fetch updates). `gh repo clone dlgrv/hermes-agent`
  wires both automatically after `gh repo fork`.
- **gh quirk:** `gh repo fork <repo> --clone` can print help text instead of cloning —
  run plain `gh repo fork <repo>` first, then `gh repo clone <you>/<repo>`.
- Full clone ≈ 937M. Tests run via `scripts/run_tests.sh` (CI-parity wrapper, no xdist).

## Architecture constraint (user hard rule, 2026-08-27)

Refactors **must not break the project's existing architecture**. Before
extracting/rewriting anything in the hermes-agent repo, read the root and
subdirectory `AGENTS.md` files (they get auto-attached when patching files
under their directories — actually read them, don't skim). The rubric
explicitly *wants* god-file refactors into module-per-concern layout, and
desktop code follows `tools/act.mjs` / `tools/flows.mjs` style (deps
injected, entry point stays thin wiring) — follow the established pattern
rather than inventing a new one. Static source-assertion tests (e.g. the
P1-2 "no fs.writeFileSync in screenshot path" grep over server.mjs) must be
updated when the code they assert on moves to a new module.

## Review rubric digest (from root AGENTS.md)

What merges: well-reproduced `fix(...)` for real symptoms (fix the whole bug class),
desktop/TUI feature growth, god-file refactors, edge capability.
What gets rejected: speculative hooks without consumers, new `HERMES_*` env vars for
non-secrets (use config.yaml), new core tools when terminal/file/skill suffice,
change-detector tests, cache-breaking mid-conversation changes, telemetry without opt-in.
Invariants: prompt caching is sacred; strict message role alternation;
`get_hermes_home()` for all paths; secrets only in `.env`.
Behavior changes (e.g. adding a confirm dialog) go through an issue FIRST.

## Debug tooling inventory (desktop) — use before writing new probes

- CDP dev port `127.0.0.1:9222` opens on any dev-server run (closed in packaged builds;
  never relaunch the user's app — spawn an isolated instance instead).
- `apps/desktop/scripts/perf/lib/cdp.mjs` — client with `CDP.connect({port, match})`,
  promise-aware eval, centralized stable `SELECTORS`.
- `scripts/eval.mjs` one-liners; ~20 `scripts/diag-*.mjs` scenario scripts (JSON out).
- `src/debug/` — `__RENDER_COUNTS__` / `__ATOM_CHURN__` render attribution.
- For DOM/CSS inspection workflow see the separate skill
  `inspecting-hermes-desktop-dom` (do not duplicate it here).

## In-flight: Desktop Debug MCP server

Proposal filed as issue #95489 on NousResearch/hermes-agent (placement question:
`apps/desktop/mcp/` vs standalone; build locally regardless). Full staged plan +
tool surface + safety rails: `~/.hermes/plans/2026-08-26_134500-desktop-debug-mcp.md`.
Verified isolated-instance launch recipe (with `HERMES_HOME` isolation + port
mismatch notes): `references/isolated-instance.md`.

## Chat bug backlog — RE-VERIFY before acting

⚠️ **This backlog was reconstructed from a compacted summary and several items
did NOT hold up against `upstream/main` (verified 2026-08-26).** Trust the live
repo, not this list. Re-grep/read the files before touching any of them.

- **Item "1 empty catch in `user-edit-composer.tsx:647`" is FALSE on
  `upstream/main`.** That file/path does not exist as named; the edit action
  lives in `apps/desktop/src/app/chat/session-tile-actions.ts` (~576,
  `editMessage` useCallback) and it **already** catches and calls
  `notifyError(err, copy.editFailed)` with a state rollback — no silent swallow.
  Do NOT chase this ghost.
- The **inline edit-composer UI itself lives inside the external `assistant-ui`
  `Thread` component**, not in `apps/desktop`. A blur-cancel race there is NOT
  fixable in this repo (would need an upstream assistant-ui fix or a wrapper).
  Confirm which layer a reported race is in before scoping a fix.
- **Reproduce first, don't assume.** Use the Debug MCP server
  (`hermes-desktop-ui-debugging`) against an isolated instance to confirm a
  race actually fires on `upstream/main` before writing a fix. The
  `ui_flow_edit` flow + `Input.insertText` typing (see that skill) is the
  verified repro path. A prior attempt to repro with `ui_type` using
  `dispatchKeyEvent type:'char'` produced an EMPTY composer and concluded
  "nothing happens" — that was the tool being broken, not the app.
- **What is plausibly still real** (unconfirmed, needs repro): model-switch
  layout jank (the `model_switch` row rendering), and race B (composer unmounts
  mid-flight while a submit latch pends). Confirm via repro before filing/PRing.

Behavior-change items (e.g. a confirm-before-rewind dialog) still need a
maintainer issue FIRST — that part of the original note stands.

Detailed audit (if it still exists) in `references/desktop-chat-edit-audit.md`
is likely also stale — treat as a starting hypothesis, not ground truth.

## Issue workflow (as of 2026-09-02)

- Filing reports: use the `github-issue-reports` skill (mechanism-first, dupes, sepia).
- As dlgrv: no triage rights — labels/assignees 403 (e.g. #101388 filed unlabeled).
- Open report #101388: desktop bare-`/` palette truncates at `_SLASH_COMPLETION_LIMIT=30`
  (server.py:15837), regression from 60f58249e5; overlaps-but-distinct from #101062
  (client-side hide). Until fixed: `/goal` etc. work typed/prefix (`/go`) but are
  invisible from a bare `/` in the desktop palette.
- GitHub raw API rate-limits occasionally (`gitmon refuses to schedule us`, HTTP 429) —
  sleep ~20s and retry once.

## Pitfalls

- **Isolated debug instance MUST set `HERMES_HOME` to a throwaway dir.** It is NOT
  enough to pass `HERMES_DESKTOP_USER_DATA_DIR` (that is only the Chromium profile).
  `HERMES_HOME` is the data dir: `config.yaml`, provider API keys, and the whole
  chat DB (`state.db`). If omitted, the instance falls back to `~/.hermes` — the
  user's REAL install — and **writes test messages into their real session history**
  (and bills their real LLM keys). Always launch with `HERMES_HOME=/tmp/<something>`.
  Full recipe + contamination cleanup in the `hermes-desktop-ui-debugging` skill.
- Editing `editMessage`/rewind semantics is MINEFIELD territory: guarded by tests
  referencing #82462, #83855, #86623, #49903. Never "simplify" the degrade-to-
  plain-resubmit logic; extend tests first.
- `editMessage` is rewind+resubmit, NOT text replacement — an edit rewrites history
  server-side via truncation addresses (ordinal/rowId); stale targets retry once
  against refreshed history.
- The edit composer routinely unmounts mid-flight (authors say so themselves);
  every timer/callback added there must clean up on unmount.
