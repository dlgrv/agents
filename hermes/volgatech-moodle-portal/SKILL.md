---
name: volgatech-moodle-portal
description: Use when working with the VolgaTech Moodle portal.
---

# VolgaTech Moodle portal (elearning.volgatech.net)

Login in the ISOLATED browser only (use_real_profile off — host Chrome locks the profile). Creds are in the vault bound to this origin: type the identifier with fill_input, then browser_vault_fill. Login form (Trusted.ID at auth.volgatech.net): `#inputUsername` / `#inputPassword`, submit button text «ВОЙТИ» — the vault fills only the password; VERIFY BOTH FIELD LENGTHS before submitting (the SPA re-renders can leave the username empty even after a successful vault fill — check `value.length` on both inputs, refill the empty one, then click «Войти»). Courses: `/course/view.php?id=<id>`; a submission editor: `/mod/assign/view.php?id=<cmid>&action=editsubmission`.

## Replace an existing submission (filemanager)
Deleting + re-uploading is the only way to swap files; Moodle keeps no in-place rename.
1. Open the assignment's `editsubmission` URL.
2. Delete each old file: click the file row inside `.filemanager` → a «Редактировать …» dialogue opens → click its «Удалить» button → confirm «OK». Sleep ~3 s between steps; `.filemanager` innerText is the source of truth (empty list = «Для загрузки файлов перетащите их сюда»).
3. Upload: click `.fp-btn-add` → `cdp('DOM.getDocument', depth=-1)` → `cdp('DOM.querySelector', selector="input[name='repo_upload_file']")` → `cdp('DOM.setFileInputFiles', files=[path], nodeId=…)` → click `.fp-upload-btn`. Wait ~5 s; uploaded names appear in `.filemanager` innerText. One file per picker pass.
4. Save with the «Сохранить» button in `#region-main`.
5. Verify by reading back the «Состояние ответа» block: new filenames + fresh timestamp + «Ответы для оценки».

Pitfall: match file rows by innerText over `.fp-file, .fp-filename, span` — `.fp-name` elements are empty in this theme, so a selector on them silently finds nothing.
Pitfall: a fresh upload can take ~5 s to register; checking `.filemanager` immediately after `.fp-upload-btn` looks like a failed upload.

## Visit all courses (register lastaccess)
Teachers see «последний доступ к курсу» per student; empty = never visited. A real page load of `/course/view.php?id=<id>` (~3 s dwell) is what writes lastaccess and the course logs — background fetches of the page do not.
1. Get the course list via the ajax service from any logged-in Moodle page: `fetch('/lib/ajax/service.php?sesskey=' + M.cfg.sesskey + '&info=...', POST)` with methodname `core_course_get_enrolled_courses_by_timeline_classification`, args `{offset:0, limit:200, classification:'all'}` — one call returns all enrolled courses.
2. `goto_url` each `viewurl`, wait ~3 s, confirm the tab title starts with «Курс:» (proof the visit was served, not a redirect loop).
3. This Moodle build does NOT return lastaccess in the course objects, so don't treat a missing field as failure — the page titles are the source of truth.
Pitfall: the OAuth redirect can re-present the SAME Trusted.ID form after the first «ВОЙТИ» — check `document.querySelector('#inputUsername')` and, if present, fill the identifier + vault-fill + submit a second time. After submitting, poll `page_info()` until the URL contains `elearning` (up to ~30 s); a single `wait_for_load()` may return while still on auth.volgatech.net.
Pitfall: if the browser daemon was restarted mid-session, the Moodle session dies with it — re-login before assuming anything about course state.

## When elearning won't load from the agent browser
The isolated browser inherits the Mac's proxy env (Clash on 127.0.0.1:17891); volgatech routes through a dead clash node and every HTTPS request hangs (proof: `curl --noproxy '*' https://elearning.volgatech.net/` returns 200). Fix WITHOUT touching Clash (user's hard rule): launch a dedicated headless Chrome for Testing with the proxy env vars unset (`env -u HTTP_PROXY -u HTTPS_PROXY ... chrome --headless=new --remote-debugging-port=9223 --user-data-dir=/tmp/agent-browser-manual-profile`), then `hermes config set browser.cdp_url http://127.0.0.1:9223` and pkill browser_harness.daemon — it respawns onto that Chrome. Configure Hermes only via `hermes config set`, never by editing config.yaml (a stray indent breaks the live gateway). Restore with `hermes config set browser.cdp_url ''` afterwards.

