# Usage Data Sources

Where to find real usage data when auditing LLM spend or activity frequency.

## Hermes (`~/.hermes/state.db`, sqlite)

- `sessions` table carries per-session sums: `input_tokens`, `output_tokens`, `cache_read_tokens`, `api_call_count`, plus `billing_provider`, `estimated_cost_usd`, `model`.
- `sessions.started_at` / `ended_at` / `last_activity_at` are unix epoch FLOATS.
- Interaction volume: `messages` where `role='user'` — `count(*)` grouped by `strftime('%Y-%m-%d', timestamp, 'unixepoch')` gives prompts/day. Sessions/day overcounts (background, cron, retries).
- First call of an audit: `pragma_table_info` on both tables — columns drift between Hermes versions. If a query returns zero rows, suspect timestamp format before suspecting no usage.

## Cursor (macOS)

- Reliable source: `~/Library/Application Support/Cursor/User/globalStorage/conversation-search.db`
  - `conversations` table: `id`, `title`, `updated_at` (ms epoch), `source` ('local' | 'cloud-cache'), `is_archived`.
  - One row ≈ one chat/composer session; group `updated_at/1000` by day/month for activity frequency. Includes chats from all workspaces.
- Dead end: workspace `state.vscdb` key `composer.composerData` — after Cursor's data migration it holds only `selectedComposerIds`, not per-chat records with timestamps. Don't mine it.
- Dead end: global `state.vscdb` has no `composerData:<id>` keys.

## Subscription limit math

- Provider weekly quotas (e.g. Z.ai GLM Coding Pro ≈ 263–526M tokens/week) → multiply by ~4.3 for a monthly ceiling.
- Count cache-read tokens against the quota: on agent workloads cache reads dwarf input+output by 10–20x and dominate total consumption.
- 5-hour rolling limits (if the plan has them) bind before monthly quotas on heavy days — check peak-day token totals, not just monthly averages.
