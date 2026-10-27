# Chapter Verification Workflow for Chinese-to-Russian Translation

## Purpose
Standardized verification and commit workflow for each translated chapter to ensure consistency and prevent pipeline interference.

## Verification Steps

### 1. Chapter Completion Check
```bash
# Verify file exists and has correct structure
ls book/ru/<chapter>-<slug>.md
head -5 book/ru/<chapter>-<slug>.md | grep -E '(Неофициальный перевод|К общему оглавлению|# [0-9]+\.)'
```

### 2. Structural Verification
```bash
# Item counts must match source
zh_items=$(grep -c '^### ' book/<chapter>-*.md)
ru_items=$(grep -c '^### ' book/ru/<chapter>-*.md)
echo "Items: ZH=$zh_items, RU=$ru_items"

# Tag-comment counts must match
zh_tags=$(grep -c '成本标签' book/<chapter>-*.md)
ru_tags=$(grep -c 'Затраты/Выгора/Риск' book/ru/<chapter>-*.md)
echo "Tags: ZH=$zh_tags, RU=$ru_tags"

# DOI counts must match
zh_doi=$(grep -c 'doi.org' book/<chapter>-*.md)
ru_doi=$(grep -c 'doi.org' book/ru/<chapter>-*.md)
echo "DOIs: ZH=$zh_doi, RU=$ru_doi"
```

### 3. Byte-Faithful Sources Check
```bash
# Source lines must be byte-identical after label translation
zsrc=$(grep '^- 来源：' book/<chapter>-*.md | sed 's/：/:/' | cut -d: -f2 | sort)
rsrc=$(grep '^- Источники:' book/ru/<chapter>-*.md | cut -d: -f2 | sort)
diff <(echo "$zsrc") <(echo "$rsrc") || echo "SOURCE MISMATCH"
```

### 4. CJK Character Check
```bash
# No Chinese characters outside allowed zones
han=$(grep -v '](book/' book/ru/<chapter>-*.md | grep -v '](docs/' | grep -v '（' | grep -v '《' | grep -c '[一-鿿]')
echo "Chinese chars outside zones: $han"
```

### 5. Numeric Verification
```bash
# Normalize and compare numbers
python3 -c "
import re
zh_nums = re.findall(r'\d+(?:\.\d+)?%?|[0-9,万]+%?', open('book/<chapter>-*.md').read())
ru_nums = re.findall(r'\d+(?:\.\d+)?%?|[0-9,万]+%?', open('book/ru/<chapter>-*.md').read())
zh_norm = [re.sub(r'[,.]', '', n).replace('万', '0000') for n in zh_nums]
ru_norm = [re.sub(r'[,.]', '', n).replace('万', '0000') for n in ru_nums]
print('Numeric match:', set(zh_norm) == set(ru_norm))
"
```

## Commit Workflow

### 1. Individual Chapter Commit
```bash
cd ~/github/HowToLiveBetter
git add book/ru/<chapter>-<slug>.md
git commit -m "translation(ru): chapter <chapter>"
```

### 2. Batch Commit for Related Changes
```bash
git add README.md TRANSLATION.md  # If updated
git commit -m "translation(ru): nav updates, review fixes, jargon cleanup"
```

### 3. Push to Fork
```bash
git push fork translation/ru
```

### 4. PR Update
```bash
# After push, comment in PR with progress
gh pr comment <PR-number> --repo eternity4719/HowToLiveBetter --body "
**Progress update:**
- Chapters completed: <list>
- Verification status: PASS/FAIL
- Commit hashes: <hashes>
- Next wave: <chapters>
"
```

## Error Handling

### Failed Verification
If any check fails:
1. Identify specific mismatch (items/tags/DOIs/sources/numeric/CJK)
2. Check subagent transcript for debugging
3. If subagent failed, recover from `~/.hermes/cache/delegation/live/`
4. Retry with corrected instructions or reassign

### Pipeline Interference
If background pipeline overwrites work:
1. Stop background process: `sudo systemctl stop htlb-pipeline`
2. Restore from git: `git checkout HEAD -- book/ru/`
3. Verify current conventions are applied
4. Restart translation with pipeline disabled

## Wave Completion Summary
After each 5-chapter wave:
```bash
echo "Wave <wave-number> summary:"
echo "- Completed: <chapters>"
echo "- Failed: <chapters> (if any)"
echo "- Commits: <count>"
echo "- PR status: <updated>"
```

## Integration
Add these checks to the beginning of each translation task:
```bash
# Check for background pipeline interference
if ps aux | grep -q 'hermes -z' | grep -v grep; then
  echo "WARNING: Background translation pipeline detected"
  echo "Current PID: $(ps aux | grep 'hermes -z' | grep -v grep | awk '{print $2}')"
  echo "Pipeline log: ~/root/github/htlb-pipeline/pipeline.log"
  echo "Decide: stop background work or proceed with verification"
fi
```