# literature-analysis Delta Specification

## Requirements

### Requirement: Reference Guidance SHALL Be Stage Manuals

The five `literature-analysis/references/*.md` files SHALL provide detailed, stage-specific manuals rather than shallow summaries.

#### Scenario: Stage reference loaded
- **WHEN** an agent loads a stage reference file
- **THEN** it sees source-of-truth rules, payload shape, field semantics, legal examples, illegal examples or failure semantics, and recovery guidance for that stage.

### Requirement: Reference Extraction Guidance SHALL Preserve Old Quality Rules

`reference_extraction.md` SHALL preserve old reference extraction rules for bibliography formats, deterministic worksets, split review, file quality, reference quality gates, metadata enrichment, numbering quality, and render truth boundaries.

#### Scenario: Reference stage reviewed
- **WHEN** an agent reads `reference_extraction.md`
- **THEN** it can handle numeric, author-year, GB/T 7714, Bibitem, BibTeX, CJK/fullwidth, low-quality, placeholder-title, author-boundary, and metadata enrichment cases.

### Requirement: Citation Guidance SHALL Preserve Old Analysis Rules

`citation_analysis.md` SHALL preserve old citation rules for public schema, mention extraction, false-positive filtering, mapping, reference-free mode, function writing, timeline closure, summary basis, merge validation, and renderer-derived report content.

#### Scenario: Citation stage reviewed
- **WHEN** an agent reads `citation_analysis.md`
- **THEN** it can produce semantic items, timeline, summary, and basis without submitting `report_md` or overriding citation scope.

### Requirement: Old Gate Main Path SHALL Stay Out Of New References

The new references SHALL NOT instruct agents to use old gate scripts, SQL playbooks, or old runtime-only action loops as the normal `literature-analysis` path.

#### Scenario: Guidance inspected
- **WHEN** tests scan `literature-analysis/references/*.md`
- **THEN** old gate/script main-path strings are absent
- **AND** durable old validation terms remain present.
