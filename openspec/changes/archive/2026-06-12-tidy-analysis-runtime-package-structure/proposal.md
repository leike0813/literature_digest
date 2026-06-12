## Why

`literature-analysis` now owns its runtime code, but the `analysis_runtime` package still reflects the incremental migration steps. Several files contain only one wrapper function, while names like `db.py`, `algorithm_core.py`, and `local_handlers.py` make the package harder to navigate.

This change tidies the internal package structure without changing the public CLI or output contract.

## What Changes

- Rename internal modules to match their responsibilities:
  - `db.py` becomes `runtime.py`.
  - `algorithm_core.py` becomes `deterministic_core.py`.
  - `local_handlers.py` becomes `algorithm_adapter.py`.
- Merge thin stage wrappers into `stages.py`.
- Keep domain-specific `references.py`, `citations.py`, `gate_contract.py`, and `runtime_db.py`.
- Update runtime tests to lock the new package shape.

## Capabilities

### Modified Capabilities

- `literature-analysis`: keeps the same command interface and artifacts while using a clearer internal runtime package layout.

## Impact

- **Public impact**: none; `scripts/run_analysis.py` commands and stdout contract are unchanged.
- **Runtime impact**: internal imports change only within `literature-analysis/scripts`.
- **Maintenance impact**: future algorithm extraction has clearer seams: runtime bootstrap, deterministic core adapter, stage wrappers, domain modules, and SQLite access.
