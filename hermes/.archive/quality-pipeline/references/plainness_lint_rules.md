# Plainness Lint Rules

## Scope
Plainness lint evaluates only the "Простыми словами" field in translation chapters for child-level readability.

## Rules

### Long Sentences
- **Trigger:** >25 words per sentence
- **Severity:** WARNING
- **Action:** Split into shorter sentences
- **Example:** "К этой цифре нужна скидка: у тех, кто старательно принимает плацебо, смертность тоже ниже, то есть заметная часть пользы объясняется тем, что 'люди, готовые дисциплинированно принимать лекарства, изначально внимательнее к своему здоровью'." → Split into 2-3 sentences

### Which Chains
- **Trigger:** ≥3 consecutive "которой" clauses
- **Severity:** WARNING
- **Action:** Replace with subordinate clauses or rephrase
- **Example:** "Пациенты, которые принимают лекарства, которые выписал врач, которые находятся под наблюдением" → "Пациенты, принимающие назначенные врачом лекарства под наблюдением"

### Unexplained Abbreviations
- **Trigger:** Medical/legal/financial abbreviations without explanation
- **Severity:** WARNING
- **Action:** Add explanation in parentheses after first use
- **Example:** "ОМС покрывает диализ" → "ОМС (обязательное медицинское страхование) покрывает диализ"
- **Whitelist:** ОМС, УЗИ, МРТ, ДТП, ВИЧ, СПИД, COVID-19, ВИЧ-инфекция

## Whitelist
Common abbreviations that do not require explanation:
- ОМС (обязательное медицинское страхование)
- УЗИ (ультразвуковое исследование)
- МРТ (магнитно-резонансная томография)
- ДТП (дорожно-транспортное происшествие)
- ВИЧ (вирус иммунодефицита человека)
- СПИД (синдром приобретённого иммундфицита)
- COVID-19
- ВИЧ-инфекция

## Implementation Notes
- Only applies to "Простыми словами" field
- Other fields ("Эффект", "Источники") use technical register
- Collapses whitespace before counting sentences
- Reports warnings but does not block pipeline
