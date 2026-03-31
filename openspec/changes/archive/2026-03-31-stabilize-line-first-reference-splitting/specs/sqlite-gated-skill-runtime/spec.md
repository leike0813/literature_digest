## ADDED Requirements

### Requirement: Gate routes suspicious stage-4 boundaries through split review

The sqlite-gated runtime MUST route stage 4 through block-level split review when deterministic references splitting is suspicious.

#### Scenario: Stage 4 review path is required

- **WHEN** `prepare_references_workset` detects unstable reference boundaries
- **THEN** gate returns `next_action = persist_reference_entry_splits`
- **AND** the payload guidance refers to suspect blocks rather than a whole `entries[]` replacement
- **AND** `persist_references` is not the next action until split review succeeds
