## 1. OpenSpec artifacts

- [x] 1.1 Create change directory
- [x] 1.2 Add proposal, design, tasks, and delta spec

## 2. Guidance absorption

- [x] 2.1 Add `literature-analysis/references/source_and_plan.md`
- [x] 2.2 Add `literature-analysis/references/digest_generation.md`
- [x] 2.3 Add `literature-analysis/references/reference_extraction.md`
- [x] 2.4 Add `literature-analysis/references/citation_analysis.md`
- [x] 2.5 Add `literature-analysis/references/finalization_and_recovery.md`
- [x] 2.6 Update `literature-analysis/SKILL.md` reference index

## 3. Algorithm absorption

- [x] 3.1 Add `analysis_runtime` package
- [x] 3.2 Move runtime DB setup behind local `db.py`
- [x] 3.3 Move source normalization behind local `source.py`
- [x] 3.4 Move reference prepare behind local `references.py`
- [x] 3.5 Move citation prepare behind local `citations.py`
- [x] 3.6 Move render fallback behind local `rendering.py`
- [x] 3.7 Update `run_analysis.py` to prefer local modules

## 4. Tests

- [x] 4.1 Add guidance tests for new references
- [x] 4.2 Add tests that prepare paths do not call `_run_legacy`
- [x] 4.3 Keep existing end-to-end compatibility tests passing

## 5. Validation

- [x] 5.1 Run targeted `literature-analysis` tests
- [x] 5.2 Run guidance tests
- [x] 5.3 Run existing related runtime/render tests
