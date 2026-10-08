---
name: llm-provider-cost-audit
description: Audit LLM provider costs and optimize spend.
version: 0.1.0
author: Leonid Dolgirev (dlgrv), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm, cost, audit, optimization, pricing]
    related_skills: [llm-provider-key-validation, hermes-config-tuning]
---

# LLM Provider Cost Audit

Audit and optimize LLM provider costs by comparing API pay-as-you-go pricing with subscription plans, analyzing actual usage patterns, and identifying savings opportunities. Applies to any provider (Z.ai, Anthropic, OpenAI, CometAPI, etc.) and integrates with Hermes' usage tracking.

## When to Use

- User asks "How much does this model cost?" or "Is the subscription cheaper than API?"
- Monthly bills are unexpectedly high and you need to understand why
- Comparing multiple providers for a workload (e.g., switching from Z.ai to Claude)
- Evaluating whether a Claude Pro/Max subscription would save money vs API calls
- Optimizing context window usage (prompt caching, compression thresholds)

Don't use for: one-time pricing lookups (web search is faster), or when the user already knows their usage volume.

## Prerequisites

- Access to Hermes' `state.db`: `~/.hermes/state.db` on the Mac, `/root/.hermes/state.db` on the VPS
- Cursor (if auditing editor usage): `~/Library/Application Support/Cursor/User/globalStorage/conversation-search.db`
- Optional: provider-specific API keys for live pricing checks
- Optional: provider dashboard access (CometAPI, Anthropic, etc.)

Before writing any SQL, probe the schema — table names and column layouts differ between installs and Hermes versions:

```python
db.execute("select name from pragma_table_info('sessions')").fetchall()
```

On current local installs the `sessions` table already carries per-session sums (`input_tokens`, `output_tokens`, `cache_read_tokens`, `api_call_count`) — there is no `session_model_usage` table on macOS desktop installs. `started_at`/`timestamp` are **unix epoch floats, not ISO strings**: use `strftime('%Y-%m', started_at, 'unixepoch')`, never `substr(started_at,1,7)` — string slicing on an epoch number silently returns zero rows.

## How to Run

Monthly/daily Hermes usage (verified working query pattern):

```sql
SELECT strftime('%Y-%m', started_at, 'unixepoch') m, count(*) sessions,
       round(sum(input_tokens)/1e6,1) inM, round(sum(output_tokens)/1e6,1) outM,
       round(sum(cache_read_tokens)/1e6,1) cacheM, sum(api_call_count) calls
FROM sessions GROUP BY m ORDER BY m;
```

Interaction frequency (real user activity, not session starts): count `role='user'` rows in `messages` grouped by day — sessions overcount automated/cron work, messages reflect actual prompts.

Editor (Cursor) usage: see `references/usage-data-sources.md` — Cursor's workspace `composer.composerData` keys do NOT contain per-chat data (migrated); the reliable source is `conversation-search.db`.

## Procedure

0. **Audit cross-tool activity when asked 'will limits suffice'**: the user
   runs multiple AI surfaces (Hermes + Cursor). Pull per-tool daily activity
   (Hermes: `messages WHERE role='user'` per day; Cursor:
   `conversation-search.db` `conversations.updated_at`) and report both
   separately — average per day, active days, and peak days. Only agent
   traffic counts against a coding plan; editor billing is separate.

1. **Extract actual usage from state.db**:
   - Run the SQL queries above to get your real token consumption
   - Note which models are being used and their volumes
   - Identify any unexpected cost spikes

2. **Gather current pricing**:
   - For each provider, fetch live pricing from their API or website
   - Include input, output, and cache-read rates per million tokens
   - Note subscription plans and their token equivalents (Z.ai's official
     formula: monthly plan quota ≈ 15–30× the fee at API rates; user-made
     back-of-envelope estimates often UNDERSTATE this — check the docs)

3. **Compare API vs subscription**:
   - Calculate what your usage would cost via API at current rates
   - Compare to subscription flat fees, using the provider's own published
     quota-conversion numbers where available
   - Check if subscriptions include the models the user actually uses
     (e.g. Z.ai plans cover the whole GLM family including top models, with
     per-model credit multipliers — cheap models stretch the quota ~3× further)
   - Audit DAILY activity peaks (sessions/messages per day, token spikes),
     not just monthly totals — windowed plan limits bite on peak days

