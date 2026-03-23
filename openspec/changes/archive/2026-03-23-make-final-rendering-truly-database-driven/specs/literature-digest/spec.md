## MODIFIED Requirements

### Requirement: Final Digest Rendering SHALL Consume Structured Slots

The skill MUST persist digest content as structured slots and section summaries before rendering the final markdown artifact.

#### Scenario: Persist digest stage
- **WHEN** `persist_digest` is called
- **THEN** it accepts `digest_slots` and `section_summaries`
- **AND** it rejects deprecated near-final `sections[]` input
- **AND** the final `digest.md` is rendered from stored structured digest content rather than agent-written markdown sections.

### Requirement: Final Citation Report SHALL Be Renderer-Derived

The skill MUST derive `citation_analysis.json.report_md` from structured citation database content during final rendering.

#### Scenario: Citation semantics persistence
- **WHEN** `persist_citation_semantics` is called
- **THEN** it persists citation batches, mapped items, and unmapped mentions
- **AND** it does not accept `report_md` as agent input.

#### Scenario: Citation report publication
- **WHEN** final citation artifacts are rendered
- **THEN** the renderer derives `report_md` from stored citation scope, mapped items, and unmapped mentions
- **AND** `citation_analysis.md` content MUST equal `citation_analysis.json.report_md` exactly.
