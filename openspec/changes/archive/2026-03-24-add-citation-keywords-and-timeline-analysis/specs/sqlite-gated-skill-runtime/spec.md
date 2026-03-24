## MODIFIED Requirements

### Requirement: Stage 5 Runtime SHALL Gate Timeline Before Summary

The SQLite-gated runtime MUST treat timeline persistence as a required stage-5 step between item semantics and the global summary.

#### Scenario: Stage 5 action ordering
- **WHEN** gate evaluates the citation-analysis stage
- **THEN** the action order is `prepare_citation_workset`, `persist_citation_semantics`, `persist_citation_timeline`, `persist_citation_summary`, and then `render_and_validate`
- **AND** `persist_citation_summary` cannot succeed until timeline state exists.

#### Scenario: Stage 5 documentation is read
- **WHEN** the agent reads `SKILL.md`, `step_05_citation_pipeline.md`, `stage_runtime_interface.md`, or `gate_runtime_interface.md`
- **THEN** those docs describe `keywords` as required in citation semantics
- **AND** they describe `persist_citation_timeline` and the fixed bucket names `early`, `mid`, and `recent`
- **AND** they describe synthetic author-year labels as `[AY-k]` when no numeric citation number exists.
