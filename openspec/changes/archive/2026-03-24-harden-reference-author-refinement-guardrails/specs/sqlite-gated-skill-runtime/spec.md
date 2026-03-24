## ADDED Requirements

### Requirement: Stage 4 Runtime SHALL Reject Invalid Author Boundary Refinement

The gate-driven runtime SHALL reject refined reference items that break stable prepared author boundaries.

#### Scenario: Oversplit author refinement reaches stage runtime
- **WHEN** `persist_references` receives a refined item that over-splits the selected candidate's `author_candidates`
- **THEN** the runtime returns `reference_author_refinement_invalid`
- **AND** records a `reference_author_oversplit_detected` warning for later inspection.
