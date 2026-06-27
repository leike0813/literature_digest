## 1. Runtime Mapping

- [x] 1.1 Extract and persist non-numeric bracket labels from plain-text reference entries.
- [x] 1.2 Strip detected alpha labels before reference parse candidate generation.
- [x] 1.3 Extract bracket-alpha citation mentions, including grouped and OCR/TeX-noisy labels.
- [x] 1.4 Join citation mentions by normalized label alias with duplicate-label ambiguity handling.
- [x] 1.5 Render mapped alpha-label items with their original source label.

## 2. Guidance

- [x] 2.1 Update `SKILL.md` citation guidance for bracket-alpha labels.
- [x] 2.2 Update `references/citation_analysis.md` mapping preference and behavior notes.

## 3. Tests

- [x] 3.1 Add runtime tests for grouped alpha labels and all-letter labels.
- [x] 3.2 Add runtime tests for OCR/TeX-noisy label normalization.
- [x] 3.3 Add runtime tests for duplicate-label ambiguity and false positives.
- [x] 3.4 Run the targeted literature-analysis regression suite.
