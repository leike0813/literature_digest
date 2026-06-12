# literature-analysis Delta Specification

## Requirements

### Requirement: Normal Runtime SHALL NOT Shell Out To Old Stage CLI

`literature-analysis/scripts/run_analysis.py` SHALL route normal commands through local `analysis_runtime` modules instead of invoking old `literature-digest/scripts/stage_runtime.py` as a subprocess.

#### Scenario: Submit command runs
- **WHEN** `persist_analysis_plan`, `persist_digest`, `persist_references`, `persist_citation_analysis`, or `finalize_outputs` runs
- **THEN** the command is handled by a local `analysis_runtime` module
- **AND** no `_run_legacy` subprocess wrapper is used.

### Requirement: Legacy Fallback SHALL Be Explicit And Migration-Only

Any remaining imported old runtime functions SHALL be isolated behind a clearly named migration fallback module.

#### Scenario: Runtime code inspected
- **WHEN** an engineer inspects `analysis_runtime/legacy.py`
- **THEN** the allowed fallback boundary is documented
- **AND** the public command runner does not load old runtime DB directly.

### Requirement: Status SHALL Expose Local Gate Contract

`run_analysis.py status` SHALL return local next-action guidance without restoring the old gate loop.

#### Scenario: Status command runs
- **WHEN** status is requested for a runtime DB
- **THEN** stdout includes `next_action`, `missing_prerequisites`, `execution_note`, `instruction_refs`, `quality_directives`, `warnings`, and `error`
- **AND** instruction refs point only to `literature-analysis/references/*.md`.
