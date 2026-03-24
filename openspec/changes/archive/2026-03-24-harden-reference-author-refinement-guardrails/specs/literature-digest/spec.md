## ADDED Requirements

### Requirement: References Refinement SHALL Preserve Prepared Author Boundaries

When stage 4 already prepared stable author boundaries, the final references refinement step SHALL preserve those boundaries.

#### Scenario: Prepared author boundaries are reused
- **WHEN** `persist_references` receives an item whose selected candidate already provides stable `author_candidates`
- **THEN** the submitted `author[]` may reuse or lightly normalize those prepared boundaries
- **AND** the runtime writes the final `reference_items`.

#### Scenario: Prepared author boundaries are split again
- **WHEN** `persist_references` receives an item whose submitted `author[]` splits one prepared candidate author into multiple elements
- **THEN** the runtime fails with `reference_author_refinement_invalid`
- **AND** it does not publish malformed `reference_items`.
