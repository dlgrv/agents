# Clippy assistant subsystem (as of 2026-09-05)

READ before editing anything under `src/widgets/assistant/` or `src/entities/assistant/`.

## Architecture map

- **Mount point:** `src/widgets/assistant/ui/mount-assistant.ts` (~214/350 LOC) — `mountAssistant()` boots the agent, resets `speechGap`, binds all reactions, wires the context menu (`openClippyMenu` → `ClippyMenuActions`). `destroyAssistant()` must clean up every imperative controller.
- **Reaction modules:** `lib/reactions/types.ts` — `ReactionModule { id; bind(ctx): unbind }`. Each is a passive listener (pointermove/keydown/etc.) that returns a cleanup fn. Bound in a list in `mount-assistant.ts`. Existing: roam, drag-end, icon-hover, window reactions, `secretReaction` (types 'clippy' into a buffer).
- **Agent:** `OfficeAgent` (`lib/agent.ts` + `agent-motion.ts`) with helpers already implemented: `moveTo(x,y,ms)`, `playAside(anim)` (returns false if clip missing — silently skip), `gestureAt(x,y)`, `directionTo(el,x,y)` → 'Left/Right/Up/Down', `pinLayout()`, `animate()` (random non-idle clip), `speak(text, hold?)`, `finishSpeech()`, `isIdling()`, `stopCurrent()`.
- **Tips pipeline:** `model/tips.ts` — `ASSISTANT_TIPS` array + `createTipPipeline` + `tipReady` gating (muted / energy / `tip-cooldown.ts` visit-cooldowns / `SPEECH_GAP_MS = 8s` after welcome). Tips: `{ id, animation, text: {ru,en} }` or `variants[]` (picked uniformly). `showTip(id)` goes through the gate — for user-triggered rewards the gate can swallow the tip (energy quiet); bypass via direct `agent.speak()` + `isAssistantMuted()` check when it must always show.
- **tips.ts LOC budget is tight:** ~346/350 (AGENTS.md cap 350). Adding tips requires a split first — plan: move `window_move_*` tips (~8 entries) to `model/window-move-tips.ts` (keep re-export, specs import from `../../model/tips`), new tips into `model/playful-tips.ts` pushed into `ASSISTANT_TIPS`.
- **Persist:** `src/entities/assistant/model/persist.ts` — only place for assistant localStorage, keys `dlgrv.assistant.*` (`MUTED_UNTIL_KEY` etc.). Every new key: int-parse helper + add `removeItem` to `clearAssistantState`. `isAssistantMuted()` / `getLang()` (from `@/entities/lang`) for speech gating.
- **Context menu:** `lib/context-menu.ts` — `ClippyMenuActions` interface; menu rebuilds on every open so labels can read live state (e.g. game toggles). Items: «Пошевелиться», «Домой», etc.
- **Chance policy v6** (`docs/superpowers/specs/2026-09-05-clippy-liveliness-v6.md`): probability-gated reactions follow a fixed policy; **new opt-in/deterministic features do NOT use `roll`**. Warmup + `reduceMotion()` no-op guards required for any motion feature.

## Voice & copy conventions (Clippy lines)

- Dry, deadpan Clippy voice. RU primary + EN pair. No trailing period on the last sentence of a block (user punctuation rule).
- One-off reward/secret lines bypass the tip pipeline (mute-check only); ambient tips always go through `showTip`.

## Existing feature inventory (don't duplicate)

Reactions to window open/close/move, orbit-around-window, dino score reactions, drag-protest variants, idle pools by context (empty desktop / one window / night), session-triggered tips, `secretReaction` ('clippy' typed), Konami planned as a SEPARATE buffer (never merge with the 'clippy' one).

## Playful pack plan (2026-09-05, not yet implemented)

`docs/superpowers/plans/2026-09-05-clippy-playful.md` — 8 tasks, TDD format: visits greeting (persist `dlgrv.assistant.visits[.date]`, morning <12:00, milestones 5/10/25 as separate tip ids `visit_5/10/25` — not `variants[]`), gaze (LookLeft/Right/Up/Down, 240px radius, 1.5s throttle, balloon-visible guard), tour (walk `.app-icon` icons, speak per step with `hold=true`, `TOUR_LINES` keyed by app NAME = `img.app-icon__img` alt), catch-me (flee radius 60px, 600ms cooldown vs `moveTo` queue flood, 3 catches → win, roam paused via module-level `isCatchMeOn()`), Konami (↑↑↓↓←→←→BA, 6s `animate()` chaos, once per load), tips.ts split, wiring, e2e.

Key conflict-handling decisions in the plan: `moveTo` enqueues — every motion feature needs a cooldown/cancel story (cooling flag, tour cancel-handle, roam pause); gaze skips while a `.clippy-balloon` is visible.
