# Web UI Capitalization Reference

## Purpose

This reference documents the capitalization rules for Russian web interfaces (index.html, README.ru.md) to ensure consistent presentation of translated content while preserving original markdown formatting.

## Rules

### Automatic Capitalization for Field Values

When rendering translated content in web interfaces, apply automatic capitalization to field values:

- **Простыми слова values**: Capitalize first letter (e.g., 'пристёгнутый ремень...' → 'Пристёгнутый ремень...')
- **Эффект values**: Capitalize first letter (e.g., 'по оценке...' → 'По оценке...')
- **Примечания values**: Capitalize first letter (e.g., 'цифры NHTSA...' → 'Цифры NHTSA...')

### Implementation in Parser

Add to the JavaScript parser logic:

```javascript
else if ((m = /^- (?:说人话|Простыми слова)[：:](.*)$/.exec(line))) { 
  entry.human = m[1]; 
  if (LANG==='ru') entry.human = entry.human.replace(/^\s*(.)/, (c)=>c.toUpperCase()); 
}
else if ((m = /^- (?:收益|Эффект)[：:](.*)$/.exec(line))) { 
  entry.gain = m[1]; 
  if (LANG==='ru') entry.gain = entry.gain.replace(/^\s*(.)/, (c)=>c.toUpperCase()); 
}
else if ((m = /^- (?:备注|Примечания)[：:](.*)$/.exec(line))) { 
  entry.note = m[1]; 
  if (LANG==='ru') entry.note = entry.note.replace(/^\s*(.)/, (c.toUpperCase()); 
}
```

### What NOT to Capitalize

- **Field labels**: "Стоимость", "Эффект", "Примечания" should remain as defined in field marker rules
- **Numbers and technical terms**: Preserve byte-for-byte (§ numbers, dosages, etc.)
- **Original markdown files**: Capitalization only applies to web interface rendering, not source files

## Quality Assurance

- Verify all 498 entries have properly capitalized first letters
- Test parser with LANG='ru' and LANG='zh' to ensure conditional logic works
- Confirm no unintended capitalization of field labels or numbers
- Check that capitalization is consistent across all chapters in web interface

## Example

**Before parsing:**
- Простыми словами: пристёгнутый ремень на переднем сиденье...
- Эффект: по оценке американского NHTSA...
- Примечания: цифры NHTSA 45%/60%...

**After parsing (LANG='ru'):
- Простыми словами: Пристёгнутый ремень на переднем сиденье...
- Эффект: По оценке американского NHTSA...
- Примечания: Цифры NHTSA 45%/60%...

**In markdown files (unchanged):**
- Простыми слова: пристёгнутый ремень на переднем сиденье...
- Эффект: по оценке американского NHTSA...
- Примечания: цифры NHTSA 45%/60%...
