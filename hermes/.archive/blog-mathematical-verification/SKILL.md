---
name: blog-mathematical-verification
description: Verify math accuracy in blog articles with Python.
---

# Blog mathematical verification workflow

## Purpose

Ensure that all formulas, numbers, and figures in technical blog articles are mathematically correct by recomputing them from scratch using Python. This workflow catches errors that can slip through during writing and figure generation, such as:
- Incorrectly plotted points on decision boundaries
- Wrong gradient descent step calculations
- Misaligned axis labels or annotations
- Inconsistent numeric examples in prose

## Workflow steps

1. **Identify all numeric claims and formulas** in the article text and figures.
2. **Write a Python script** that recomputes each value using the same formulas and data as the article.
3. **Run the script using `execute_code`** and compare outputs to the article's stated values.
4. **Fix any discrepancies** in the article or figures, then re-run verification.
5. **Document the verification** in the article commit message (e.g., "math verification: all formulas recomputed and verified").

## Common error patterns

### 1. Decision boundary points

- **Error:** Points plotted above/below the decision boundary line when they should be exactly on it (z=0).
- **Check:** For each point (x₁, x₂), compute z = w₁x₁ + w₂x₂ + b. Verify |z| < tolerance (e.g., 0.01).
- **Fix:** Adjust point coordinates or the line equation to satisfy z=0 exactly.

### 2. Gradient descent steps

- **Error:** Incorrect weight updates or loss values between steps.
- **Check:** Recompute each step: w_new = w_old - α·∇w, loss_new = loss(w_new). Verify loss decreases monotonically.
- **Fix:** Correct the step calculations in the article and update the figure accordingly.

### 3. Figure annotations

- **Error:** Axis labels or data point annotations that don't match the actual computed values.
- **Check:** Extract the plotted data from the figure (or regenerate it) and verify all labels are accurate.
- **Fix:** Update annotations to match the recomputed values.

### 4. Numeric prose precision

- **Error:** Text stating "increased by 30%" when the actual calculation shows "increased by almost 30%".
- **Check:** Recompute the percentage change and verify the wording matches the precision.
- **Fix:** Adjust text to match the exact calculated value (e.g., "почти на треть" instead of "на треть").

## Example verification script (logistic regression)

```python
import numpy as np

# Article parameters
w = np.array([1.2, -0.4, 2.0])
b = -0.9

# Check decision boundary points (should satisfy z = 0)
test_points = [
    (0.5, 0.3),  # Article claims this is above line (cat)
    (0.9, 0.7),  # Article claims this is below line (not cat)
    (1.42, 0.35), # Fixed point that was incorrectly plotted
]

print("Decision boundary verification:")
for x1, x2 in test_points:
    z = w[0]*x1 + w[1]*x2 + b
    print(f"Point ({x1}, {x2}): z = {z:.3f} ({'ON boundary' if abs(z) < 0.01 else 'OFF boundary'})")

# Check gradient descent steps
alpha = 0.1
y_true = 1  # Example: actual label is "cat"

print("\nGradient descent verification:")
for step, (x1, x2) in enumerate([(0.5, 0.3), (0.9, 0.7)], 1):
    z = w[0]*x1 + w[1]*x2 + b
    y_pred = 1 / (1 + np.exp(-z))  # Sigmoid
    loss = -y_true * np.log(y_pred) - (1-y_true) * np.log(1-y_pred)
    
    print(f"Step {step}: z={z:.3f}, ŷ={y_pred:.3f}, loss={loss:.3f}")
    # Verify loss decreases (if multiple steps)
```

## Integration with blog article workflow

This verification should be added to the "Structural review workflow" in the dlgrv-desktop skill's `references/blog-articles.md`: after the naive reader review, run this mathematical verification script. If any errors are found, fix them and re-run both the naive reader and math verification before proceeding to PR creation.

## Best practices

- **Always use actual computed values**, not approximated ones
- **Set appropriate tolerances** for floating-point comparisons (typically 0.01 for decision boundaries)
- **Verify both directions** of claims (e.g., if a point is claimed to be above the boundary, verify z > 0)
- **Document all fixes** in the commit message for transparency
- **Re-run verification** after any changes to ensure no new errors were introduced