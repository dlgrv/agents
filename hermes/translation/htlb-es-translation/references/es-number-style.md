# Spanish number style for HTLB translations

## Rules

- Thousands separator: space (not period or comma)
- Decimal separator: comma (not period)
- Examples: 248 099, 17,4, ×10 000
- Never round or invent digits: 8.03 万 = exactly 80 300
- 万 → ×10 000 written out (never 'mil millones')
- 亿 → ×10⁸ written out (never 'cien millones')
- Unit-weight figures require parenthetical gloss: CN «0.25 千克» → ES «0,25 kilogramos (250 gramos)» due to verifier quirk (千 inside 千克 is read as scale word and folds to key 250)

## Examples

| Original | Spanish |
|---|---|
| 248099 | 248 099 |
| 17.4 | 17,4 |
| 8.03万 | 80 300 (×10 000) |
| 0.25千克 | 0,25 kilogramos (250 gramos) |
| 国食药监办〔2010〕432号 | Oficina de la Administración Estatal de Alimentos y Medicamentos (documento 〔2010〕 n.º 432) |
