# Badge Update Workflow

## README Badge Synchronization

After adding new chapters or completing translation waves, HTLB project badges must be updated to reflect current statistics.

### Badge Values Source
Badge values are derived from Chinese source files (`book/*.md`), not translated files:

- **Items**: Total `### ` headings in all `book/*.md` files
- **Evidence grades**: Count of A/B/C grade markers (`- 证据等级：A/B/C`) across all chapters
- **Primary sources**: Count of HTTP(S) URLs in source lines (`- 来源：` and `- 备注：`)

### Update Command
Run this Python script to generate correct badge URLs:

```bash
cd ~/github/htlb-ru
python3 -c "
import re, glob
zh_files = glob.glob('book/[0-9][0-9]-*.md')
items = sum(len(re.findall(r'^### ', open(f).read(), re.M)) for f in zh_files)
grades = {'A':0, 'B':0, 'C':0}
links = 0
for f in zh_files:
    for m in re.finditer(r'^- 证据等级：([ABC])', open(f).read(), re.M):
        grades[m.group(1)] = grades.get(m.group(1), 0) + 1
    for l in re.finditer(r'^- (?:来源|备注)：.*$', open(f).read(), re.M):
        links += len(re.findall(r'https?://', l.group(0)))
print(f'Items-{items}-Evidence grades-A {grades[\"A\"]}·B {grades[\"B\"]}·C {grades[\"C\"]}-Primary sources-{links} links')
"
```

### Application to README Files

**README.md**: Update badge URLs with English labels:
- `Items-601-18794e?style=flat-square` (was 528)
- `Evidence grades-A 407·B 146·C 48-915930?style=flat-square` (was A347·B131·C50)
- `Primary sources-1253 links-565a5f?style=flat-square` (was 1066)

**README.ru.md**: Update Russian-encoded badge URLs:
- `Пунктов-601-18794e?style=flat-square` (was 528)
- `Уровни доказательности-A 407·B 146·C 48-915930?style=flat-square` (was A347·B131·C50)
- `Первоисточники-1253 ссылка-565a5f?style=flat-square` (was 1066)

### Verification
After updating:
1. Check that `tools/check_content.py` passes
2. Verify badge URLs are correct in all README files
3. Confirm CI check-links gate passes

### Timing
- Update badges after each major translation wave
- Always update after adding new chapters (e.g., ch33)
- Run before committing to ensure CI gates pass

### Pitfalls
- Never use translated file counts for badge values — always use Chinese source files
- Badge URLs must be URL-encoded for non-English README files
- README.ru.md badges use Russian labels in URL-encoded format
- Missing badge updates cause CI check_content.py failures
