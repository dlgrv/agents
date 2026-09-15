---
name: adhd-blog-audit
description: Audit technical blogs for ADHD/СДВГ readers.
---

# ADHD Blog Audit

Use alongside blog-clarity-check when targeting readers with ADHD/СДВГ or general attention challenges.

## ADHD-specific audit checklist

### 1. Term Consistency
- One concept = one name throughout the section
- If a synonym is used, add explicit bridge: «this is the same as X»
- Watch for: signal/gradient, network/model/neural network, token/piece, vector/embedding
- Report: list of synonyms used without bridges

### 2. Sentence Length & Structure
- Max 25 words per sentence
- No more than 2 commas, dashes, or parentheses per sentence
- Break complex sentences into 2-3 shorter ones
- Report: top 10 longest sentences with rewrite suggestions

### 3. Promise-Keeping
- Every «explained later», «see in step X», «we'll cover this» must be fulfilled within 3 sections
- If not fulfilled, either add the explanation or remove the promise
- Report: list of broken promises with line numbers

### 4. New Terms per Paragraph
- Max 1-2 new technical terms per paragraph
- Provide example or analogy immediately after introducing a new term
- If introducing multiple terms, break into separate paragraphs
- Report: paragraphs with >2 new terms without examples

### 5. Scan Test (Headers + Bold Only)
- Extract only ## headings, ### subheadings, and **bold** text
- Does this skeleton tell a coherent story?
- If not, add explicit links between key points in bold text
- Report: gaps in skeleton logic

### 6. Attention Drop Points
- Flag where a linear reader would get lost
- No backtracking allowed: if the reader can't understand from context alone, fix it
- Common drop: symbols before introduction, anaphora without clear reference
- Report: exact line numbers and reasons

### 7. Formula Clarity (NEW)
- Every formula must have: (1) meaning explained before appearance, (2) concrete numerical example, (3) connection to real-world intuition
- Report formulas missing any of these, with exact line numbers
- Common gaps: formulas introduced without context, symbols not defined, no example computation
- Special focus: linear algebra (matrices, vectors), derivatives, probability terms

## Report format

```
ADHD AUDIT — <section name>
Term consistency: ✅/⚠️/❌ (list of issues)
Sentence length: ✅/⚠️/❌ (top problematic sentences)
Promise-keeping: ✅/⚠️/❌ (broken promises)
New terms density: ✅/⚠️/❌ (problematic paragraphs)
Scan test: ✅/⚠️/❌ (skeleton gaps)
Attention drops: ✅/⚠️/❌ (exact locations)
→ rewrite / minor fixes / clean
```

## Workflow

1. Run blog-clarity-check first
2. Then run this ADHD-audit for attention-specific issues
3. Fix term consistency and sentence length first (most impactful for ADHD)
4. Then address promises and scan test
5. Finally flag attention drop points for manual review

## Pitfalls

- **Term drift**: Same concept using multiple names without bridges confuses working memory
- **Long sentences**: Complex nested sentences exceed working memory capacity
- **Broken promises**: Unfulfilled «explained later» creates frustration and loss of trust
- **Term overload**: More than 2 new terms per paragraph causes cognitive overload
- **Skeleton gaps**: Headers and bold text must tell the story alone for skimmers