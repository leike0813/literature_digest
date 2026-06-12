# literature-analysis Delta Specification

## Requirements

### Requirement: Runtime Package Layout SHALL Be Clear And Stable

`analysis_runtime` SHALL use internal module names that describe runtime responsibilities without changing the public CLI.

#### Scenario: Package shape is inspected
- **WHEN** the package files are listed
- **THEN** `runtime.py`, `stages.py`, `algorithm_adapter.py`, `deterministic_core.py`, `runtime_db.py`, `references.py`, `citations.py`, and `gate_contract.py` exist
- **AND** migration-era one-function modules `db.py`, `source.py`, `plan.py`, `digest.py`, `rendering.py`, `local_handlers.py`, and `algorithm_core.py` do not exist.

### Requirement: Public Commands SHALL Remain Compatible

The package structure cleanup SHALL NOT change `scripts/run_analysis.py` command names or output behavior.

#### Scenario: Runtime wrapper runs
- **WHEN** a user runs any existing `run_analysis.py` command
- **THEN** command parsing and stdout JSON remain compatible with the previous `literature-analysis` contract.
