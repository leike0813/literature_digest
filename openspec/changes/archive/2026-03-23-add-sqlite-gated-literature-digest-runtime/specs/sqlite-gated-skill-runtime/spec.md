## ADDED Requirements

### Requirement: Gate Runtime SHALL Control Execution

The skill runtime MUST use a gate script to determine the only legal next action from database state.

#### Scenario: Database missing
- **WHEN** the gate script runs before the runtime DB exists
- **THEN** it returns `bootstrap_runtime_db` as the next action
- **AND** it does not permit any later stage action.

#### Scenario: Illegal stage prerequisites
- **WHEN** the workflow state points to a stage whose prerequisite data is missing
- **THEN** the gate script returns a blocked state with repair instructions
- **AND** the skill does not continue execution until the DB is repaired.

### Requirement: State Machine SHALL Use Stage and Substep

The runtime database MUST persist workflow progress through both `current_stage` and `current_substep`.

#### Scenario: Ready next action
- **WHEN** the DB has valid data for the active stage
- **THEN** the gate script returns the persisted `next_action`
- **AND** it includes the current stage, substep, gate status, status summary, and resume packet.
