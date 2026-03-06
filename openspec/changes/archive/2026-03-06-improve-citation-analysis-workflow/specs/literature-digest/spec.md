## ADDED Requirements

### Requirement: Citation Analysis SHALL Follow Explicit Multi-Stage Workflow
For citation analysis generation, the system MUST follow an explicit staged workflow defined in `literature-digest/SKILL.md`: preprocess extraction, mention mapping/accounting, semantic aggregation, and final gate checks.

#### Scenario: Workflow order is enforced
- **WHEN** generating `citation_analysis.json`
- **THEN** semantic aggregation is executed only after preprocess extraction is available
- **AND** final output is produced only after mention-accounting checks run.

### Requirement: Citation Scope Decision SHALL Be Agent-Owned and Single-Object
`citation_scope` MUST be decided by LLM/agent (not by deterministic preprocess scripts), and represented as a single scope-definition object that can cover one or multiple review chapters.

#### Scenario: Multi-section review coverage
- **WHEN** review discourse spans both `Introduction` and `Related Work(s)`
- **THEN** the chosen `citation_scope` covers both sections rather than only one
- **AND** downstream preprocess runs strictly inside this provided scope.

#### Scenario: Parent-section child coverage
- **WHEN** `citation_scope` selects a parent review section that has child subsections
- **THEN** the scope includes all child-subsection content until the next heading of same-or-higher level
- **AND** under-coverage is treated as invalid scope and triggers fallback handling.

### Requirement: Mention Accounting Gate
The system MUST account for every extracted mention by placing it either in mapped `items[].mentions` or in `unmapped_mentions`, and MUST NOT silently drop mentions.

#### Scenario: Full mention accounting
- **WHEN** preprocess extracts N citation mentions in `citation_scope`
- **THEN** the final citation-analysis structure contains exactly N consumed mention records across mapped and unmapped groups
- **AND** no extracted mention is omitted from both groups.

### Requirement: Semantic Tasks MUST Be Grounded on Preprocess Evidence
After preprocess, semantic tasks MUST use preprocess outputs and local snippets as primary evidence. Mapping decisions MUST prefer deterministic cues first and MUST fall back to `unmapped_mentions` when confidence is insufficient.

#### Scenario: Ambiguous author-year mapping
- **WHEN** an author-year mention has multiple plausible reference candidates
- **THEN** the system records the mention in `unmapped_mentions` with a reason code
- **AND** the system does not force a low-confidence hard mapping.

### Requirement: Fallback Behavior for Boundary Cases
`literature-digest/SKILL.md` MUST define deterministic fallback behavior for boundary cases including missing/invalid `citation_scope`, missing references, parse failures, and gate-check failures.

#### Scenario: References unavailable
- **WHEN** references cannot be loaded for mapping
- **THEN** citation mentions are still extracted from provided `citation_scope`
- **AND** mentions that cannot be mapped are emitted through `unmapped_mentions` rather than dropped.

#### Scenario: Gate check failure
- **WHEN** mention-accounting gate fails
- **THEN** the system returns a schema-compatible output with a populated `error`
- **AND** avoids returning a false-success citation-analysis result.
