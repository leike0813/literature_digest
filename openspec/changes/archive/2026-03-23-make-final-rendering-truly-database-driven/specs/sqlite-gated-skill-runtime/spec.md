## MODIFIED Requirements

### Requirement: Stage Runtime SHALL Persist Structured Digest Content

The stage runtime MUST store digest content in structured slot form rather than near-final markdown-section form.

#### Scenario: Structured digest payload
- **WHEN** the runtime persists digest content
- **THEN** it writes `digest_slots` and `digest_section_summaries`
- **AND** the gate/runtime guidance refers to those tables as the active digest SSOT.

### Requirement: Final Rendering SHALL Be Database-Driven

The runtime renderer MUST build final public artifacts from structured database content rather than LLM-written final text fragments.

#### Scenario: Final render
- **WHEN** `render_and_validate --mode render` runs
- **THEN** digest markdown is rendered from structured digest rows
- **AND** citation report markdown is rendered from structured citation rows
- **AND** the runtime does not depend on a pre-written citation report row supplied by the agent.
