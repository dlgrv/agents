---
name: github-issue-triage
description: "Triage upstream GitHub issues, prioritize user context."
license: MIT
metadata:
  hermes:
    tags: [GitHub, Issues, Triage]
    related_skills: [github-issues, github-issue-reports]
---

# GitHub Issue Triage and Response

Class: Analyzing and responding to issues in upstream repositories, focusing on user context, categorization, and providing actionable feedback where possible.

## Workflow

When users ask about issues in upstream repos:

### 1. List and Categorize Issues

```bash
# List all open issues to understand the landscape
gh issue list --state open

# Filter by specific labels if needed
gh issue list --state open --label "bug"
gh issue list --state open --label "enhancement"

# Search for specific keywords in issue titles/descriptions
gh issue list --state open --search "authentication error"
```

### 2. Categorize by Intent

- **Bug reports**: Issues describing unexpected behavior or defects
- **Feature requests**: Proposals for new functionality
- **Feedback**: General comments or suggestions
- **Help requests**: Personal assistance or guidance
- **Duplicate issues**: Already reported problems
- **Non-actionable**: General praise, questions about unrelated topics

### 3. Identify Actionable Issues

Focus on issues where you can add value:

- **Help requests** (individual users seeking guidance)
- **Feature requests** (clear, implementable suggestions)
- **Bug reports** with reproducible steps
- **Feedback** that can be addressed with context or resources

### 4. Prioritize Based on User Context

- **Individual help requests**: High priority when users are personally stuck
- **General project feedback**: Lower priority unless it affects many users
- **Critical bugs affecting functionality**: Medium priority
- **Nice-to-have features**: Lower priority

### 5. Selective Response Strategy

Not every issue requires a comment. Focus on:

- **Help requests**: Provide practical guidance or resources
- **Clear feature requests**: Acknowledge and suggest implementation paths
- **Reproducible bugs**: Offer troubleshooting steps or workarounds
- **Feedback**: Acknowledge and forward to maintainers if appropriate

### 6. Check for Existing Comments

Before adding your own response:

```bash
# View existing comments on an issue
gh issue view 42 --json comments

# Or via API
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues/42/comments" \
  | python -c "
import sys, json
for c in json.load(sys.stdin):
    print(f\"@{c['user']['login']}: {c['body'][:100]}...\")"
```

## Response Templates

### Help Request Response

```bash
gh issue comment 42 --body "@username, thanks for reaching out! Based on your description, here are some suggestions:

1. [Specific guidance related to the issue]
2. [Practical workaround if available]
3. [Resource link if helpful]

If you need more specific help, feel free to share more details about your setup or ask follow-up questions."
```

### Feature Request Response

```bash
gh issue comment 42 --body "Thanks for the suggestion! This is a great idea that could benefit many users.

Here's how it might work:
- [Brief explanation of implementation approach]
- [Potential benefits]

I've forwarded this to the maintainers for consideration."
```

### Bug Report Response

```bash
gh issue comment 42 --body "Thanks for reporting this! To help us understand and reproduce the issue:

1. Have you tried [basic troubleshooting step]?
2. What's your environment (OS, version, etc.)?
3. Can you provide a minimal reproduction case?

This will help the maintainers investigate more effectively."
```

## Best Practices

- **Be concise**: Focus on actionable guidance rather than lengthy explanations
- **Use markdown**: Format responses with clear sections and code blocks where needed
- **Link to resources**: Include relevant documentation, examples, or similar issues
- **Stay constructive**: Even for bug reports, maintain a helpful tone
- **Know your limits**: Don't promise fixes you can't deliver; focus on guidance and context

## Common Pitfalls

- **Over-commenting**: Not every issue needs a response; prioritize where you can add value
- **Making promises**: Don't commit to implementing features or fixing bugs unless you have the authority
- **Ignoring context**: Always consider the user's specific situation and experience level
- **Duplicate responses**: Check existing comments before adding your own

## See Also

- `references/response-examples.md` — Concrete examples of issue responses