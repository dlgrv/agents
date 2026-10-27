# HTLB Field Marker Reference

## Chinese Field Markers → Russian

| Chinese | Russian | Notes |
|---------|--------|-------|
| 成本 | Стоимость | Cost/expense field |
| 说人话 | Простыми словами | Simple language field |
| 收益 | Эффект | Benefit/effect field |
| 证据等级 | Уровень доказательности | Evidence level (A/B/C remain) |
| 备注 | Примечания | Notes/remarks field |

## Translation Rules

- **Numbers**: Always byte-for-byte copy (§ numbers remain unchanged)
- **Slang**: Never translate: cohort/exposure/quartile/confounding/population/low-evidence
- **Style**: Live Russian, not literal translation
- **Headers**: Must start with verbs
- **Simple language field**: No numbers outside "Эффект" section
- **Exclamation marks**: None allowed
- **Sources**: Never translate — injected byte-by-byte by assemble.py

## Unit File Structure

Each unit file must contain:
1. Chapter header (exact format per TRANSLATION.md)
2. Empty lines
3. Translated content with field markers
4. §TAG§ placeholder (on its own line)
5. §SRC§ placeholder (on its own line)

## Chapter Preparation

```bash
# Prepare run directory for a chapter
cd ~/github/HowToLiveBetter
mkdir -p /root/htlb-run/<chapter>/units
cp tools/digest/<chapter>/units/*.md /root/htlb-run/<chapter>/units/
for n in 00 01 02 ...; do 
  echo "§TAG§" >> /root/htlb-run/<chapter>/units/$n.md
  echo "§SRC§" >> /root/htlb-run/<chapter>/units/$n.md
done
```