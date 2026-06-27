## MODIFIED Requirements

### Requirement: Citation workset preparation maps source citation mentions to references
The `literature-analysis` runtime SHALL prepare citation worksets by mapping source citation mentions to persisted references using deterministic local evidence. It SHALL support LaTeX citekeys, source-local bracket-alpha labels, numeric reference numbers, and author-year hints without requiring additional agent-submitted citation semantic fields.

#### Scenario: Alpha labels map to reference entries
- **WHEN** the source body contains `[RNSS18, DCLT18, YDY+19]` and the reference list contains matching bracket-alpha entries
- **THEN** citation workset preparation SHALL create mapped workset items for the matching references with `citation-label` mentions

#### Scenario: Original alpha label is preserved for rendering
- **WHEN** a citation item is mapped through a bracket-alpha label such as `[DCLT18]`
- **THEN** the rendered citation label SHALL use `[DCLT18]` rather than a generated author-year fallback

#### Scenario: Unknown alpha labels are not guessed
- **WHEN** the source body contains a bracket-alpha label that has no matching persisted reference alias
- **THEN** citation workset preparation SHALL NOT create a workset item for that label

#### Scenario: Duplicate alpha labels are ambiguous
- **WHEN** more than one persisted reference exposes the same normalized bracket-alpha label
- **THEN** mentions using that label SHALL remain unmapped and the runtime SHALL record a warning
