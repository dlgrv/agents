# JS-bundle design extraction — worked example

Real site: `https://www.probablynothing.xyz/` (Astro + React islands; the visible
UI is client-rendered, so raw HTML has almost no useful classes). Goal this session:
copy (1) the exact font used for the article title "the story of telegram's new
visual wave", and (2) the exact "Dive in" button (`.aqua-link`) styling.

## What failed first

Grepping the linked CSS (`_astro/seo.*.css`) returned only base tokens. The
article-title font and the button gradient were NOT in that file. They live in
the **compiled JS bundle** as template strings.

## Recovery steps (exact commands that worked)

```bash
# 1. raw HTML
curl -sL https://www.probablynothing.xyz/ -o /tmp/pn.html
# 2. find JS bundle names in the HTML
grep -oE '/_astro/[a-zA-Z0-9_.-]+\.js' /tmp/pn.html
# 3. fetch the app bundle (one of the listed _astro/*.js)
curl -sL https://www.probablynothing.xyz/_astro/HelloWorld.BOOpDpFy.js -o /tmp/pn-app.js
```

### Font mapping (article title)

```bash
grep -oE '[a-z-]*title[^{]*\{[^}]*font-family[^}]*\}' /tmp/pn-app.js | sort -u
```

Result (real):
```
.tg-article-title => Playfair Display,serif
.tg-article-subtitle => Golos Text,sans-serif
.tg-article-description => Golos Text,sans-serif
.tg-article-quote => Playfair Display,serif
html,body => Archivo,sans-serif
.texts => Archivo
.folder-window-title--blured => Archivo,sans-serif
.font-system => var(--font-system)        # = Instrument Serif on that site
```

So the headline font is **Playfair Display** (NOT Instrument Serif — a plausible
guess that was wrong; the bundle proved it). Body/UI font is **Archivo**.

### "Dive in" button (.aqua-link) — full CSS recovered from a template string

```bash
grep -oE '\.aqua-link \{[^}]*\}' /tmp/pn-app.js
```

Recovered literal values (copy verbatim for a 1:1 pill):
```css
.aqua-link {
  height: 44px;
  position: relative;
  display: block;
  padding: 0 24px;
  border-radius: 70px;
  background: linear-gradient(0deg, #F5F5F5 -15.69%, #B5B5B5 127.45%);
  box-shadow: 0 4px 8px 0 rgba(62, 62, 62, 0.19);
  display: flex; flex-flow: column nowrap;
  align-items: center; justify-content: center; width: fit-content;
}
.aqua-link__before {  /* top highlight */
  position: absolute; top: 1px; height: 23px; left: 12px; right: 12px;
  border-radius: 120px;
  background: linear-gradient(180deg, #FFF 0%, rgba(255,255,255,0) 79.41%);
  pointer-events: none;
}
.aqua-link__after {   /* bottom glow */
  position: absolute; bottom: 1px; height: 12px; left: 12px; right: 12px;
  border-radius: 70px; background: #EDF8FF; filter: blur(8.5px);
  pointer-events: none;
}
.aqua-link__text {
  position: relative; z-index: 1; color: #2A2A2A;
  font-size: 16px; font-weight: 500; line-height: 32px;
}
```
The component renderer was `function ne({href,text,...})` producing
`<a class="aqua-link" href={t} target="_blank" rel="noopener noreferrer">`.

### Sphere asset

The "rotating sphere" on load is NOT a 3D engine — it's a pre-rendered video:
```bash
grep -oE 'emoji-sphere[a-zA-Z0-9_./-]*' /tmp/pn-app.js
# → https://not.ams3.cdn.digitaloceanspaces.com/portal/not_collective/emoji-sphere.mp4
```
(Reproduced locally with a CSS-3D emoji sphere instead of shipping a video.)

## Local-font lesson (separate failure mode)

Even with the right font name in `<link>`, the font may not load in the user's
browser/preview while it DOES load on the reference site (Google Fonts blocked
for the user). Fix: download the woff2 and serve it locally via `@font-face`,
then verify with `document.fonts.check('700 80px "Playfair Display"')` in a test
that **blocks** `fonts.googleapis.com`/`fonts.gstatic.com` to prove it works
offline. See the `entities/lang` + `public/fonts` pattern used this session.

## Checklist before declaring "value not found"

1. grep the linked `.css`  → not found?
2. grep the JS bundle (`/_astro/*.js`) for the class name AND `font-family:`/`linear-gradient`  → usually here.
3. grep the bundle for asset URLs (`mp4`/`woff2`/`png`).
4. only then conclude it doesn't exist / approximate.
