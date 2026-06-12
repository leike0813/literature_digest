# literature-analysis Delta Specification

## Requirements

### Requirement: Assets SHALL Describe Only The Current Runtime

`literature-analysis` assets and guidance SHALL describe the current `scripts/run_analysis.py` workflow and SHALL NOT instruct agents to use old gate/stage scripts.

#### Scenario: Runner asset is read
- **WHEN** a runner reads `assets/runner.json`
- **THEN** it identifies the skill as `literature-analysis`
- **AND** its prompt instructs the six current `run_analysis.py` stages.

### Requirement: Reference Split Review SHALL Be Executable

`persist_references` submit SHALL accept `split_reviews[]` and map them to deterministic entry split persistence.

#### Scenario: Split repair changes boundaries
- **WHEN** a payload contains boundary-changing `split_reviews[]`
- **THEN** runtime persists the split repair
- **AND** returns regenerated reference review packages instead of persisting stale reference reviews.

#### Scenario: Split repair is invalid
- **WHEN** a payload contains invalid split review fields
- **THEN** runtime returns all common split review validation errors in one response.

### Requirement: Skill Package SHALL Exclude Bytecode

The `literature-analysis` skill package SHALL NOT contain Python bytecode or `__pycache__` directories.
