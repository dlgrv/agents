# GitHub Issue Response Examples

## Help Request Response Example

**Issue**: User asking for guidance on a specific problem

```bash
gh issue comment 42 --body "@username, thanks for reaching out! Based on your description, here are some suggestions:

1. [Specific guidance related to the issue]
2. [Practical workaround if available]
3. [Resource link if helpful]

If you need more specific help, feel free to share more details about your setup or ask follow-up questions."
```

## Feature Request Response Example

**Issue**: User proposing new functionality

```bash
gh issue comment 42 --body "Thanks for the suggestion! This is a great idea that could benefit many users.

Here's how it might work:
- [Brief explanation of implementation approach]
- [Potential benefits]

I've forwarded this to the maintainers for consideration."
```

## Bug Report Response Example

**Issue**: User reporting a defect

```bash
gh issue comment 42 --body "Thanks for reporting this! To help us understand and reproduce the issue:

1. Have you tried [basic troubleshooting step]?
2. What's your environment (OS, version, etc.)?
3. Can you provide a minimal reproduction case?

This will help the maintainers investigate more effectively."
```