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

Project-specific git conventions for the **lowbid** repos — `sfsef/krutilka` (local `~/aezly/krutilka`) and the SSP repo **`ortblab/ssp`** (private, org repo; local `~/aezly/lowbid-ssp`, Go module `github.com/ortblab/ssp`). Repo PLACEMENT rule: `sfsef` is a personal account, not an organization — user-facing product repos go under the **`ortblab`** org with neutral names; the `lowbid` codename must NOT appear in repo names or repo CONTENT (user-scrubbed it everywhere: README, module path, cookies/env, docs). The commit/branch prefix `lowbid-NN` stays — it's the task-tracking convention and lives only in git history. This is NOT the general `github-pr-workflow` skill — those git/gh mechanics still apply, this skill only fixes the naming/format rules and the permission gate specific to these repos.

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
- **Load this skill before any git/PR operation.** The format is strict and project-specific; working from memory of general conventions will produce wrong names (e.g. `refactor: desc` instead of `refactor(lowbid-00): desc`). The skill was NOT loaded when branch and PR #47 were created, and they had to be renamed post-hoc.
