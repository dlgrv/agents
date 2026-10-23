---
name: lowbid-git-workflow
description: "Git branch/commit/PR conventions for the lowbid (krutilka) repo — issue-scoped naming, and a hard gate: never branch/commit/PR unless the developer explicitly asks."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, lowbid, krutilka, conventions]
    related_skills: [github-pr-workflow, github-auth]
---

# lowbid (krutilka) Git Workflow

Project-specific git conventions for the **lowbid** repos — `sfsef/krutilka` (local `~/aezly/krutilka`) and the SSP repo **`ortblabs/ssp`** (private; org is `ortblabs` — WITH the trailing s, easy to typo; local `~/aezly/lowbid-ssp`). Go module path is `github.com/ortblab/ssp` (historic, no s) — do NOT 'fix' it to match the org: module path ≠ repo URL, renaming it churns every import for zero value. Repo PLACEMENT rule: `sfsef` is a personal account, not an organization — product repos go under the **`ortblabs`** org with neutral names.

## Branding visibility matrix (user-settled — don't re-litigate)
- **Repo names + repo content (README, docs, env/cookies, UI strings): no `lowbid` codename, no `ortblabs` org name.** Before finishing any UI/text change, grep the built output (`frontend/dist/`, VAST XML, tracking URLs) for both — source being clean is not enough if a stale bundle deploys.
- The admin UI tab/login card title is **`Lowbid SSP`** — 'Lowbid' here is ALLOWED because the admin is staff-only behind auth; the org name is the one that never ships.
- **Public surfaces stay neutral:** VAST `AdSystem` = `ssp`, tracking paths generic (`/imp`, `/clk`), no branding in API responses — buyers/players see these.
- Favicon: emoji 📺 via inline SVG data-URI in `index.html` (SSP = video/CTV traffic); no image asset needed. The commit/branch prefix `lowbid-NN` stays — it's the task-tracking convention and lives only in git history. This is NOT the general `github-pr-workflow` skill — those git/gh mechanics still apply, this skill only fixes the naming/format rules and the permission gate specific to these repos.

> Code-side conventions for lowbid-ssp (structure, lint contour, test pyramid, delivery loop) live in the `programmatic-adtech` skill + the repo's `docs/CODE-STANDARD.md`; this file stays git-only.

## ⚠️ Hard gate — read first

**Never create a branch, commit, or PR in this repo unless the developer explicitly asks for it in the current turn.** Writing/patching files is fine on request; committing/branching/PR-ing is not implied just because files changed. If the user asks you to "implement X" without saying "commit"/"create a branch"/"open a PR", stop after the code changes and ask, or wait for an explicit follow-up instruction. This overrides any general assumption that finishing a task means shipping a commit.

## Issue number convention

`lowbid-<issue-number>` — the issue number from GitHub, no leading zeros (e.g. `lowbid-32`, `lowbid-9`).
If there is no related issue, use `lowbid-00`.

## 1. Branch naming

```
git checkout -b feat/lowbid-00-bid-sink-and-vast-cache
```

Format: `<type>/lowbid-<issue-or-00>-<short-kebab-description>`

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `ci` — same set as commit types below.

## 2. Commit message format

```
git commit -m 'chore(lowbid-00): remove TODO dir'
```

Format: `<type>(lowbid-<issue-or-00>): <short description>`

Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `ci`, `perf` (Conventional Commits, scoped to the issue number instead of a module name).

**Commit subjects and bodies are in ENGLISH** — the user set this as a repo-wide rule («у нас все коммиты должны быть на английском»); do not mirror the user's chat language into commit text. This is MECHANICALLY enforced: a pre-commit `commit-msg` hook (`scripts/hooks/check-commit-msg.sh`, identical copy in krutilka and lowbid-ssp) rejects any message containing Cyrillic. Detect via python3, not `grep -P` (BSD grep on macOS has no `-P`). Emergency bypass is `git commit --no-verify` — use only when the user explicitly asks.

**Sequential NN when there is no issue**: the effective practice is one shared sequence, not every no-issue commit staying at 00 — take the next number from history (`git log --oneline | grep -oE 'lowbid-[0-9]+' | sort -V | tail -1`) and bump it. When work spans stages/tasks in one wave, split into consecutive numbers (one clean commit each), staging explicit per-commit file lists — a tree carrying several stages' changes mixed in one file needs the file assigned to its dominant stage, not a combined commit. When one file genuinely carries two commits' changes (e.g. a constant change and an unrelated fix in the same module), stage per-hunk with `git add -p` instead of assigning the file wholly to one commit — file-level assignment mislabels one of the changes.

If there's an issue, add `Closes #<number>` in the commit body when the commit fully resolves it:

```bash
git commit -m "$(cat <<'EOF'
feat(lowbid-11): add parameter help tooltips on campaigns page

Closes #11
EOF
)"
```

## 3. Pull request

```bash
gh pr create --title "feat(lowbid-11): add parameter help tooltips on campaigns page" --body "Closes #11"
```

- PR title: same format as the commit message — `<type>(lowbid-<issue-or-00>): <description>`.
- PR body: `Closes #<number>` when applicable, otherwise a short summary.
- Use the mechanics (push, checks, merge, CI auto-fix loop) from the general `github-pr-workflow` skill — this skill only overrides naming/format and the permission gate.

## Full example

