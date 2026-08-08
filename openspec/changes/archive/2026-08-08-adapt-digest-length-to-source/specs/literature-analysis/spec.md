## ADDED Requirements

### Requirement: Digest Depth SHALL Adapt To Source Length And Information Density

The `literature-analysis` agent SHALL choose digest depth from the normalized source's substantive length and information density. Numeric item ranges SHALL be treated as soft writing guidance rather than validation limits, and the runtime SHALL preserve the existing structured payload and coverage validation behavior.

#### Scenario: Ordinary paper uses the normal depth

- **WHEN** the normalized source is an ordinary journal or conference paper with a conventional number of substantive sections and findings
- **THEN** the agent produces a digest near the documented reference ranges
- **AND** it does not expand the digest merely to consume an available range

#### Scenario: Long information-dense source expands

- **WHEN** the normalized source contains substantially more grounded methods, experiments, results, limitations, chapters, or independent subtopics
- **THEN** the agent expands the relevant digest slot items and section summaries to preserve those distinctions
- **AND** it may exceed the documented soft reference ranges without causing a validation error or warning solely because of item count

#### Scenario: Long but sparse source does not inflate mechanically

- **WHEN** a source is long because of layout, appendices, repeated material, or other low-density content
- **THEN** the agent bases digest depth on substantive evidence rather than page, character, or line thresholds
- **AND** it avoids padding, synonymous bullets, repeated claims, and unsupported detail
