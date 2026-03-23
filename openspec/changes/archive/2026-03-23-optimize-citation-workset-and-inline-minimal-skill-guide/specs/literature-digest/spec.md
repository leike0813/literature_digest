## MODIFIED Requirements

### Requirement: Citation Semantics SHALL Consume A Prepared Workset

The skill MUST prepare mention-to-reference associations in SQLite before the agent writes citation semantics.

#### Scenario: Prepare citation workset
- **WHEN** `prepare_citation_workset` runs
- **THEN** it persists extracted mentions, mention links, grouped workset items, unmapped mentions, and citation batches
- **AND** later semantic analysis reads those persisted workset rows instead of rebuilding mention-reference joins.

#### Scenario: Persist citation semantics
- **WHEN** `persist_citation_semantics` runs
- **THEN** it accepts ref-index keyed semantic items only
- **AND** it rejects mention lists, reference snapshots, and `report_md` payload content.

### Requirement: Citation Analysis SHALL Include A Required Global Summary

The final citation analysis artifact MUST include a required top-level summary synthesized from the itemized analysis.

#### Scenario: Persist citation summary
- **WHEN** `persist_citation_summary` runs
- **THEN** it persists a non-empty `summary`
- **AND** final rendering reads that summary from SQLite.

#### Scenario: Publish final citation artifacts
- **WHEN** final citation artifacts are rendered
- **THEN** `citation_analysis.json` includes required `summary`
- **AND** `citation_analysis.json.report_md` and `citation_analysis.md` are rendered from stored summary plus structured citation data.

### Requirement: SKILL.md SHALL Be Minimally Executable

`SKILL.md` MUST be sufficient for executing the main path without preloading the entire appendix directory.

#### Scenario: Reading discipline
- **WHEN** an agent starts the skill
- **THEN** it can derive the main execution path from `SKILL.md`
- **AND** it treats `references/` docs as on-demand appendix material selected by gate `instruction_refs`
- **AND** it does not need `references/runtime_playbook.md` or `references/rendering_contracts.md`.

#### Scenario: Main-path guidance is script-oriented
- **WHEN** `SKILL.md` describes a main-path action
- **THEN** it documents the script call, the required payload or parameters, and a minimal valid example
- **AND** it does not rely on DB table descriptions as the primary way to guide execution.

#### Scenario: Shared terminology is payload-oriented
- **WHEN** `SKILL.md` defines glossary entries
- **THEN** it defines payload and parameter names that agents must fill correctly
- **AND** appendix docs reuse those definitions instead of redefining them independently.
