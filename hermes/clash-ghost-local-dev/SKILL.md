---
name: clash-ghost-local-dev
version: 0.1.0
author: Leonid Dolgirev (dlgrv), Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [tauri, svelte, rust, local-dev]
description: "Dev workflow for clash-ghost (Tauri 2 + Svelte) app."
---

# clash-ghost local dev

## When to Use
- Any work in `~/aezly/clash-ghost`: features, fixes, config generation, UI, bundling.
- Don't use for other Tauri apps without checking their layout first.

Repo: `~/aezly/clash-ghost`. Tauri 2 app: Svelte + TS frontend, Rust backend in `src-tauri/`.

## Layout
- Frontend follows FSD strictly: `src/entities`, `src/features`, `src/widgets`, imports via aliases (`$entities/profile`, `$features/manage-profiles`, …). Steiger (in `pnpm lint`) enforces layer boundaries — never import across layers sideways.
- Clash config generation lives in `src-tauri/src/config/clash.rs` (`generate_clash_config`); settings model in `src-tauri/src/settings.rs`.
- UI locale files: `en.ts` / `ru.ts` — every UI string exists in both.

## Verification order (run all before handing to user)
```bash
pnpm lint                # eslint + steiger
pnpm test                # vitest unit
cd src-tauri && cargo test
pnpm build               # svelte static build
E2E=1 pnpm test:e2e      # playwright
pnpm tauri build         # release .app + .dmg (only after everything green)
```

## Conventions
- TDD RED-first for frontend logic: pure functions live in `<layer>/<name>/model/*.ts` with vitest tests beside them. Write the failing test, see it fail, then implement.
- E2E specs rely on stable `data-testid` hooks — adding new interactive UI gets a `data-testid`; never rename existing ones.
- New Settings fields: add `#[serde(default)]` in Rust so old settings.json stays compatible, expose through Tauri command → store → UI toggle, and add the key to BOTH locale files.

## Pitfalls
- When patching locale files, the patch can land in the wrong locale block and create a duplicate key in one of en/ru — after editing, grep the file for the key and assert exactly one occurrence per locale.
- A header row that toggles a collapsible group must `on:click|stopPropagation` the buttons inside it (refresh/delete), or clicking the button also collapses the group.
- Collapsible-group state goes in a small store persisted to localStorage (widget `model/`), with an auto-collapse threshold for oversized groups and a user click overriding the default.

## Shipping a build to the user
`pnpm tauri build` produces `src-tauri/target/release/bundle/macos/Clash Ghost.app` and `bundle/dmg/*.dmg`. The user replaces the app in /Applications themselves — hand them the `open "…/bundle/macos"` command, don't move files into /Applications unasked. Verify the installed version by comparing `shasum -a 256` of the bundled binary vs the installed one before claiming the update landed.