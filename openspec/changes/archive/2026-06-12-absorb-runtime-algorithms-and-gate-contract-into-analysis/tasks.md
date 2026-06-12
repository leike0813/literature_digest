## 1. OpenSpec artifacts

- [x] 1.1 Create change directory
- [x] 1.2 Add proposal, design, tasks, and delta spec

## 2. Runtime ownership

- [x] 2.1 Add direct stage handler adapter for migration-only fallback
- [x] 2.2 Add local plan and digest domain modules
- [x] 2.3 Move reference submit and metadata enrichment orchestration into `references.py`
- [x] 2.4 Move citation submit orchestration into `citations.py`
- [x] 2.5 Add local gate/status contract
- [x] 2.6 Remove `_run_legacy` subprocess usage from `run_analysis.py`

## 3. Guidance

- [x] 3.1 Mark legacy fallback as internal migration-only
- [x] 3.2 Note that normal runtime path is owned by `analysis_runtime`

## 4. Tests

- [x] 4.1 Add runtime ownership assertions
- [x] 4.2 Add status/gate contract assertions
- [x] 4.3 Keep existing wrapper and guidance tests passing

## 5. Validation

- [x] 5.1 Run targeted runtime/guidance tests
- [x] 5.2 Run broader related regression tests
- [x] 5.3 Run OpenSpec status for this change
