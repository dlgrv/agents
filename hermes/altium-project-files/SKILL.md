---
name: altium-project-files
description: Use when bulk-editing Altium project files from scripts.
version: 1.0.0
author: hermes-mac
license: MIT
metadata:
  hermes:
    tags: [altium, university]
    related_skills: [parallels-desktop-ops, volgatech-moodle-portal]
---

# Altium project files: scripted edits and forensics

## When to Use
Load when the task involves bulk edits inside Altium Designer project trees (.PrjPcb/.SchDoc/.PcbDoc/.PCBDwf/.LibPkg) done from the mac side — authorship renames, stale-path cleanup, reference fixing — e.g. inherited classmate projects that must carry the USER's ФИО everywhere.

NEVER hand-edit these files while Altium has the project open — the app holds locks and rewrites every file on save; close it first (check `tasklist` for X2.EXE via prlctl exec).

## File format map (what encoding lives where)
- `.PrjPcb`, `.LibPkg` — ASCII/UTF-8 INI text (sections `[Design]`, `[DocumentN]`, `[GeneratedDocumentN]`, `[OutputGroupN]`, `\r\n` line endings).
- `.SchDoc`, `.SchLib` — ASCII record streams; each parameter is DUPLICATED as `%UTF8%Text=<utf8>` and `Text=<cp1251>` — a rename must hit both copies.
- `.PcbDoc` — binary OLE; embedded strings in cp1251 (e.g. stored absolute source paths).
- `.PCBDwf` (Draftsman drawings) — proprietary container, NOT a zip (starts `01 80 80 40`); plain UTF-8 XML fragments inside, other segments compressed.
- Always scan with ALL of utf-8, cp1251, utf-16-le, utf-16-be before concluding "clean".

## Renaming a string (authorship) — equal-length byte replacement
1. Backup first: `ditto -c -k <folder> <folder>_БЭКАП_<date>.zip` (a 170-file project ≈ 14 MB).
2. Assert the old and new strings have IDENTICAL byte length in every encoding (utf-8: Cyrillic counts double; assert programmatically). Russian ФИО of the same character count qualifies — e.g. «Якурнова И.С.» (23/13/26 bytes in utf-8/cp1251/utf-16-le) ↔ «Долгирев Л.М.». Equal length is what makes in-place replacement safe: record offsets and length fields stay untouched, so binary containers don't corrupt.
3. If variants survive (e.g. the form without the trailing dot inside compressed segments), repeat with the shorter stem — Cyrillic stems of equal char count are still equal-length. Unmatched occurrences are inside compressed streams — you cannot and need not touch them.
4. Replace across ALL files, then verify: rescan in all encodings = 0 hits, AND every replaced file has the exact same byte size as before (any drift means a length field was corrupted — restore from backup).

## Cleaning an inherited project (built on a classmate's files)
- `.PrjPcb` keeps the predecessor's fingerprints: `[GeneratedDocumentN]` entries pointing at an output folder named after them, plus absolute paths like `C:\Windows.old\Users\...\<Their Name>\...` inside `ConfigurationN_Item` records (dozens per project). Strip the dead absolute prefix so the path becomes relative to the project root.
- If you rename the real outputs folder on disk, update the `.PrjPcb` references in the same operation — one without the other produces «could not be found. It remains in the project but has been marked as missing» warnings.
- Missing-output warnings for a file that never existed (e.g. Pick Place): delete that whole `[GeneratedDocumentN]` section and RENUMBER the remaining sections to contiguous N (Altium reads them sequentially).
- File renames (e.g. «ЛР2 <Фамилия>..SchLib» → clean name) must be paired with every reference: `.LibPkg` `[DocumentN] DocumentPath=` entries, `.PrjPcb` paths, and stale `LibraryPath=` mentions inside `.SchDoc`.

## Verification gate
1. Rescan the tree for the old string in all 4 encodings → 0.
2. Parse every `DocumentPath=` in the .PrjPcb and confirm the file exists. Normalize backslashes to forward slashes when checking on macOS — Windows-style separators make every check falsely fail otherwise.
3. Byte sizes of purely-replaced files unchanged.
4. FINAL GATE (nothing else proves Altium parses it): reopen the project in Altium and check the Messages panel is clean. Do not report success after step 3 alone.

## Virtual folders in the Projects panel
The sidebar folder INI format inside .PrjPcb is undocumented and NOT guessable — never hand-write folder sections. Learn it empirically: have the user create ONE folder in Altium (ПКМ по проекту → Add New → Project Folder) and Save Project, then diff the .PrjPcb before/after and replicate the discovered structure. Note the Projects panel is flat regardless of physical disk folders — grouping requires these virtual folders, and files must first exist as `[DocumentN]` entries to be grouped at all.

## Related workflows
- Copying the project into the Windows VM: parallels-desktop-ops skill (staging via shared folder + robocopy /MIR via UNC).
- docx/ipynb peer-copy renames: volgatech-moodle-portal skill (peer-copy workflow).
