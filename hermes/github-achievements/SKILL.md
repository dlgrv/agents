---
name: github-achievements
description: "Legitimate strategy for earning GitHub achievements when most of your repos are private. Use when the user asks how to get GitHub badges/achievements, or wants to maximize their profile activity."
version: 1.0.0
author: dlgrv
license: MIT
tags: [github, achievements, profile, contributions]
---

# GitHub Achievements Strategy

A legitimate, non-gaming strategy for earning GitHub achievement badges given a
mostly-private GitHub setup. The goal is real, useful work (keeping your public
skills hub current) with achievements as a side effect — NOT farming empty PRs.

> Re-verify names/thresholds against
> https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/managing-contribution-settings-on-your-profile/viewing-contributions-on-your-profile
> before relying on this; GitHub changes achievements over time.

## Achievement catalog (verified)

| Achievement | How to earn | Levels (default/br/sl/gold) |
|---|---|---|
| Pull Shark | Merged PRs | 2 / 8 / 16 / 32 |
| Star-Struck | Stars on your public repos | 1 / 10 / 24 / 48 |
| Quick-Draw | PR merged <5 min after opening | 1 / 10 / 24 / 48 |
| Pair Extraordinaire | Commits with `Co-authored-by` | 2 / 16 / 128 / 1024 |
| Galaxy Brain | Accepted Discussion answers | 1 / 10 / 24 / 48 |
| Open Sourcerer | Consecutive contribution weeks | 16 / 128 / 512 / 4096 |
| YOLO | Merge PR bypassing branch protection | 1 |
| GitHub Sponsor | Someone sponsors you | 1 |

## The private-repo tension

If ALL your repos are private (the user's deliberate choice):
- **Unreachable:** Pull Shark, Star-Struck, Galaxy Brain, Quick-Draw, YOLO,
  GitHub Sponsor — they require PUBLIC activity.
- **Still reachable:** Pair Extraordinaire and Open Sourcerer (they count private
  commits / contribution facts too).

## Your lever: the public `dlgrv/agents` repo

`dlgrv/agents` is the user's only public repo (the agent-skills hub). Use it as the
engine for public-repo achievements:
- Every real change → branch → PR → merge = +1 Pull Shark.
- Regular PRs → Open Sourcerer (consecutive weeks) grows naturally.
- Ask peers to star it → Star-Struck.

## Concrete actions (honest only)

| Achievement | Action via dlgrv/agents |
|---|---|
| Pull Shark | Send every real change as a PR (branch → merge). Even small skill updates count. |
| Open Sourcerer | Keep a streak: at least one PR/commit per week to dlgrv/agents. |
| Quick-Draw | Open PR and merge within 5 min for trivial, safe changes. |
| Pair Extraordinaire | Add `Co-authored-by: <agent/collaborator> <email>` to commits (counts on private too). |
| Star-Struck | Share dlgrv/agents; ask peers to star. Social, not technical. |
| YOLO | Only if a repo has branch protection and you intentionally bypass for a hotfix — rare, not worth chasing. |
| Galaxy Brain | Answer in GitHub Discussions of projects you use. |
| GitHub Sponsor | Becomes relevant if you publish useful open source others sponsor. |

## Workflow (established, no direct main pushes)

```bash
# 1. feature branch off main
git checkout -b feat/<name>

# 2. make changes, commit
git add -A && git commit -m "feat: ..."

# 3. push + open PR
git push -u origin feat/<name>
gh pr create --base main --head feat/<name> --title "..." --body "..."

# 4. merge + cleanup
gh pr merge <N> --merge --delete-branch

# Update third-party skills (real change → PR):
git submodule update --remote --recursive
bash scripts/snapshot.sh
# then commit + PR as above

# Pair Extraordinaire co-author trailer:
git commit -m "feat: x

Co-authored-by: Hermes Agent <noreply@hermes.ai>"
```

## Anti-patterns (DO NOT)

- **No empty/gaming PRs or commits** purely to farm achievements. GitHub detects
  low-signal history; it pollutes your log and is against the spirit of the badges.
- **Do not re-publicize private repos** just for stars — you chose to hide them.
  `dlgrv/agents` is sufficient.
- Achievements are a side effect of real, useful work (keeping your skills hub
  current). Optimize for that, not the badge.
