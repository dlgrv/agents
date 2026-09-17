# MQM-based review rubric for Chinese-to-Russian translation

## Review categories

### Fidelity & Terminology
- Check that statistics are preserved (e.g., 498 items, A 323/B 126/C 49, 891 studies)
- Verify that numbers and percentages are not altered (e.g., 20–48%, 97.2%, 38,227)
- Ensure that Chinese-specific jargon is localized appropriately (e.g., «когорта» → «группа»)
- Check that field labels are translated correctly (来源→Источники, 成本标签→Затраты/Выгода/Риск)
- Confirm that DOIs and URLs are preserved byte-faithful
- Verify that disclaimer is present for chapters discussing Chinese laws

### Structure & Links
- Verify that item counts match source (### X. Title must equal source)
- Check that tag-comment counts match source (<!-- 成本标签: 钱=0 时间=少 毅力=些 收益=大 口径=死亡率 -->)
- Ensure that all back-links use correct relative path to README.ru.md
- Confirm that chapter links in README.ru.md point to Russian slags
- Check that badges have Russian labels but same statistics
- Verify that glossary table rows count matches source

## Verification script template

```bash
# item counts
zh_items=$(grep -c '^### ' book/zh-file.md)
ru_items=$(grep -c '^### ' book/ru-file.md)

# tag-comment counts
zh_tags=$(grep -c '成本标签' book/zh-file.md)
ru_tags=$(grep -c 'Затраты/Выгода/Риск' book/ru-file.md)

# DOI presence
zh_doi=$(grep -c 'doi.org' book/zh-file.md)
ru_doi=$(grep -c 'doi.org' book/ru-file.md)

# sources (byte-faithful after label translation)
zsrc=$(grep '^- 来源：' book/zh-file.md | sed 's/：/:/' | cut -d: -f2)
rsrc=$(grep '^- Источники:' book/ru-file.md | cut -d: -f2)

# no untranslated han outside allowed zones
han=$(grep -v '](book/' book/ru-file.md | grep -v '](docs/' | grep -v '（' | grep -v '《' | grep -c '[一-鿿]')
```