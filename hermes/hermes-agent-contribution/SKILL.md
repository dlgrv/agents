---
name: hermes-agent-contribution
description: "Contribute PRs to NousResearch/hermes-agent via your fork."
version: 1.0.0
author: dlgrv
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [github, contribution, pr, fork, issue, nousresearch, hermes-agent]
    related_skills: [github-pr-workflow]
---

# Contributing to NousResearch/hermes-agent

External-contributor (no write access) workflow for the Hermes Agent repo.
Pair with the repo's `CONTRIBUTING.md` (branch naming `fix/` `feat/` `docs/`;
Conventional Commits; "keep PRs focused — one logical change per PR").

## When to use

- You're about to file an issue or open a PR against
  `NousResearch/hermes-agent` and you don't have push access (you're `dlgrv`).
- You need to decide: file an issue directly (no fork) vs open a PR (needs the
  fork) — and how to keep tooling and bugfix work in separate PRs.
- A fork got deleted and its PR closed; you need to recover/merge the code.
- You're hitting `gh` quirks around `delete_repo` scope or issue/PR JSON fields.

## Issue vs PR — different rules, different transport

- **Issue** = created **directly in upstream** `NousResearch/hermes-agent`.
  No fork needed. Any logged-in GitHub user can file one. (We created #95489
  and #95798 this way — no fork involved.)
- **PR** = needs the branch to live *somewhere GitHub can see*. Without
  write access you push to **your fork** `dlgrv/hermes-agent` and open
  `dlgrv:<branch> → NousResearch:main`. (Maintainers / people with push access
  skip the fork and push the branch straight into upstream.)

Mental model: issue is a note on the wall (write on the wall); PR is "merge
THIS branch" (the branch must exist in a repo you can push to).

## Keep the fork — it is permanent

`dlgrv/hermes-agent` is the standing base for **all** future PRs. Do NOT delete
it between contributions (a past session deleted it pre-merge, then had to
recreate it and reopen the PR). Only delete when you truly abandon the account.
Multiple PRs share one fork via different branches.

## Opening a PR (cross-repo)

```bash
# 1. fork once (or recreate if deleted)
gh repo fork NousResearch/hermes-agent --clone=false
# 2. branch off fresh upstream/main, do work, then push to the FORK
git fetch upstream main
git checkout -b feat/my-thing upstream/main
# ... commit ...
git push -u origin feat/my-thing        # origin = dlgrv fork
# 3. open PR into upstream
gh pr create --repo NousResearch/hermes-agent \
  --repo NousResearch/hermes-agent \
  --head dlgrv:feat/my-thing --base main \
  --title "feat(scope): ..." --body-file /tmp/pr-body.md
```

Body should reference the issue (`Closes #NNNN` auto-closes it on merge;
`Related to #NNNN` if not closing). The `closedByPullRequestsReferences`
field on the issue stays empty until merge — that's normal; the link shows in
the issue's Development sidebar.

## Split tooling from bugfix (user's firm rule)

One issue/PR for the *tool* (e.g. Debug MCP server #95489 → PR #95781), a
**separate** issue/PR for the *product fix* (e.g. chat-edit races → issue
#95798). Mixing them makes maintainers hesitate and bloats a single review.
`CONTRIBUTING.md` explicitly wants "one logical change per PR".

## Recovering a deleted fork / closed PR

Deleting the fork **auto-closes** its open PRs (GitHub drops the head repo),
but the PR diff stays visible in GitHub's DB and the issue link still resolves.
To make the code mergeable again, the branch must exist somewhere:
- **Local backup branch** is the source of truth: `git branch
  backup/<name> <branch>` before risky ops, then re-push from it.
- **Public gist** of the diff as a last-resort mirror:
  `git diff upstream/main...<branch> > p.patch && gh gist create p.patch --public`.
  Comment the gist URL on the issue so the code is visible regardless of fork
  state. (raw `curl .../raw` may return 0 lines — use the web/API, not raw curl.)

Closing a PR does NOT delete the code; reopening or re-creating from the local
branch restores it.

## Responding to a P1 / security review (reusable pattern)

When a reviewer returns P1 blockers (not nits), the issue is usually the
*design boundary*, not a typo. For PR #95781 the blockers were: (1) the
isolation guard trusted a caller-supplied coordinate instead of proving the
realized target, and (2) `ui_screenshot` wrote arbitrary files. The fix path
that lands:

1. Write a **plan** (`/plan`) with bite-sized TDD tasks before touching code.
2. For each blocker, add **deterministic negative tests first** (e.g. "declared
   sandbox but target proves real home → REFUSED"), watch them fail, then
   implement the fix, watch them pass.
3. Extract security-critical logic into a small pure module (`guard.mjs`) so it
   is unit-testable without spinning Electron.
4. Reply on the PR mapping each P1 → exact fix + test. Be explicit about any
   residual risk the reviewer should accept (e.g. "CDP-attached attacker can
   overwrite the renderer descriptor; accepted for the dev-only threat model").
5. Do NOT silently convert an open `needs-decision` placement question (#95489)
   into architecture by merging — state that the PR leaves placement open.

Check issue/PR state with `gh` JSON, not the browser: `gh issue view NNNNN -R
NousResearch/hermes-agent --json state,comments` and `gh pr view NNNNN -R
NousResearch/hermes-agent --json state,reviews,comments`. A stale browser tab
can show a closed PR as OPEN (cache) — trust the API.



- Deleting a repo via `gh` needs the **`delete_repo`** OAuth scope, which the
  default token lacks (`gist, read:org, repo, workflow`). `gh auth refresh -h
  github.com -s delete_repo` hangs in non-interactive shells (waits on a
  browser prompt that never fires) — delete forks via the **web UI**
  (repo Settings → Delete) instead. Preferred: don't delete at all.
- `gh search prs --state` accepts only `open|closed`, not `all`.
- `gh issue view` JSON fields: use `closedByPullRequestsReferences` (not
  `timelineItems`, which is invalid there).

## Multi-round review cycles + landing readiness

A big PR goes through several review rounds keyed to the **exact head SHA**.
Pattern that converged to "source review closed" (detailed case study:
`references/pr-95781-review-cycles.md`):

- **Self-audit pass between rounds:** re-read your own merged-to-branch code
  fresh (dispatch/lifecycle boundaries are where bugs hide) and hunt real
  defects — e.g. a typed MCP image result silently JSON-stringified into a
  text blob by the wrap layer; a cached CDP handle never invalidated on
  socket close; `JSON.stringify(undefined)` → TypeError in a bounds helper.
  Fix each RED-first; post a numbered mapping comment (defect → commit →
  test). Reviewers credit this and it pre-empts their next round.
- **Reviewers re-check the exact head against live `main` every round.**
  Before pushing, rebase onto fresh `upstream/main`. After rebase, prove no
  content drift with `git range-diff <old-base>..<old-head> upstream/main..<head>`
  — every line must read `N: <old> = N: <new>` — and re-run the full suite.
- **Hosted acceptance jobs (CI/Docker/Nix) sit in `action_required` until a
  maintainer authorizes them**, and stay keyed to the head SHA at the time.
  Local green runs do NOT transfer ("I am not transferring local receipts").
  Post-rebase, comment the new head SHA + verification summary so the gate
  re-runs against the current tree. Don't ping about the approval — the
  reviewer records the gate in every disposition; noise costs goodwill.
- **"Source review closed; remaining release authority is hosted
  execution"** means: no more code changes are wanted. Don't invent extra
  work; leave the repo on a rebased, fully-tested head and wait.
- **Attributing a test failure on the new base:** before calling a failure a
  rebase regression, run the same test on the previously-reviewed head. If
  it fails there too, it's a pre-existing environment flake (e.g. exit 127 =
  command-not-found in `/bin/sh`) — note it in the PR comment rather than
  "fixing" it, and never block a rebase push on it.
- Extraction pattern reviewers reward: pull security/lifecycle logic out of
  the god-file into small pure modules (`guard.mjs`, `dispatch.mjs`,
  `cdp-client.mjs`, `tools/read.mjs`) with injected deps so each is
  unit-testable without Electron. `AGENTS.md` explicitly wants god-file
  refactors; name the rubric in the commit/comment.

## See also

- `hermes-desktop-ui-debugging` — the Debug MCP server (#95489) is the tooling
  half; this skill is the contribution half.
- `github-pr-workflow` — generic PR lifecycle if you need more.
