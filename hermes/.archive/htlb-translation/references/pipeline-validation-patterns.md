# Pipeline Validation Patterns

Patterns for validating translation quality pipeline passes before enabling them in production.

## Principles

**validate-before-enable**: Each pass must prove its effectiveness on test data before inclusion in the main flow.

**seed-reproducibility**: All test data (mutations, anchors, degradations) is fixed with seed=42 for reproducible results.

**unit-first**: Validation runs on small, representative units (not full chapters) to catch issues quickly.

## Patterns

### 1. Mutational Testing

**Use case**: Validate fact-check pass (E)
**Implementation**:
```python
# Task 4: Мутационный тест для E
# 30 семантических мутаций + 30 контролов, seed=42
# Catch-rate E ≥ 80%, FP на контролях ≤ 10%

# Generate mutations with subagents
# Run factcheck on mutated units
# Aggregate results programmatically
# Accept: пороги выше → переработка промпта, максимум 1 итерация
```

**Key metric**: catch-rate (percentage of real defects caught)

### 2. Golden Set Validation

**Use case**: Validate judge pass (C/D)
**Implementation**:
```python
# Task 7: Золотой сет
# 60 пар (6 глав × 3 страты × ru/en + 24 случайных + 10 приманок)
# Judge agreement: Cohen's κ ≥ 0.6 (судья = семья переводчика)

# Generate pairs with controlled degradations
# Run judge A/B comparisons
# Calculate agreement with ground truth
# Accept: κ < 0.4 → запасные модели или переработка промптов
```

**Key metric**: Cohen's kappa (inter-judge reliability)

### 3. FP Rate Auditing

**Use case**: Validate style pass (A)
**Implementation**:
```python
# Task 6: FP-аудит стиля
# Аудит ≥100 фрагментов по 64 главо-языкам
# Precision ≥ 80%, recall ≥ 60%

# Sample from existing translations
# Run style_check on sample
# Manually verify findings
# Accept: FP > 40% → выбрасывать правило, а не тюнить
```

**Key metrics**: precision, recall (style marker detection accuracy)

### 4. QE Noise Baseline

**Use case**: Validate QE pass (B)
**Implementation**:
```python
# Task 3: Шум QE + базлайны
# 4 якоря × 5 прогонов → σ → порог τ = max(3σ, 0.01)
# Anchor improvement ru13 pre-fix vs post-fix ≥ 2τ

# Run QE on anchor texts multiple times
# Calculate standard deviation
# Set threshold for "significant" improvement
# Accept: advisory-only, no blocking threshold
```

**Key metric**: anchor improvement ratio

## Integration with TDD

Each pipeline pass follows TDD-like validation:

1. **RED**: Define validation criteria (catch-rate ≥80%, κ ≥0.6, etc.)
2. **GREEN**: Implement pass on test data
3. **REFACTOR**: Adjust thresholds or prompts if criteria not met
4. **ENABLE**: Include in main flow only after validation passes

## Pitfalls

**Over-validation**: Don't iterate endlessly on validation criteria — set reasonable thresholds and move forward.

**Under-validation**: Don't skip validation on "simple" passes — even advisory passes need empirical validation.

**Seed dependence**: Always document seed=42 and include test data in version control.

**Scale mismatch**: Validation on small units may not scale to full chapters — monitor for scalability issues.

## Acceptance Workflow

1. Run validation task
2. Check if acceptance criteria met
3. If not: adjust pass/prompts/thresholds
4. If yes: enable in pipeline
5. Monitor performance on real data

## Monitoring

After enabling a pass, monitor:
- Real-world catch rate vs validation rate
- False positive rate in production
- Performance impact (time, cost)
- User feedback on quality changes

Adjust if real-world performance differs significantly from validation.
