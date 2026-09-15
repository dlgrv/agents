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

Project-specific git conventions for the **lowbid** repo (`sfsef/krutilka`, local path `~/aezly/krutilka`). This is NOT the general `github-pr-workflow` skill — those git/gh mechanics still apply, this skill only fixes the naming/format rules and the permission gate specific to this repo.

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

## Pitfalls

- Don't reuse generic branch names like `feat/add-user-authentication` (that's the general-skill example) — always include `lowbid-<n>`.
- Don't skip `lowbid-00` when there's no issue — an unscoped branch/commit breaks the convention's grep-ability.
- Don't infer permission to commit/branch/PR from "the task is done" — always require an explicit ask in-turn (see hard gate above).
- **Load this skill before any git/PR operation.** The format is strict and project-specific; working from memory of general conventions will produce wrong names (e.g. `refactor: desc` instead of `refactor(lowbid-00): desc`). The skill was NOT loaded when branch and PR #47 were created, and they had to be renamed post-hoc.
