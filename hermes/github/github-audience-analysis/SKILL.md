---
name: github-audience-analysis
description: "Analyze GitHub repo audience via available APIs."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [github, analysis]
related_skills: [github-repo-management]
---

# GitHub Repository Audience Analysis

Analyze GitHub repository audience demographics and community signals using available APIs and indirect metrics. This skill focuses on what IS accessible via GitHub APIs, respecting platform privacy constraints.

## Limitations (Important)

GitHub API does NOT expose individual stargazer lists for third-party repos (even with authentication). This is a platform privacy feature, not an API bug:
- REST: Returns 404 for `/repos/{owner}/{repo}/stargazers`
- GraphQL: Returns `totalCount: 0` and empty edges
- Only repo owners can see who starred their repos

## Available Audience Signals

### 1. Star Count and Growth

```bash
# Get current star count (public info)
gh repo view owner/repo --json stargazers_count

curl -s "https://api.github.com/repos/owner/repo" | python -c "import sys,json; print(json.load(sys.stdin)['stargazers_count'])"

# Track star growth over time (requires historical data)
echo "$(date +%Y-%m-%d) $(gh repo view owner/repo --json stargazers_count | jq '.stargazers_count')" >> stars.log
```

### 2. Fork Count and Fork Network

```bash
# Fork count (public)
gh repo view owner/repo --json forks_count

curl -s "https://api.github.com/repos/owner/repo" | python -c "import sys,json; print(json.load(sys.stdin)['forks_count'])"

# List forks (public info)
gh repo view owner/repo --json forks --jq '.forks[] | "\(.full_name) \(.stargazers_count) stars"'

curl -s "https://api.github.com/repos/owner/repo/forks" | python -c "
import sys, json
for f in json.load(sys.stdin):
    print(f'{f[\"full_name\"]} {f[\"stargazers_count\"]} stars')
"
```

### 3. Issue and PR Activity

```bash
# Recent issues (public)
gh issue list --repo owner/repo --limit 10 --json 'title,user,created_at,comments'

curl -s "https://api.github.com/repos/owner/repo/issues?state=open&per_page=10" | python -c "
import sys, json
for i in json.load(sys.stdin):
    print(f'{i[\"title\"]} by {i[\"user\"][\"login\"]} ({i[\"created_at\"]})')
"

# Recent PRs (public)
gh pr list --repo owner/repo --limit 10 --json 'title,user,created_at,merged_at'

curl -s "https://api.github.com/repos/owner/repo/pulls?state=all&per_page=10" | python -c "
import sys, json
for p in json.load(sys.stdin):
    print(f'{p[\"title\"]} by {p[\"user\"][\"login\"]} ({p[\"merged_at\"] or \"open\"})')
"
```

### 4. Contributor Analysis (Limited)

```bash
# List contributors (public info, but no details)
gh repo view owner/repo --json contributors --jq '.contributors[] | "\(.login) \(.contributions) contributions"'

curl -s "https://api.github.com/repos/owner/repo/contributors" | python -c "
import sys, json
for c in json.load(sys.stdin):
    print(f'{c[\"login\"]} {c[\"contributions\"]} contributions')
"

# Note: No demographic info available via API
```

### 5. Language and Technology Stack

```bash
# Primary language
gh repo view owner/repo --json language

curl -s "https://api.github.com/repos/owner/repo" | python -c "import sys,json; print(json.load(sys.stdin)['language'])"

# Languages used (by percentage)
gh repo view owner/repo --json languages --jq '.languages | to_entries[] | "\(.key): \(.value)%"'

curl -s "https://api.github.com/repos/owner/repo/languages" | python -c "
import sys, json
langs = json.load(sys.stdin)
total = sum(langs.values())
for lang, bytes in langs.items():
    print(f'{lang}: {int(bytes/total*100)}%')
"
```

## Indirect Audience Inference

### 1. Repository Topics and Tags

```bash
# Repository topics (public)
gh repo view owner/repo --json topics --jq '.topics[]'

curl -s "https://api.github.com/repos/owner/repo/topics" | python -c "import sys,json; print(' '.join(json.load(sys.stdin)['names']))"
```

Topics can indicate intended audience:
- `machine-learning`, `python` → technical/developer audience
- `documentation`, `tutorial` → learner audience
- `chinese`, `russian` → language-specific audience

### 2. README and Description Analysis

```bash
# README content (public)
gh api repos/owner/repo/readme --jq '.content' | base64 -d > readme.md

curl -s "https://api.github.com/repos/owner/repo/readme" | python -c "import sys,json; print(json.load(sys.stdin)['content'])" | base64 -d > readme.md

# Analyze for language clues, target audience mentions
# (requires manual text analysis or NLP tools)
```

### 3. Issue/PR Language Patterns

```bash
# Check issue/PR titles and bodies for language patterns
gh issue list --repo owner/repo --limit 20 --jq '.[] | .title' | head -5
gh pr list --repo owner/repo --limit 20 --jq '.[] | .title' | head -5
```

## Case Study: HowToLiveBetter Repository

### Available Metrics

```bash
# Star count and growth
gh repo view eternity4719/HowToLiveBetter --json stargazers_count
# Result: 5550 stars (as of 2026-09)

# Fork network
gh repo view eternity4719/HowToLiveBetter --json forks --jq '.forks[] | "\(.full_name) \(.stargazers_count) stars"'
# Shows forks like dlgrv/HowToLiveBetter (our fork)

# Recent activity
gh pr list --repo eternity4719/HowToLiveBetter --limit 5 --json 'title,user,created_at,merged_at'
gh issue list --repo eternity4719/HowToLiveBetter --limit 5 --json 'title,user,created_at,comments'
```

### Inferred Audience (From Available Data)

- **Primary language**: Chinese (repo name, issue comments)
- **Technical audience**: Developers (book content format, technical nature)
- **International reach**: Multiple language forks (RU, EN translations)
- **Growth pattern**: Steady star accumulation (consistent engagement)

### What Cannot Be Determined

- Individual user demographics (no access to stargazer lists)
- Geographic distribution of users
- Professional vs. hobbyist breakdown
- Exact language preferences beyond what's visible in issues/PRs

## Best Practices

1. **Respect API limitations**: Do not attempt to bypass stargazer list restrictions
2. **Focus on public metrics**: Star counts, forks, issues, PRs, languages, topics
3. **Combine with indirect signals**: README analysis, issue language patterns
4. **Track trends over time**: Star growth, contribution patterns
5. **Cross-reference with external signals**: Social media mentions, blog posts about the repo

## Tools and Scripts

### Star Growth Tracker

```bash
#!/bin/bash
# track-stars.sh
OWNER="eternity4719"
REPO="HowToLiveBetter"
LOG_FILE="stars_$(date +%Y%m).log"

while true; do
    STARS=$(gh repo view $OWNER/$REPO --json stargazers_count | jq '.stargazers_count')
    echo "$(date +%Y-%m-%d\ %H:%M:%S) $STARS" >> $LOG_FILE
    sleep 86400  # Daily
    tail -n 30 $LOG_FILE
done
```

### Fork Network Analyzer

```bash
#!/bin/bash
# analyze-forks.sh
OWNER="eternity4719"
REPO="HowToLiveBetter"

echo "Fork network for $OWNER/$REPO:"
gh repo view $OWNER/$REPO --json forks --jq '.forks[] | "\(.full_name) \(.stargazers_count) stars \(.created_at)"' | sort -k3
```