```bash
git checkout -b feat/lowbid-11-parameter-help-tooltips
# ... make changes ...
git add frontend/src/components/FieldLabel.tsx frontend/src/components/InfoTooltip.tsx
git commit -m "$(cat <<'EOF'
feat(lowbid-11): add parameter help tooltips on campaigns page

Closes #11
EOF
)"
git push -u origin HEAD
gh pr create --title "feat(lowbid-11): add parameter help tooltips on campaigns page" --body "Closes #11"
```

## Pre-merge gate (run before proposing a merge to main)

When the user asks "are tests green / can we merge":

1. Backend: full suite (`cd backend && uv run python -m pytest tests -q`) + the lint contour (black/flake8/ruff/import-linter, see repo docs).
2. Frontend: `npm run check` (prettier+tsc+eslint), unit tests, e2e Playwright with the stack up.
3. Triage e2e failures per the krutilka-local-dev flake rule (re-run failing specs in isolation before counting them as real) — report which failures are pre-existing flakes, with evidence, not a bare pass/fail number.
4. Conflict/ff check: `git rev-list --count HEAD..origin/main` (0 = fast-forward possible) and `git log --oneline <base>..HEAD --not origin/main` for how many of ours actually ship.
5. Working tree must be clean (`git status --short` minus untracked) before asking merge permission; then ask PR-vs-direct-push and deploy timing — the repo's history goes through PRs.

## Pitfalls

- **Never `git add -A` / `git add .` in this repo.** Untracked scratch and subagent WIP (shadcn scaffolding, half-written modules under backend/app) sits in the worktree between delegated waves; stage explicit paths only, then verify `git status --short` shows nothing unrelated before committing.
- Don't reuse generic branch names like `feat/add-user-authentication` (that's the general-skill example) — always include `lowbid-<n>`.
- Don't skip `lowbid-00` when there's no issue — an unscoped branch/commit breaks the convention's grep-ability.
- **Commits stay local until an explicit in-turn ask — and this now includes subagent/delegation cycles.** Before dispatching an implementation subagent, put the no-commit/no-push rule verbatim into its task context: a delegated agent treated 'implement week 1' as license to commit on its own (2026-10-10), which is exactly what the hard gate exists to prevent. When a cycle IS authorized, still keep push gated: commit `feat(lowbid-NN): …` locally, push only on the user's command.
- **Install the hook, don't just ship the script:** after landing `scripts/pre-commit`, run `chmod +x scripts/pre-commit && ln -sf ../../scripts/pre-commit .git/hooks/pre-commit` — a CI-only lint gate does not protect local commits, and an uninstalled hook is invisible until the first bad commit.
- **A newly added commit-msg hook stays semi-inert until its files are committed:** the pre-commit shim refuses to run while `.pre-commit-config.yaml` / hook scripts are untracked (it prints a 'git add .pre-commit-config.yaml' hint instead of enforcing). Land the hook files with the very next commit — do not remove or disable the hook to 'fix' the refusal — and after the landing commit verify enforcement with a direct script probe (echo a Cyrillic line into the script, expect exit 1).
- **Load this skill before any git/PR operation.** The format is strict and project-specific; working from memory of general conventions will produce wrong names (e.g. `refactor: desc` instead of `refactor(lowbid-00): desc`). The skill was NOT loaded when branch and PR #47 were created, and they had to be renamed post-hoc.
- After a frontend change, run the full local gate in one chain — `npm run build` + `npx vitest run` — before committing: `vite build` catches TS/import errors that vitest-with-mocks passes over, and an untested UI commit wastes a deploy cycle to find out.
- **Auditing «did anything get lost» in a squash-merge repo: verify CONTENT, not commits.** Squash makes every merged PR's branch read as unmerged by ancestry — commit-based checks false-alarm. Real losses are only closed-but-not-merged PRs: `gh pr list --state all --json number,state,mergedAt,headRefName` (empty closed-unmerged list = PR history clean). For branches with no PR: `git diff main...<ref>` (three-dot = the branch's unique changes) — empty means nothing to lose; non-empty means compare those files against main before judging. Build the no-PR set by comm'ing branch names against PR head names, delete in one batch `git push origin --delete $(cat list)`, then `git fetch --prune`.
- **Branch-listing pipelines eat branches silently**: `git branch --format='%(refname:short)'` still prefixes `* ` (current) and `+ ` (checked out in a worktree) — strip before feeding to xargs; and filter main with an EXACT match (`grep -vx main`, `grep -v 'origin/main$'`) — a loose `grep -v main` drops any branch whose name contains 'main' (e.g. `flatten-bid-to-main`), which then survives the cleanup invisibly. A branch held by a linked worktree can't be deleted until `git worktree remove <path>` (find it via `git worktree list`, check the worktree is clean first).
- Redeploys after UI commits: `gh workflow run cd.yaml --ref main -f branch=main`, then verify the LIVE site (curl the deployed `<title>` / assets), not just the local dist — the running container still serves the old bundle until the CD run finishes.
- CD deploys code AND restarts the backend systemd workers (`lowbid_playback_worker@1/2`, `lowbid_bid_worker`, `lowbid_api`) — verified live: workers get a fresh `ActiveEnterTimestamp` at deploy completion. Still verify that timestamp + journalctl for errors after every backend-affecting deploy; if a restart did NOT happen, the fix is inert and needs `ssh ssp-deploy` + restart (full recipe in the ssp-local-dev skill, deploy section).
