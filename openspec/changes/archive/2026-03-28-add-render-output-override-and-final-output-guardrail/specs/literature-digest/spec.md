## MODIFIED Requirements

### Requirement: Artifact File Protocol

Artifacts MUST be written using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

The default output directory remains the directory of `source_path`, but the final render step MAY override the output directory explicitly without changing filenames.

#### Scenario: Default render output directory
- **WHEN** the final render step runs without an explicit output-directory override
- **THEN** `digest.md`, `references.json`, and `citation_analysis.json` are written beside `source_path`

#### Scenario: Render output directory override
- **WHEN** the final render step runs with an explicit output-directory override
- **THEN** the runtime writes the fixed artifact filenames into that directory
- **AND** the final stdout payload reports those actual artifact paths

## ADDED Requirements

### Requirement: Gate Payload SHALL Include Execution Notes

The gate payload SHALL include a short `execution_note` for the current action.

#### Scenario: Main-path action is ready
- **WHEN** the gate returns a ready main-path `next_action`
- **THEN** the payload includes a non-empty `execution_note`
- **AND** that note summarizes the most important execution constraint for the current action

### Requirement: Final Render Guidance SHALL Be Scoped To Stage 6 Gate Output

The instruction to directly adopt the render script stdout JSON as the final assistant output SHALL be delivered through the stage-6 gate note rather than a broader global rule.

#### Scenario: Gate advances to final render
- **WHEN** the gate returns `next_action = render_and_validate`
- **THEN** `execution_note` tells the agent to run render mode next
- **AND** `execution_note` tells the agent to directly use the render script stdout JSON as the final assistant output
