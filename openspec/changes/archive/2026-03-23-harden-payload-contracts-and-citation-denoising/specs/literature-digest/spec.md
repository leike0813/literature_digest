## ADDED Requirements

### Requirement: References extraction follows a conservative structured contract
The skill SHALL accept references persistence payloads only when they provide the runtime minimum structure for raw entries, batch ranges, and structured items.

#### Scenario: Conservative reference parsing remains valid
- **WHEN** `persist_references` receives an item whose author parsing is unstable
- **THEN** the item may keep `author` as a single-element array
- **AND** the runtime MUST preserve `raw`, `title`, `year`, and `confidence`

### Requirement: Citation mention extraction filters deterministic markdown noise
The skill SHALL filter deterministic false-positive citation markers before citation workset persistence.

#### Scenario: Noise-like markdown tokens are filtered
- **WHEN** `prepare_citation_workset` scans a citation scope containing image links, URLs, resource paths, image/PDF suffix tokens, or date-like strings
- **THEN** those candidates MUST NOT be stored as citation mentions
- **AND** the runtime MUST emit `citation_false_positive_filtered` when at least one candidate is filtered

### Requirement: Citation workset exports include a lightweight review view
The skill SHALL expose a compact review view alongside the full citation workset export.

#### Scenario: Lightweight review export is generated
- **WHEN** `prepare_citation_workset` or `export_citation_workset` exports the workset
- **THEN** the runtime MUST also generate a review view containing only `ref_index`, `title`, `mention_count`, and `snippets`

## MODIFIED Requirements

### Requirement: Skill guidance remains executable and aligned with the runtime
The skill SHALL document the main path and runtime payloads using the exact fields accepted by the scripts.

#### Scenario: Guidance examples match runtime payloads
- **WHEN** `SKILL.md`, `stage_runtime_interface.md`, and the step appendices describe `persist_outline_and_scopes`, `persist_references`, or `persist_citation_semantics`
- **THEN** their examples MUST use the exact payload fields accepted by `stage_runtime.py`
- **AND** they MUST NOT present looser conceptual shapes as valid runtime payloads

### Requirement: Warning categories are standardized for parsing and denoising
The skill SHALL use stable warning categories for the most common non-blocking quality issues.

#### Scenario: Non-blocking runtime quality issues are categorized
- **WHEN** the runtime detects low-confidence reference parsing, citation false-positive filtering, scope fallback, or digest undercoverage
- **THEN** it MUST emit stable warning categories that can appear in DB warnings, stdout warnings, or artifact metadata as appropriate
