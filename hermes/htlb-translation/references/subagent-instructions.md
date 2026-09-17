# HTLB Subagent Instructions

## For Translation Subagents

**Task:** Translate one unit (not a whole chapter) immediately upon receiving it.

### Strict Instructions

- **Work = write files** — no analysis, no planning, no style study
- Write the translated unit to its file immediately upon completion
- Do not return JSON summaries — only write the file
- Do not study existing chapters for style — use the provided style sample in the task
- If you stall, restart with: 'work = write files, no analysis'

### Unit Translation Rules

| Chinese | Russian | Notes |
|---------|--------|-------|
| 成本 | Стоимость | Cost/expense field |
| 说人话 | Простыми словами | Simple language field |
| 收益 | Эффект | Benefit/effect field |
| 证据等级 | Уровень доказательности | Evidence level (A/B/C remain) |
| 备注 | Примечания | Notes/remarks field |

### Translation Constraints

- **Numbers**: Always byte-for-byte copy (§ numbers remain unchanged)
- **Slang**: Never translate: cohort/exposure/quartile/confounding/population/low-evidence
- **Style**: Live Russian, not literal translation
- **Headers**: Must start with verbs
- **Simple language field**: No numbers outside "Эффект" section
- **Exclamation marks**: None allowed
- **Sources**: Never translate — injected byte-by-byte by assemble.py

### File Structure

Each unit file must contain:
1. Chapter header (exact format per TRANSLATION.md)
2. Empty lines
3. Translated content with field markers
4. §TAG§ placeholder (on its own line)
5. §SRC§ placeholder (on its own line)

### Example Task Template

```
Translate unit /root/htlb-run/16/units/01.md

Use this style sample (from chapter 17):
- Стоимость: 0 юаней; заявление подаётся по месту жительства ребёнка
- Простыми словами: если ребёнок родился 1 января 2025 года или позже и проживает в Китае
- Эффект: план, изданный совместно Канцелярией ЦК КПК и Госсоветом
- Уровень доказательства: A
- Примечания: это единая для всей страны минимальная планка

Write result back to /root/htlb-run/16/units/01.md immediately. No analysis, no planning — just write.
```

## Pitfall

- **Never let subagents spend time on analysis or planning** — they must write files immediately
- Each subagent gets one unit (not a whole chapter) and must write it to its file upon completion
- Do not let subagents study existing chapters for style — provide a style sample in the task instead
- Subagents must not return JSON summaries — only write the translated unit file
- If a subagent stalls, restart it with stricter instructions: 'work = write files, no analysis'
