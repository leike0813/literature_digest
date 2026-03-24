## MODIFIED Requirements

### Requirement: Stage 5 Guidance SHALL Constrain Semantic Payload Quality

The gate-driven runtime documentation MUST make the stricter stage-5 payload contract explicit so agents do not stop at generic function labels.

#### Scenario: Stage 5 guidance is read
- **WHEN** the agent reads `SKILL.md`, `step_05_citation_pipeline.md`, or `stage_runtime_interface.md` for stage 5
- **THEN** those docs describe `topic`, `usage`, and `is_key_reference` as required citation-semantic fields
- **AND** they describe `basis.research_threads`, `basis.argument_shape`, and `basis.key_ref_indexes` as required summary inputs
- **AND** they explicitly forbid agent-authored `report_md`.

#### Scenario: Stage 5 completes successfully
- **WHEN** gate evaluates the transition after `persist_citation_summary`
- **THEN** it only allows render to proceed after the structured citation summary has been stored
- **AND** the runtime can derive the final report from DB state alone.
