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

- Access to Hermes' `state.db` (`~/.hermes/state.db`)
- Optional: provider-specific API keys for live pricing checks
- Optional: provider dashboard access (CometAPI, Anthropic, etc.)

## How to Run

```bash
# Quick audit of last 7 days' usage
terminal(command="sqlite3 ~/.hermes/state.db 'SELECT model, SUM(estimated_cost_usd), SUM(input_tokens), SUM(output_tokens), SUM(cache_read_tokens) FROM session_model_usage WHERE last_seen > strftime(\"%s\",\"now\",\-7 days\") GROUP BY model'", timeout=60)

# Full usage breakdown with provider context
terminal(command="python3 -c \"
import sqlite3
import json
from collections import defaultdict

db = sqlite3.connect('/root/.hermes/state.db')
rows = db.execute('''SELECT model, billing_provider, SUM(estimated_cost_usd), SUM(input_tokens), SUM(output_tokens), SUM(cache_read_tokens) FROM session_model_usage GROUP BY model, billing_provider''').fetchall()
for m,p,c,i,o,cr in rows:
    print(f'{m:30} {p:15} ${c:.2f} in={i/1e6:.1f}M out={o/1e6:.2f}M cache={cr/1e6:.1f}M')
\"", timeout=60)
```

## Procedure

1. **Extract actual usage from state.db**:
   - Run the SQL queries above to get your real token consumption
   - Note which models are being used and their volumes
   - Identify any unexpected cost spikes

2. **Gather current pricing**:
   - For each provider, fetch live pricing from their API or website
   - Include input, output, and cache-read rates per million tokens
   - Note subscription plans and their token equivalents

3. **Compare API vs subscription**:
   - Calculate what your usage would cost via API at current rates
   - Compare to subscription flat fees (Pro $20, Max 5x $100, Max 20x $200)
   - Check if subscriptions include models you use

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
| Check 7-day usage | `sqlite3 ~/.hermes/state.db 'SELECT ... WHERE last_seen > ...'` |
| Full usage breakdown | `python3 -c "import sqlite3; ..."` |
| Compare API vs subscription | Calculate: `(input×rate_in) + (output×rate_out)` vs subscription fee |
| Check compression settings | `hermes config get compression` |
| Optimize context | Reduce history length, enable compression at 200k tokens |

## Pitfalls

- **Subscription ≠ API access**: Claude Pro/Max cannot be used in Hermes' gateway — only in claude.com and Claude Code CLI. This is a common misconception that leads to wrong cost comparisons.
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
