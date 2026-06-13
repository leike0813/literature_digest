## ADDED Requirements

### Requirement: Skill SHALL Prohibit Temporary Scripts For Semantic Review

The skill SHALL explicitly prohibit using ad hoc scripts to replace LLM judgment for digest writing, reference core review, metadata enrichment, and citation semantic analysis.

#### Scenario: Helper script is allowed
- **WHEN** a script only serializes already-reviewed decisions, checks JSON syntax, counts stable keys, or invokes `run_analysis.py`
- **THEN** it is allowed as deterministic support.

#### Scenario: Temporary script replaces semantic work
- **WHEN** a script infers reference authors, titles, years, metadata, citation topics, citation usage, summaries, or representative image judgment
- **THEN** the skill guidance marks that as forbidden.

### Requirement: Delegatable Tasks SHALL Have Named Delegation Points

The skill SHALL name the exact task points where subagents should be used by default.

#### Scenario: Reference prepare returns core review batches
- **WHEN** `persist_references` prepare returns `batch_work_packages`
- **THEN** the main agent uses the Reference Core Review delegation prompt unless delegation is unavailable or unsuitable.

#### Scenario: Core references return metadata batches
- **WHEN** core `reference_reviews[]` submit returns `metadata_review_packages` and metadata `batch_work_packages`
- **THEN** the main agent uses the Metadata Enrichment delegation prompt unless delegation is unavailable or unsuitable.

#### Scenario: Citation prepare returns semantic batches
- **WHEN** `persist_citation_analysis` prepare returns citation `batch_work_packages`
- **THEN** the main agent uses the Citation Semantic Review delegation prompt unless delegation is unavailable or unsuitable.
