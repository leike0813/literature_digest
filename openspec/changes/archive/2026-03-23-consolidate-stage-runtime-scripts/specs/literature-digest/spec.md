## MODIFIED Requirements

### Requirement: SQLite Runtime SHALL Expose A Unified Stage Executor

The skill runtime MUST expose a single stage-action CLI entrypoint that executes deterministic work for every gate-approved step.

#### Scenario: Agent executes a legal next action
- **WHEN** the gate returns a stage action such as `normalize_source`, `persist_references`, or `render_and_validate`
- **THEN** the action is executed through `literature-digest/scripts/stage_runtime.py`
- **AND** the action name maps directly to a `stage_runtime.py` subcommand.

### Requirement: Runtime Guidance SHALL Describe The Three-Layer Execution Model

The published skill guidance MUST describe runtime execution in terms of gate orchestration, stage execution, and DB access.

#### Scenario: Agent reads runtime guidance
- **WHEN** the agent reads `SKILL.md` and the referenced runtime docs
- **THEN** the guidance describes `gate_runtime.py`, `stage_runtime.py`, and `runtime_db.py`
- **AND** it does not require removed standalone runtime entry scripts.