4. **Analyze optimization opportunities**:
   - Context compression savings (auto-compress at 200k tokens)
   - Prompt caching potential (repeated context reuse)
   - Model switching (Haiku for simple tasks, Opus for complex)
   - Provider fallback chain efficiency

5. **Document findings**:
   - Current monthly cost breakdown
   - Recommended provider/model mix
   - Configuration changes needed
   - Expected savings

## Quick Reference

| Task | Command |
|------|---------|
| Monthly Hermes usage | `SELECT strftime('%Y-%m', started_at, 'unixepoch'), sum(input_tokens), sum(cache_read_tokens), sum(api_call_count) FROM sessions GROUP BY 1` |
| Prompts per day | `SELECT strftime('%Y-%m-%d', timestamp, 'unixepoch'), count(*) FROM messages WHERE role='user' GROUP BY 1` |
| Cursor chat frequency | `conversation-search.db` → `conversations.updated_at` (see references/usage-data-sources.md) |
| Compare API vs subscription | Calculate: `(input×rate_in) + (output×rate_out)` vs subscription fee; include cache reads |
| Check compression settings | `hermes config get compression` |
| Optimize context | Reduce history length, enable compression at 200k tokens |

## Pitfalls

- **Epoch timestamps**: Hermes `sessions.started_at` / `messages.timestamp` are unix epoch floats. Filter with `strftime('%s','now','-30 day')` comparisons or `strftime(..., 'unixepoch')` formatting — string functions (`substr`, `date()`) on the raw column return empty result sets, which looks like 'no usage' if you don't check.
- **Subscription ≠ API access**: coding-plan subscriptions are endpoint-scoped, not protocol-scoped — they work in Hermes only via the plan's dedicated coding endpoint (e.g. Z.ai GLM Coding Plan: `api.z.ai/api/coding/paas/v4` for OpenAI protocol, `api.z.ai/api/anthropic` for Anthropic), and editor subscriptions like Cursor's billing are separate from any provider plan being evaluated. Confirm which surface the plan actually covers before claiming it fits the user's workflow.
- **Plan quotas are windowed, not just monthly**: Z.ai plans also cap prompts per 5 hours and per week. A workload whose MONTHLY token total fits the plan can still hit the 5-hour limit on heavy days — audit daily peaks, not just monthly sums, before recommending a tier.
- **One subscription can't cover both agent and editor**: Cursor usage belongs on its own billing; never fold editor sessions into the provider-plan fit calculation.
- **Token inflation**: New models (Sonnet 5) may be less efficient than older ones (Sonnet 4.6) — same text = more tokens, increasing API cost.
- **Cache read costs**: Long sessions with cached context can have massive cache-read token counts that significantly impact cost.
- **Provider-specific quirks**: Some providers (CometAPI) offer different pricing than official APIs — always verify current rates.
- **Usage spikes**: One-off heavy sessions (model training, large deployments) can skew monthly averages.

## Verification

- [ ] Actual usage extracted from state.db matches expected costs
- [ ] All provider pricing verified against current rates
- [ ] API vs subscription comparison accounts for Hermes' limitations
- [ ] Configuration changes tested in a staging environment
- [ ] Savings estimates backed by real usage data, not assumptions

## Example Output

```
Current usage (7 days):
ZHIPU/GLM-5.3-Flash          zai             $25.30 in=50.3M out=2.7M cache=657.8M

CometAPI claude-sonnet-5      cometapi-claude $234.00 in=50.3M out=2.7M cache=657.8M
Anthropic claude-sonnet-5     anthropic        $259.00 in=50.3M out=2.7M cache=657.8M

Subscription comparison:
- Current (Z.ai GLM): $25/week = $100/month
- Claude Max 20x: $200/month (but not usable in Hermes)
- Recommendation: Keep Z.ai for Hermes, use Claude Code for heavy tasks

Optimizations:
- Enable compression at 200k tokens (saves ~30% on long sessions)
- Use model aliases for task-appropriate model selection
```
