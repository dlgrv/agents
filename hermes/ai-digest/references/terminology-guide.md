# AI Digest Terminology Guide

This reference explains how to format complex ML/AI terms for novice audiences while preserving technical accuracy.

## Format Rules

1. **First Mention**: Always use the real term first, then explain in Russian parentheses immediately after
   - Example: "on-policy дистилляция (обучение ученика на данных, сгенерированных учителем)"
   - Never replace the term with a simplified version — teach through explanation

2. **Common Terms to Expand** (alphabetical):
   - **KV-кэш** — память модели о уже прочитанном тексте: чтобы не перечитывать всё заново на каждом шаге, модель хранит промежуточные вычисления; чем длиннее диалог, тем сильнее эта память потребляет ресурсы
   - **On-policy дистилляция** — обучение ученика на данных, сгенерированных учителем: в отличие от off-policy, где данные берутся из опыта, здесь ученик учится на действиях учителя, что даёт более стабильное обучение
   - **RL-среда** (Reinforcement Learning) — симуляция мира, в которой агент обучается делать действия: среда выдаёт награды за правильные действия и штрафы за плохие, агент учится максимизировать общую награду
   - **Sparse lookup** — разреженное извлечение информации: вместо того чтобы перебирать все данные, модель использует индексы для быстрого доступа к релевантным частям
   - **Mixture-of-Experts** — подход с несколькими специализированными моделями: вместо одной большой модели используются маленькие эксперты, каждый отвечает за свою область, и система решает, какой эксперт нужен для текущего запроса

3. **Glossary Section**: After selecting top-5 papers, include a glossary block:
   ```
   📚 Словарик
   - **Термин** — простое объяснение с бытовой аналогией, где уместно
   - **Термин** — простое объяснение с бытовой аналогией, где уместно
   ```

4. **Anglicisms**: Provide Russian equivalents when available
   - Harness → обвязка агента
   - Prefill → предзаполнение
   - KV cache → KV-кэш
   - Token indexing → индексация токенов

## Style Notes

- Maintain technical precision while using accessible language
- Use analogies only when they clarify, not when they oversimplify
- Repeat key terms across papers to build vocabulary gradually
- Update glossary with 3-6 terms per digest, focusing on newly introduced concepts