## Portal quirks for scripted access
- **`core_course_get_contents` is disabled on this portal** («Веб-служба недоступна») — enumerate a course's modules by parsing the `/course/view.php?id=<id>` HTML: regex over `/mod/<type>/view.php?id=N` hrefs plus the nearest `instancename` text gives type/id/name for every module including the 10 assignments of a practice course.
- **Check assignment submissions via the page wording, not guesses**: `mod/assign/view.php?id=N` (full goto, not XHR — XHR GET of an assign URL returns the course shell) reports «Состояние ответа … Ни одной попытки» when nothing was submitted.
- **This harness's js() has no await_promise — run in-page API calls as synchronous XHR** (`x=new XMLHttpRequest(); x.open('POST',url,false); x.send(body); return x.responseText`), and build the JS expression by string concatenation, not an f-string — the JS braces collide with f-string syntax and throw.
- On a course page the plain ajax `core_course_get_enrolled_courses_by_timeline_classification` still works (see above) — only some WS methods are disabled; read the error body before assuming the whole ajax service is dead.

## Find a staff member's contacts (site volgatech.net, not Moodle)
Use this for «как связаться с преподавателем/сотрудником» asks.
- The official site is **www.volgatech.net** (ПГТУ «Волгатех», Йошкар-Ола). `volgatech.edu` does not resolve/open — don't burn time on it.
- **Fastest path is the telephone directory, one page with everyone**: `goto_url('https://www.volgatech.net/about_the_university/telephone_directory/')`, then loop `t.find("Фамилия", idx)` over `document.body.innerText` — every hit gives office, phone, and email. Go here FIRST; personal pages are often stale one-liners (a teacher listed as «АСПИРАНТ» years after defending).
- Corporate emails follow `Фамилия+Инициалы@volgatech.net` transliterated (Кислицын А.А. → KislitsinAA@volgatech.net) — once the directory confirms one address for a person, that pattern predicts whether a guessed second address is plausible, but never invent an address without a directory hit.
- Site search at `/search/?q=<url-encoded Cyrillic>` returns relevance-sorted hits with breadcrumb paths and «Изменен» dates — use it to find a person's staff-page id and news mentions (titles, roles, dissertation), which help write a letter that addresses them correctly.
- A teacher may hold an admin post (отдел/департамент) outside their faculty — their directory entry can sit under that unit, not under кафедра. Grab BOTH blocks: the personal entry (direct phone/email) and the кафедра entry (общий email, завкафедрой) as fallback contact routes.
- js() returns a Python str: use Python slicing/`.find`, not JS methods like `.slice` (AttributeError).

## File naming formula
`{Предмет-аббревиатура}_{Тип+№}_{Группа}_{Фамилия_И.О.}.{ext}` → e.g. `ОИИ_ЛР1_ИТС-41з_Долгирев_ЛМ.docx`. Canonical spec with the full rule list: `university/именование-файлов.md`. When renaming, rename BOTH the local files and the portal submission (old filenames linger on the platform otherwise).

## Peer-copy workflow (копии работ для одногруппниц)
Group lab works are declared identical by the instructor, so the deliverable is a renamed copy of the same executed work — not new content.
1. Create `university/<Предмет>/<ЛРn>_<Фамилия>_И.О./`.
2. docx: patch the title page — ФИО and «Выполнил(а) студент(ка) гр. ИТС-41(з)» — via run-level python-docx edits (keep formatting).
3. ipynb: re-execute for fresh outputs/execution counts (resolve the venv's jupyter explicitly; bare `jupyter` may be off PATH), don't ship stale outputs under a new name.
4. Name all files by the formula. Zip only when asked; show the result in Finder.

## Identify a course / place its files
1. Open `/course/view.php?id=<id>` (login above) and read `#region-main` innerText — section names (lecture titles, lab topics) identify the course.
2. Before creating any folder, search `university/` for the course title: course folders are named `<Название курса> (<Фамилия И.О. препода>)` and usually already exist.
3. To attribute unknown lab files (e.g. from Downloads) to a course: `json.load` each notebook and read the first ~8 cells' source, then match titles/topics against the Moodle course page's lab list — exact title+topic match identifies the course; don't create a new folder when attribution lands on an existing one, just offer to move the files in.

## Print jobs
Print-ready files live in `university/на печать/` with formula names. Determine sheet format from the PDF mediabox (`mm = pt*25.4/72`: А2=594×420, А3=420×297, А4=210×297) and report the per-format print count — never trust the format in a filename.