## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, tasks, and delta spec

## 2. Runtime and assets

- [x] 2.1 Copy render templates and schemas into `literature-analysis/assets`
- [x] 2.2 Add local runtime DB implementation and remove top-level legacy DB shim
- [x] 2.3 Add local deterministic algorithm core backed by local assets and DB

## 3. Domain module migration

- [x] 3.1 Route source normalization through local algorithms
- [x] 3.2 Route plan and digest persistence through local algorithms
- [x] 3.3 Route reference preparation, persistence, quality, and enrichment through local algorithms
- [x] 3.4 Route citation preparation, persistence, and render finalize through local algorithms
- [x] 3.5 Route status/gate contract through local DB only

## 4. Legacy removal

- [x] 4.1 Delete `analysis_runtime/legacy.py`
- [x] 4.2 Delete `analysis_runtime/stage_adapter.py`
- [x] 4.3 Ensure runtime scripts contain no cross-skill package references

## 5. Tests and validation

- [x] 5.1 Add static boundary tests for `literature-analysis/scripts/**`
- [x] 5.2 Keep wrapper runtime and guidance tests passing
- [x] 5.3 Run related old skill regression tests
- [x] 5.4 Run OpenSpec status for this change
