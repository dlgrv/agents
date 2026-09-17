# Chapter Splitter for Large Documents

Splits large chapters (30–42 Kbyte) into 1–2 Kbyte units for LLM processing.
Extracts sources and tags byte-for-byte to prevent accidental translation.

## Usage

```bash
cd /path/to/repo
python3 tools/make_digest.py <NN> /tmp/workdir
```

- `NN`: Chapter number (e.g., 16)
- `/tmp/workdir`: Output directory for units and blocks.json

## Output

- `units/NN.md`: Split chapter with `§TAG§`/`§SRC§` placeholders
- `blocks.json`: Byte-faithful sources and tags for later injection

## Key Features

- Replaces source lines with `§SRC§` placeholders
- Replaces tag lines with `§TAG§` placeholders
- Preserves all formatting, punctuation, and byte-exact content
- Creates index.json for watchdog cross-chapter validation
