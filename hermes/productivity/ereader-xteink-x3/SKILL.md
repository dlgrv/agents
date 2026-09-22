---
name: ereader-xteink-x3
description: "Use for Xteink X3 e-reader settings, library, or book recs."
version: 0.1.0
---

# E-reader: Xteink X3 (crosspoint firmware)

The device exposes a web UI on the LAN at `http://192.168.31.115` (`/settings`, `/files`). Work against it with `curl` from the terminal.

## Procedure — settings audit / change

1. Cloud browser backends cannot reach LAN IPs — go straight to `curl` via terminal, never via browser tools.
2. The settings page loads values through a JSON API (page HTML is gzipped; use `curl --compressed`). Find the API endpoint the page itself calls, read current values first, build the audit table from that snapshot.
3. Propose changes as a table (current → recommended, with a reason tied to the device) and WAIT for the user's OK before writing anything.
4. Apply each change via the API, then VERIFY by reading the settings back from the device and show the post-write values — a successful write call is not proof the value stuck.
5. Enumerate choice values before setting them (e.g. progress-bar modes turned out to be 1=Chapter, not Book): read the option list from the API/UI first, then apply the value the user actually meant.

## Device profile (do not re-derive)

- X3 is tiny: narrow screen, buttons only, no touch. Every pixel counts — do NOT recommend larger margins (Screen Margin stays 5) or ghosting-prone refresh settings (Refresh Frequency 5 pages).
- User's standing config choices: Hyphenation On, Quick Resume On, Sleep Timeout 5 min, UI Theme Lyra (no battery %), Progress Bar = Book, Refresh Frequency 5 pages. Do not revert these without an explicit ask — the user once asked to revert a theme change.

## Book recommendations

- Recommend in Russian first: before recommending any book, check a Russian edition exists (piter.com for dev books, litres.ru generally) and link where to legally get the epub. This session's pattern: user asked 'is there a Russian translation?' — always check up front.
- Taste: Japanese literary prose (Yoshimoto, Murakami) for leisure; ML/LLM learning track for study (Ng's course is the anchor); narrative popular science in the Mukherjee style; science non-fiction broadly (Саган, Хокинг, Харари tier). Goodreads ratings/popularity are welcome in recommendation tables.
- Deliver epubs to the device via the web UI files interface at `http://192.168.31.115/files`.

## Sourcing epubs

- Never fetch copyrighted books from pirate libraries (flibusta and mirrors), even when the user says they already bought the book — purchase does not make a pirate copy legal. State the line once, then pivot straight to legal routes; do not relitigate it.
- Legal routes in order: (1) user checks Литрес → «Мои книги» for the official DRM-free epub/fb2 download many editions offer; (2) user supplies files → upload all to the device via `/files` in one pass; (3) legal free sources: rusneb.ru (НЭБ), free library subscriptions, genuinely free books (e.g. Nielsen's neuralnetworksanddeeplearning.com).
- Do NOT recommend «Всенаука»/«Дигитека» as a free source — the project closed and its rights expired; the domain is dead.
