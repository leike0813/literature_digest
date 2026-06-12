# literature-analysis Delta Specification

## Requirements

### Requirement: Skill Entry SHALL Contain A Full Execution Contract

`literature-analysis/SKILL.md` SHALL define the background automation constraints, input/output contract, SQLite SSOT discipline, LLM/script responsibility boundary, unified parameter vocabulary, and six stage cards needed to run the skill.

#### Scenario: Agent starts a run
- **WHEN** an agent reads `literature-analysis/SKILL.md`
- **THEN** it can identify the required input payload, stdout keys, fixed artifact names, runtime SSOT rules, and next command sequence
- **AND** it does not need to consult old `literature-digest/SKILL.md` for the normal run contract.

### Requirement: Stage Cards SHALL Match The Six Analysis Stages

The entry contract SHALL describe `init_runtime`, `persist_analysis_plan`, `persist_digest`, `persist_references`, `persist_citation_analysis`, and `finalize_outputs`.

#### Scenario: Stage card read
- **WHEN** an agent reaches a stage card
- **THEN** the card states when to execute it, the command, source of truth, required payload, field meanings, a minimal legal example, success condition, and key failure branches.

### Requirement: References SHALL Preserve High-Risk Old Rules

The `literature-analysis/references/` files SHALL preserve rewritten old rules for normalization, scope selection, digest structure, representative image evidence, reference quality gates, bibliography formats, citation denoising, semantic function labeling, timeline closure, summary basis, and final render validation.

#### Scenario: Reference extraction guidance read
- **WHEN** the agent reads `reference_extraction.md`
- **THEN** it sees pattern selection, split review, CJK/type-marker handling, placeholder-title rejection, author-boundary validation, metadata enrichment, and representative examples.

#### Scenario: Citation analysis guidance read
- **WHEN** the agent reads `citation_analysis.md`
- **THEN** it sees mention extraction, false-positive filtering, numeric/author-year/LaTeX mapping, reference-free mode, function examples, timeline closure, and renderer-derived `report_md` rules.

### Requirement: Old Gate Main Path SHALL NOT Be Reintroduced

The new guidance SHALL NOT require the old gate loop or direct old runtime script calls as the normal `literature-analysis` main path.

#### Scenario: Guidance regression check
- **WHEN** tests inspect `literature-analysis` guidance
- **THEN** old gate-only requirements such as rerunning gate after every write or executing only a returned `next_action` are absent
- **AND** normal instructions use `literature-analysis/scripts/run_analysis.py`.
