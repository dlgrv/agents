---
name: hermes-glm-optimization
description: "GLM model optimization for Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    files: [SKILL.md]
---

# GLM Model Optimization for Hermes Agent

This skill provides best practices for using GLM models (especially GLM-5.3-flash) with Hermes Agent, focusing on error handling, context management, and cost optimization.

## Error 1210: Reasoning Mandatory

**Symptom:** `Error code: 1210 - "This model always engages in thinking and cannot be disabled; please use low, high, or max"`

**Root cause:** GLM-5.3-flash always engages in reasoning, regardless of the `reasoning_effort` setting. Sending `{enabled: false}` triggers this error.

**Fix:** Never set `reasoning_effort: none` or disable reasoning for GLM-5.3-flash. Accept the default behavior or use `low`/`medium`/`high`.

**If you see repeated 1210 errors in a session:**
- The context may be too large, causing thinking to exhaust output limits
- Use `/compress` to trim history
- For persistent issues, start a new session with `/new session-name`

**Note:** This error is model-specific; other providers may allow disabling reasoning without error.

## Context Management

GLM-5.3-flash benefits from context compression in long sessions:
- Use `/compress` when sessions exceed 20-30 messages
- Large contexts increase the likelihood of thinking exhausting output limits
- Consider starting new sessions for complex, multi-turn tasks to avoid context bloat

## Provider Configuration

When using GLM-5.3-flash via Z.ai or other providers:
- Verify the model name exactly matches provider specifications (case-sensitive)
- Check that auxiliary models (vision, compression) are configured to use a different provider if needed
- Monitor cache-read usage for cost optimization

## Cost Optimization

GLM-5.3-flash cache-read is significantly cheaper than input tokens:
- Structure prompts to maximize cache hits
- Reuse similar prompts within sessions
- Consider subscription plans if cache-read usage is high

## Troubleshooting Checklist

When encountering GLM-related errors:
1. Check if `reasoning_effort` is set to `none` – if so, change to `low`/`medium`/`high`
2. Use `/compress` to reduce session context size
3. Verify model name matches provider specifications
4. Check auxiliary model configuration
5. Monitor token usage patterns to identify optimization opportunities
