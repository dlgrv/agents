# Upstream communication for translations

## Overview
When translating content and working with upstream Chinese repositories, follow this protocol for clear communication and proper issue management.

## Issue management workflow

### 1. Proposing a translation

- **Open issue in Chinese:** Write the proposal in Chinese to match the upstream community
- **Explain fork-only approach:** Clarify that translation lives in fork, no PR to main (unless explicitly requested)
- **Highlight QA rigor:** Mention byte-identity verification, machine tag preservation, and automated scripts
- **Provide timeline:** Estimate completion timeframe and update progress in issue comments
- **Request README integration:** Ask author to add language links when complete

### 2. Progress updates

- **Regular milestones:** Update issue with completed chapters (e.g., "10/31 chapters translated")
- **Include verification status:** Mention if chapters are verified (item counts, sources byte-identical)
- **Link to fork branch:** Provide direct links to translation branch for transparency
- **Website previews:** Share GitHub Pages URLs when available

### 3. Completion announcement

- **Final status:** Declare all chapters complete and verified
- **Website links:** Provide all language URLs (zh/ru/en)
- **README request:** Ask author to update main README language links to dedicated URLs
- **Issue closure:** Request issue closure or mark as resolved

## Author response patterns

Based on HowToLiveBetter project experience:

### Positive responses
- **"Go ahead. Same as Russian version"** — Author approves fork-only approach
- **"Keep sources byte-identical"** — Author emphasizes QA rigor
- **"Add to README when done"** — Author expects language link updates

### Common requests
- **"Update Russian link to /ru/"** — Author prefers dedicated language URLs over root redirect
- **"No PR needed, just close"** — Author prefers to keep main repo clean

### Follow-up timing
- Allow 1–2 days for author response before concluding
- If no response to completion announcement, consider issue resolved after 48 hours

## Issue template

```markdown
## 翻译提案 / Translation Proposal

**语言 / Language:** [English/Russian]

**计划 / Plan:**
- 翻译将保存在 fork 中，不会提交到主仓库 / Translation will live in fork, no PR to main
- 源码（来源：/DOI/URLs）和机器标签将保持字节级一致 / Sources and machine tags will remain byte-identical
- 使用自动化脚本验证结构完整性 / Use automated scripts for structure verification

**进度 / Progress:**
- [ ] 开始 / Started
- [ ] 翻译中 / In progress
- [ ] 验证中 / Verifying
- [ ] 完成 / Complete

**链接 / Links:**
- Fork 分支: [translation/en branch link]
- 网站: [GitHub Pages URL]

**请求 / Request:**
完成后请将 README 中的语言链接更新为专用地址 / Please update language links in README to dedicated URLs when complete
```