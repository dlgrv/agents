# Wave Planning and Task Management

## Wave Structure

### Delta-Based Wave Classification
After upstream delta analysis (fe33acf^1 → HEAD), chapters are classified into three waves based on content changes:

- **W1**: Chapters with significant CN changes requiring retranslation (21 chapters × 3 languages = 63 tasks)
- **W2**: Chapters with moderate CN changes requiring revision (24 chapters × 3 languages = 72 tasks) 
- **W3**: Chapters with minimal/no CN changes (45 chapters × 3 languages = 135 tasks)

### Specific Chapter Assignments
- **W1**: 02, 05, 06, 23, 04, 12, 31
- **W2**: 03, 08, 09, 11, 20, 21, 30, 07
- **W3**: 10, 14, 15, 16, 17, 18, 19, 22, 24, 25, 26, 27, 28, 29, 32

## Task Contract for All Waves

### Core Requirements
Each task must include:
- **Fresh units**: Translation from CN (already in file) → overwrite with translation
- **Revised units**: Compare with new CN from digest → update differences in existing translation
- **Write-first rule**: First tool call = write_file, no batch reading, no analysis paralysis
- **Self-check**: Verify §TAG§ and §SRC§ markers, no '- Источники:', no '<!--', no '!'
- **Output format**: JSON with units_done, list, chapter, lang fields

### Field Marker Rules by Language
- **RU**: `- Стоимость:`, `- Простыми словами:`, `- Эффект:`, `- Уровень доказательности:`, `- Примечания:`
- **EN**: `- Cost:`, `- In plain terms:`, `- Benefit:`, `- Evidence grade:`, `- Notes:`
- **ES**: `- Costo:`, `- En términos sencillos:`, `- Beneficio:`, `- Nivel de evidencia:`, `- Notas:`

### Number Formatting Rules
- **RU**: Space thousands (80 300), no commas
- **EN**: Comma thousands (80,300), no spaces
- **ES**: Space thousands, comma decimal (80 300,17,4)

## Pipeline Integration

### Preparation Phase
- **Run directories**: Fill with CN for fresh units, translations for revised units
- **Delta analysis**: Map edited units to specific chapters and languages
- **Task generation**: Create 90 tasks (chapters × languages) with precise unit lists

### Execution Phase
- **Wave order**: W1 first (validation), then W2, then W3
- **Parallel execution**: Use delegation for parallel subagent work
- **Progress monitoring**: Track file writes and completion status

### Validation Phase
- **Wave pipeline**: Run `tools/wave_pipeline.py` to verify all chapters in the wave
- **Quality gates**: Check assembly output, verify.py status, Chinese character leaks
- **Publication**: Only after full wave validation and user approval

## Quality Assurance

### Assembly Validation
```bash
# For each chapter in the wave
python3 tools/assemble.py /root/htlb-run-<lang>/<chapter>
python3 tools/verify.py <chapter> --lang <lang>
```

### Cross-Language Consistency
- Verify field labels match expected patterns per language
- Check number formatting consistency across languages
- Ensure no Chinese characters in visible text (regex scan)

### Error Handling
- **Timeout recovery**: Use subagent timeout recovery protocol for stalled tasks
- **Format drift**: Monitor for incorrect field markers or number formatting
- **Content gaps**: Check for missing units or incomplete translations

## References

- [Pilot wave protocol](./pilot-wave-protocol.md)
- [Subagent timeout recovery](./subagent-timeout-recovery.md)
- [Field markers reference](./field-markers.md)
- [Web UI capitalization](./web-ui-capitalization.md)
