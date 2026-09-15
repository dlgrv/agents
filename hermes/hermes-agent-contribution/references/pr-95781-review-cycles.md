# Case study: PR #95781 (Desktop Debug MCP) — 4 review rounds to closed

Timeline and what moved the needle each round. Upstream: NousResearch/hermes-agent, fork: dlgrv.

## Round-by-round

1. **Initial review (head `602c84e72`)** — 2 P1 blockers: isolation guard trusted a caller-declared
   home instead of target-derived proof; `ui_screenshot({path})` was an arbitrary file write.
2. **Fix round (`6faa15cada`+)** — added Electron-emitted descriptor `__DEBUG_MCP_INSTANCE__
   = {nonce, dataRoot}` injected on did-finish-load; screenshot returns typed MCP image content.
   Reviewer accepted screenshot typing immediately, but found the descriptor re-derived the home
   from `HERMES_HOME` env alone while the app also honours `HERMES_DESKTOP_USER_DATA_DIR`,
   Windows registry, `%LOCALAPPDATA%` → descriptor could attest the WRONG root.
3. **Home-authority round** — extracted `electron/hermes-home.ts::resolveHermesHomeFromInputs()`
   (pure, injected deps, `pathModule` injectable so win32 paths test on macOS); `main.ts` computes
   `HERMES_HOME` BEFORE `DEV_CDP_INSTANCE` (order mattered! it was computed later at :768) and
   passes `resolvedHermesHome` in. Guard split into two independent policies: identity
   (expected==realized) AND protected-home refusal (realized ∈ {server defaultHome, os.homedir()
   /.hermes} → REFUSED even when caller agrees — "agreement is not permission"). Reviewer: closed.
4. **Self-audit round (`f976cc52ae`..`68a76633d1`)** — auto-invalidate CDP handle on socket close
   (identity guard: stale close must not null a newer handle); `evalBounded` `?? 'null'`;
   `requireSelector` shared by act tools; `CDP.eval` → `r.result?.value`. Reviewer re-reviewed the
   new head unprompted: "source review closed; remaining release authority is hosted execution,
   not another requested code change."

## Practical details that mattered

- `path.win32` must be injected when testing Windows path logic on macOS — `path.join` mangles
  `C:\` paths on POSIX, and `normalizeHermesHomeRoot(path, {pathModule})` accepts an override.
- Rebase verification: `git range-diff <old-base>..<old-head> upstream/main..<new-head>` — every
  line must read `N: old = N: new`; proves zero content drift to the reviewer.
- `gh api .../pulls/N/reviews` (not issues comments) returns review bodies; EOF errors on the API
  are transient — retry after a sleep.
- Pre-existing environment flakes (exit 127 in `/bin/sh`-driven launcher tests) reproduce on the
  old reviewed head too — document in the PR comment, don't chase.
- Hosted jobs (CI/Docker/Nix) are `action_required` per head SHA until a maintainer authorizes;
  local receipts don't transfer. Post-rebase: comment the new head + verification numbers.

## Skill cross-links

- Tooling half of this PR: `hermes-desktop-ui-debugging`.
- Plan documents produced: `~/.hermes/plans/2026-08-27_193000-desktop-mcp-p1-home-authority.md`,
  `2026-08-27_234000-desktop-mcp-audit-fixes.md`, `2026-08-28_003000-pr-95781-landing-readiness.md`.
