# Local assets & layout-shift audit (dlgrv desktop)

The user is sensitive to **content jumping on load / reset** («контент внутри
блока all равно скачет»). This is a layout-shift (CLS) problem. Capture the
audit + fix recipe used to stabilize the About Me window.

## Symptom
On reset, About Me content first renders small/short, then suddenly grows
(hero lower, avatar lower, title shifts down ~16–32px).

## Audit recipe (Playwright)

Write a throwaway spec that samples geometry over time while DELAYING assets:

```ts
test('layout shift audit', async ({ page }) => {
  await page.route('**/*.{woff2,ttf,png,gif,css}', async (route) => {
    const u = route.request().url();
    if (u.includes('/src/')) return route.continue();   // keep app code fast
    await new Promise((r) => setTimeout(r, 1000));        // slow assets
    await route.continue();
  });
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'domcontentloaded' });
  for (const ms of [0, 100, 300, 700, 1200, 2000]) {
    await page.waitForTimeout(ms);
    const data = await page.evaluate(() => {
      const rect = (s) => {
        const e = document.querySelector(s);
        if (!e) return null;
        const r = e.getBoundingClientRect();
        return { y: +r.y.toFixed(1), h: +r.height.toFixed(1), w: +r.width.toFixed(1) };
      };
      const ava = document.querySelector('.about-ava');
      return {
        title: rect('.about-title'), hero: rect('.about-hero'), ava: rect('.about-ava'),
        avaComplete: ava?.complete,
        fonts: document.fonts?.status,
        archivo: document.fonts?.check?.('16px Archivo'),
      };
    });
    console.log('SAMPLE ' + JSON.stringify(data));
  }
});
```

Read the numbers: if `hero.y` / `ava.y` change between samples → a child without
reserved size is loading. If `title.w` changes after `fonts: loaded` → webfont
metric swap.

## Real causes found (this session)

1. **Rocket GIF from `melonking.net` with `height:auto`.**
   The About hero has two `img.about-rocket` (42px wide, `height:auto`). Until the
   GIF arrived, hero was shorter; on arrival it grew → everything below shifted.
   Fix: download the GIF locally, set explicit size:
   ```css
   .window-content--about .about-rocket {
     width: 42px;
     height: 84px;          /* real GIF ratio 120x240 = 1:2 */
     flex: 0 0 auto;
     image-rendering: pixelated;
   }
   ```
   And `rocketL.src = '/about/rocket.gif'` (copy from melonking.net into
   `public/about/`). Measured result: `hero.y` stable at 143, `ava.y` stable at 245
   from t0.

2. **Google Fonts `display=swap` in `index.html`.**
   `title.w` changed 311 → 327 when Archivo loaded. Fix: remove the
   `fonts.googleapis.com` `<link>`, download latin+cyrillic woff2 subsets to
   `public/fonts/archivo/` and `public/fonts/inter-tight/`, register via `@font-face`
   in `fonts.css`. (Download recipe: hit the css2 endpoint with a Chrome UA, grep
   the `https://fonts.gstatic.com/...woff2` URLs, fetch latin + the cyrillic block
   containing `U+0400-045F`.)

3. **Window open animation `transform: scale(.92)`.**
   `.mac-window { animation: window-in }` with `from { transform: scale(.92) }`
   made every window "grow" on open. Fix: keep only `from { opacity: 0 }` — no
   scale. Confirmed `getComputedStyle(win).transform === 'none'` at all samples.

## Rule of thumb
Any remote image/gif in a fixed layout must be (a) localized and (b) given explicit
`width`+`height` (or `aspect-ratio`) so it reserves space before load. All webfonts
must be local. After any such change, re-run the audit and confirm geometry is
identical across all samples.
