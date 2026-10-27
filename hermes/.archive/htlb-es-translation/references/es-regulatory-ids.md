# Regulatory document ID translation (HTLB ES)

## Rule

CN regulatory document IDs (e.g. 国食药监办〔2010〕432号) must be paraphrased in Spanish with the issuing office name + "(documento 〔2010〕 n.º 432)" pattern per the EN translation. Never keep hanzi in body text (except in citation lines, which are byte-faithful).

## Examples

| Original | Spanish |
|---|---|
| 国食药监办〔2010〕432号 | Oficina de la Administración Estatal de Alimentos y Medicamentos (documento 〔2010〕 n.º 432) |
| ... | (follow EN pattern for all regulatory IDs) |

## Pitfall

If a subagent preserves hanzi in body text (e.g. in Notas fields), the verifier must manually replace it with this pattern. This is a byte-faithfulness override for regulatory IDs only; other byte-faithful zones (citation lines, DOIs) must remain untouched.
