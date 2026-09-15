---
name: web-desktop-windows
description: Use when building/testing sites mimicking macOS/Win95 chrome
version: 1.0.0
author: Hermes Agent (curator)
metadata:
  hermes:
    tags: [frontend, css, playwright, drag-and-drop, ui]
---

# Web Desktop Windows (macOS / Win95 style sites)

Patterns and hard-won pitfalls for building websites that mimic a desktop OS:
draggable/resizable windows, traffic lights, desktop icons, emoji spheres.
Born from a macOS+Win95 business-card site (Vite + TS strict, FSD layers,
no framework), but the techniques are framework-agnostic DOM code.

## When to use
- Building/refactoring draggable or resizable windows, desktop-icon layouts,
  OS-chrome metaphors (titlebars, traffic lights) on a website.
- Debugging "window doesn't move / teleports back / snaps to origin".
- Writing Playwright tests for such UIs (they have unique failure modes).
- Copying exact visual styles from a reference site (fonts, gradients, chrome sizes).

## The core drag pattern — DO NOT improvise

Key invariants:

1. **Accumulate deltas.** `dx`/`dy` from each pointermove are INCREMENTS:
   ```ts
   pos.x += dx;                     // ✅ current position
   el.style.left = `${pos.x}px`;
   ```
   Never `el.style.left = startPos.x + dx` with a start captured once — every frame
   recomputes origin + last tiny step, so the window barely moves or appears to snap
   back. This exact bug occurred three times before being measured properly.
2. **No `setPointerCapture`.** Attach `pointermove`/`pointerup`/`pointercancel`
   listeners to `document` for the duration of the gesture; remove on end.
   Embedded webviews deliver spurious `pointercancel` or fail to retarget captured
   events; document-level listeners work everywhere.
3. **Ignore `pointercancel` when `e.pointerType === 'mouse'`** — treat touch cancel
   honestly, mouse cancel as noise from system gesture interception.
4. **Resize = same pattern**: handler gets `(dw, dh)` increments applied to a size
   object with min-clamps (`Math.max(minW, w + dw)`); top-left corner must not move.
5. Capture drag-start offset ONCE in `onStart` (element rect minus offsetParent rect)
   into a per-window closure. Module-level shared `startX/startY` causes multi-window
   teleport bugs.

## Chrome sizing cheat-sheet
- macOS: titlebar **28px**, window radius 10px, traffic lights 12px ⌀ with 8px gap and
  ~13px left padding, title 13px semibold centered `rgba(0,0,0,.85)`; unfocused window
  grays its title. macOS does NOT change the cursor during titlebar drag.
- Win95: titlebar ~20px, blue gradient `#000080→#1084d0`, title left white bold 11px,
  buttons right (`— □ ✕`) gray `#C0C0C0` bevel, body `#C0C0C0`, radius 0, bevel borders
  (outer `#DFDFDF`/`#000`, inner `#FFF`/`#808080`).

## Playwright testing pitfalls — see references/playwright-testing.md
Overlay elements intercepting icon clicks; cascade-positioned windows needing settle
waits before measuring; ids containing spaces breaking attribute selectors; weak "it
moved" assertions passing while the drag is actually broken (assert final position ≈
cursor destination).

## Copying styles from a reference site — see references/reference-style-extraction.md
Recipe for pulling exact colors/sizes/fonts out of any production site (SSR HTML +
linked CSS + JS bundle grep) and serving fonts locally so they load even where
Google Fonts is blocked.

## Project conventions seen here (FSD, Vite+TS strict)
- Alias `@/* → src/*`; dependency direction `app → pages → widgets → features → entities → shared`.
- Window factory takes `{ id, title, width?, height?, theme? }`; theme classes like
  `.mac-window--win95` restyle one DOM structure instead of duplicating markup.
- Per-app content lives in a content renderer keyed by app id; i18n = dict object +
  `navigator.language` detection + localStorage persistence + listener-based re-render
  of open windows on language change.
