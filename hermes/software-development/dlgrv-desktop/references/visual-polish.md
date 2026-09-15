# dlgrv visual-polish techniques (session-learned)

## Floating brand in "the air" (no topbar)

The user wants the `dlgrv` title to type out (inteko-style) but **floating over the
wallpaper, with NO topbar/menu-bar**. Never re-introduce a menu bar to host it.

Implementation: `src/shared/ui/floating-brand.ts` → returns a `div.floating-brand`
containing `.floating-brand__nick` + `.floating-brand__caret`. Mounted in
`app/index.ts` via `root.append(..., brand)` (NOT inside desktop grid).

CSS (`src/app/app.css`):
```css
.floating-brand { position: fixed; z-index: 900; pointer-events: none;       /* clicks pass through */
  font-family: 'Inter Tight', system-ui, sans-serif; font-weight: 700;
  font-size: clamp(20px,3vw,34px); color: var(--foreground);
  text-shadow: 0 1px 14px rgba(0,0,0,.55); }
.floating-brand__caret { width:.52em; height:.85em; margin-left:.16em; background:currentColor;
  animation: floating-caret-blink 1.1s step-end infinite; transition: opacity .35s ease; }
.floating-brand__caret.is-done { opacity: 0; }   /* removed by JS 650ms after full word */
/* positions — pick ONE by adding the modifier class: */
.floating-brand--bl { left: 40px; bottom: 36px; }   /* bottom-left (default, chosen) */
.floating-brand--tc { left: 50%; top: 36px; transform: translateX(-50%); } /* center-top */
.floating-brand--br { right: 180px; bottom: 36px; } /* right-bottom, left of Reset btn */
```
Switch position by editing the single `brand.classList.add('floating-brand--bl')` line
in `app/index.ts`. The three variants were all built so the user can pick; do not delete
the unused modifiers.

## Typing animation timing — taken 1:1 from inteko (boylifein.eu)

Dissected their minified SvelteKit bundle to copy the exact feel. Method:
`curl` the page HTML → find `_app/immutable/` chunk/node URLs → download
`chunks/*.js`, `nodes/2.*.js`, `assets/*.css` → grep for the animation logic.
The hero types the tag char-by-char:
```js
let e = 0;
const tick = () => {
  nick.textContent = TAG.slice(0, ++e);
  timer = e < TAG.length ? setTimeout(tick, 110)        // 110ms per char
                          : setTimeout(() => hideCaret(), 650);  // caret lingers 650ms
};
timer = setTimeout(tick, 250);                          // start 250ms after load
```
Caret: block `.5em×.85em`, blink `step-end` 1.1s; honor `prefers-reduced-motion`
(no blink). Copy these timings exactly when replicating "typewriter" effects.

## Win95 window title-bar buttons (draw with CSS, NOT unicode)

The maximize button was first a unicode `□` rendered by Tahoma — it came out as a tiny
broken square. Fix: draw all three icons with CSS pseudo-elements:
- **close (X)**: two crossed diagonal `linear-gradient`s.
- **minimize (_)**: a short bar pinned to the lower-left of the button; on our larger 24px
  buttons center it for balance; strict Win98 keeps it lower-left.
- **maximize (□)**: a rectangle with a thick top border (`border-top: 2px solid`) centered.
- **Authentic Win98 ORDER**: `[ _ ] [ □ ]  [ X ]` — minimize, maximize, THEN close on the
  right with an enlarged gap before it (`margin-left` on the close button). macOS-style
  `[X][_][□]` order is wrong for Win95.
- Buttons are 21×17px (orig ~16×14) with double bevel (`border` white/gray top-left,
  black/dark-gray bottom-right).
- Relay classes: `.mac-window--win95 .traffic-lights__btn::after { content:none }` to kill
  the old unicode glyph before adding CSS icons.

## Galaxy wallpaper: monochrome + film grain

- **Monochrome**: in `src/shared/ui/galaxy/generate.ts`, `createColorGrade` has a
  `GALAXY_MONOCHROME` flag; when true it returns `[lum, lum, lum]` after boosting luminance
  ×1.12 (compensates for lost "color energy" so the core stays bright). Set `false` to revert.
- **Film grain over the galaxy** (separates background from icons without darkening):
  `.desktop__wallpaper::after { content:''; position:absolute; inset:-20px; pointer-events:none;
    background-image: url("data:image/svg+xml,...feTurbulence baseFrequency=1.6 numOctaves=2...");
    background-size:120px 120px; filter: blur(.6px); mix-blend-mode: overlay; opacity:.34; }`
  knobs: `baseFrequency` (smaller = coarser), `background-size` (tile), `opacity` (.10-.25
  subtle, .34 stronger), `blur` (the "haze/diffuse" feel). The `inset:-20px` hides blur
  bleed at screen edges.

## Dino iframe keyboard-focus relay (non-obvious bug)

The Safari window embeds the real dino via `<iframe src="/dino/index.html">`. Space/arrows
are listened on the iframe's `document` — but on first open the iframe has no focus, so
Space does nothing until the user clicks inside. Fix (two layers):

1. **Parent to iframe relay** (`src/features/open-window/content.ts`): on `window`
   `keydown`/`keyup`, if `document.activeElement !== iframe`, `postMessage` the event into
   the iframe. Stop relaying once focus is inside (avoids double-jumps).
2. **iframe listener** (`public/dino/index.js`): `window.addEventListener('message', ...)`
   builds a fake event and feeds `this.handleEvent(fake)` — but the fake MUST set
   `target: document` (not `undefined`).

**The gotcha:** `Runner.onKeyDown` guards `if (e.target != this.detailsButton)`.
In JS `undefined == null` is `true`, so with `target: undefined` and `detailsButton: null`,
the guard evaluates `undefined != null` → **false**, and the handler silently ignores the
keypress. Setting `target: document` fixes it. Always give a relayed fake-event a real
`target`/`currentTarget`.

Also: the idle dino was drawn at `xPos=0` by the Trex constructor BEFORE our pin could run.
Pin position inside the **Trex constructor** (`this.xPos = Trex.config.START_X_POS`) before
`this.init()`, and enable arcade-mode in `init()` (not on start) so idle and running frames
share identical transform — otherwise the dino "jumps" on first Space.
