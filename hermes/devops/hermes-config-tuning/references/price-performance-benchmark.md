# Price-Performance Benchmark Reference

This file supplements the `hermes-config-tuning` skill with actionable intelligence
on model pricing and Artificial Analysis Intelligence Index rankings. Updated
regularly from https://artificialanalysis.ai/models.

## Top Value Models (2026-09)

| Model | AA Index | $/M Input | $/M Cache | $/M Output | Notes |
|---|---|---|---|---|---|
| GLM-5.3-Flash | 42 | $0.15 | $0.03 | $0.50 | Best overall value for agent workloads |
| DeepSeek V4 Flash | 25 | $0.14 | $0.014 | $0.28 | Cheap, but lower agentic capability |
| GLM-5.3 (full) | 45 | ~$1.40 | ~$0.26 | ~$4.40 | Use for hard stop problems only (hybrid workflow) |
| Kimi K3 | 57 | $3.00 | $0.30 | $15.00 | Top open-weight, expensive |
| Claude Sonnet-5 | ~55 | $3.00 | $0.30 | $15.00 | High intelligence, high cost |

## Key Insights

- **AA Index 40–45 is the sweet spot:** Models in this range offer the best
  balance of intelligence and cost for general agent work.
- **Cache-read dominates cost:** At your usage profile (cache-read ≈10× input),
  GLM-5.3-Flash costs 60% of CometAPI's equivalent despite higher headline rates.
- **Mirror vs vendor direct:** Vendor APIs (z.ai, deepinfra) often beat mirrors
  (CometAPI, OpenRouter) on cache-read pricing — verify with your usage.

## Hybrid Workflow Strategy

For users with $100/month budget:

1. **$60/month:** GLM-5.3-Flash for 90% of tasks
2. **+$50/month:** Switch to full GLM-5.3 for hard problems (debug, architecture)
3. **Total: ~$110/month** for +3 AA intelligence on complex workloads

## When to Upgrade

- **Never upgrade for <5 AA points:** The cost increase rarely justifies it.
- **Consider full models only for:**
  - Complex multi-step reasoning tasks
  - Architecture design and refactoring
  - Persistent debugging sessions
  - When cache-read rate is low (<20% of total tokens)

## Provider Notes

- **Z.ai GLM-5.3-Flash:** Native cache pricing ($0.03/M), honors reasoning_effort
- **CometAPI GLM-5.3-Flash:** Ignores reasoning_effort, higher cache pricing
- **DeepSeek V4 Flash:** Excellent price but lower AA Index (25) for agentic work

## Discovery Workflow

1. Pull your real usage: `sqlite3 ~/.hermes/state.db "SELECT SUM(input_tokens), SUM(cache_read_tokens), SUM(output_tokens) FROM session_model_usage WHERE model LIKE '%glm-5.3%'"`
2. Calculate monthly cost: `(inp*$0.15 + cache*$0.03 + out*$0.50) * (30/14)`
3. Compare against AA Index table
4. Test upgrade only if AA gain > cost increase ratio

*Prices and AA Index subject to change — verify at artificialanalysis.ai/models*