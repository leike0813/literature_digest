## MODIFIED Requirements

### Requirement: Gate Actions SHALL Map Directly To Stage Runtime Subcommands

The gate payload MUST return `next_action` values that are directly executable through the unified stage runtime entrypoint.

#### Scenario: Gate returns a ready action
- **WHEN** `gate_runtime.py` returns `stage_gate = ready`
- **THEN** `next_action` equals a supported `stage_runtime.py` subcommand
- **AND** the caller does not need an intermediate action-to-script translation layer.

### Requirement: Consolidated Runtime SHALL Not Preserve Legacy CLI Wrappers

Removed standalone runtime scripts MUST NOT remain as compatibility wrappers after the consolidation.

#### Scenario: Runtime entrypoints after consolidation
- **WHEN** the runtime is inspected after the consolidation
- **THEN** stage execution is centered on `stage_runtime.py`
- **AND** legacy standalone entry scripts are absent rather than thinly forwarding into the new entrypoint.
