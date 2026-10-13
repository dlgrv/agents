---
name: volgatech-moodle-portal
description: Use when working with the VolgaTech Moodle portal.
---

# VolgaTech Moodle portal (elearning.volgatech.net)

Login in the ISOLATED browser only (use_real_profile off — host Chrome locks the profile). Creds are in the vault bound to this origin: type the identifier with fill_input, then browser_vault_fill. Courses: `/course/view.php?id=<id>`; a submission editor: `/mod/assign/view.php?id=<cmid>&action=editsubmission`.

## Replace an existing submission (filemanager)
Deleting + re-uploading is the only way to swap files; Moodle keeps no in-place rename.
1. Open the assignment's `editsubmission` URL.
2. Delete each old file: click the file row inside `.filemanager` → a «Редактировать …» dialogue opens → click its «Удалить» button → confirm «OK». Sleep ~3 s between steps; `.filemanager` innerText is the source of truth (empty list = «Для загрузки файлов перетащите их сюда»).
3. Upload: click `.fp-btn-add` → `cdp('DOM.getDocument', depth=-1)` → `cdp('DOM.querySelector', selector="input[name='repo_upload_file']")` → `cdp('DOM.setFileInputFiles', files=[path], nodeId=…)` → click `.fp-upload-btn`. Wait ~5 s; uploaded names appear in `.filemanager` innerText. One file per picker pass.
4. Save with the «Сохранить» button in `#region-main`.
5. Verify by reading back the «Состояние ответа» block: new filenames + fresh timestamp + «Ответы для оценки».

Pitfall: match file rows by innerText over `.fp-file, .fp-filename, span` — `.fp-name` elements are empty in this theme, so a selector on them silently finds nothing.
Pitfall: a fresh upload can take ~5 s to register; checking `.filemanager` immediately after `.fp-upload-btn` looks like a failed upload.

## File naming formula
`{Предмет-аббревиатура}_{Тип+№}_{Группа}_{Фамилия_И.О.}.{ext}` → e.g. `ОИИ_ЛР1_ИТС-41з_Долгирев_ЛМ.docx`. Canonical spec with the full rule list: `university/именование-файлов.md`. When renaming, rename BOTH the local files and the portal submission (old filenames linger on the platform otherwise).

## Peer-copy workflow (копии работ для одногруппниц)
Group lab works are declared identical by the instructor, so the deliverable is a renamed copy of the same executed work — not new content.
1. Create `university/<Предмет>/<ЛРn>_<Фамилия>_И.О./`.
2. docx: patch the title page — ФИО and «Выполнил(а) студент(ка) гр. ИТС-41(з)» — via run-level python-docx edits (keep formatting).
3. ipynb: re-execute for fresh outputs/execution counts (resolve the venv's jupyter explicitly; bare `jupyter` may be off PATH), don't ship stale outputs under a new name.
4. Name all files by the formula. Zip only when asked; show the result in Finder.

## Print jobs
Print-ready files live in `university/на печать/` with formula names. Determine sheet format from the PDF mediabox (`mm = pt*25.4/72`: А2=594×420, А3=420×297, А4=210×297) and report the per-format print count — never trust the format in a filename.