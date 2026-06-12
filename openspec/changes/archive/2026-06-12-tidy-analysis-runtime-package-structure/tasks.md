## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, tasks, and delta spec

## 2. Package shape

- [x] 2.1 Rename `algorithm_core.py` to `deterministic_core.py`
- [x] 2.2 Rename `local_handlers.py` to `algorithm_adapter.py`
- [x] 2.3 Rename `db.py` to `runtime.py`
- [x] 2.4 Merge `source.py`, `plan.py`, `digest.py`, and `rendering.py` into `stages.py`
- [x] 2.5 Delete obsolete thin wrapper files

## 3. Import updates

- [x] 3.1 Update `run_analysis.py` imports and aliases
- [x] 3.2 Update internal references to `deterministic_core` and `algorithm_adapter`
- [x] 3.3 Keep top-level `scripts/runtime_db.py` compatibility entrypoint unchanged

## 4. Tests and validation

- [x] 4.1 Update package shape and orchestration tests
- [x] 4.2 Run targeted literature-analysis tests
- [x] 4.3 Run broader related regression tests
- [x] 4.4 Run OpenSpec status for this change
