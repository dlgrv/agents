# Build pages procedure (HTLB ES translation site)

## Rule

When updating site parser regexes (e.g. adding Spanish field labels to `index.html`), **always run `python3 tools/build_pages.py`** after modifying `index.html`. This copies the fixed parser to `es/index.html`, `en/index.html`, `ru/index.html`, `zh/index.html`, and `v1/*`. Without this step, users see old parser in `/es/` and translation cards display empty fields.

## Why

The site generator (`build_pages.py`) copies the main `index.html` template to language-specific directories (`es/`, `en/`, etc.) and the `v1/` legacy path. If you only update the root `index.html`, the language subdirectories keep the old parser, causing empty fields in `/es/` despite the parser fix being committed.

## Procedure

```bash
# After updating index.html with new regexes:
python3 tools/build_pages.py
# Verify:
grep -c "En términos sencillos" es/index.html  # must be >0
grep -c "Costo" es/index.html                 # must be >0
# Commit all regenerated pages:
git add es/ en/ ru/ zh/ v1/
git commit -m "fix: regenerate language pages with updated parser"
```

## Pitfall

Never commit parser fixes in `index.html` without regenerating language pages — this leaves `/es/` with old regexes and empty translation cards, even though the fix is committed and merged.
