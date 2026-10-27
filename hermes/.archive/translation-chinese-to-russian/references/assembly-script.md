# Assembly and Verification Script

Assembles translated units with byte-faithful source injection and structural validation.

## Usage

```bash
python3 tools/assemble.py <NN> /tmp/workdir <output.md>
```

- `NN`: Chapter number
- `/tmp/workdir`: Directory with units and blocks.json
- `<output.md`: Final assembled chapter

## Checks Performed

- Unit count matches original chapter
- Tag count matches blocks.json
- Source lines match byte-for-byte
- Chinese characters only allowed in sources/tags/status lines
- Structural integrity (blank lines, headers preserved)

## Exit Codes

- 0: Success
- Non-zero: Fail (missing units, mismatched counts, structural issues)

## Key Features

- Injects sources/tags from blocks.json at placeholder positions
- Preserves all original formatting and punctuation
- Warns about untranslated lines but doesn't fail for them
- Validates structural match against original chapter
