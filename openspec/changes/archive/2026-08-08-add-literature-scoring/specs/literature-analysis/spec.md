## ADDED Requirements

### Requirement: Literature Analysis SHALL Include A Scoring Stage

The normal `literature-analysis` workflow SHALL route from digest persistence to literature scoring before reference extraction and SHALL include the score artifact in final output.

#### Scenario: Digest completes in normal mode
- **WHEN** `persist_digest` succeeds with `score_only=false`
- **THEN** the next agent-facing action is `persist_literature_score`.

#### Scenario: Scoring completes in normal mode
- **WHEN** `persist_literature_score` accepts a valid payload
- **THEN** the next agent-facing action is `persist_references`
- **AND** the eventual full stdout contains a non-empty absolute `literature_score_path`.

### Requirement: Literature Analysis SHALL Support Score-Only Runs

The Skill SHALL accept a boolean `score_only` parameter with default `false` and SHALL persist the selected mode at initialization.

#### Scenario: Score-only run initializes
- **WHEN** `init_runtime` receives `score_only=true`
- **THEN** source normalization still completes
- **AND** the next agent-facing action is `persist_literature_score`
- **AND** analysis planning and digest generation are skipped.

#### Scenario: Score-only run succeeds
- **WHEN** scoring succeeds in a score-only run
- **THEN** `literature_score_path` is a non-empty absolute path
- **AND** `digest_path`, `references_path`, `citation_analysis_path`, and `literature_matching_metadata_path` are empty strings
- **AND** `citation_analysis_report_path` is absent.

#### Scenario: Disallowed score-only action is invoked
- **WHEN** a score-only run invokes analysis plan, digest, references, or citation analysis
- **THEN** the runtime returns `mode_action_not_allowed`
- **AND** keeps `next_action = "persist_literature_score"` until scoring succeeds.

### Requirement: Skill Guidance SHALL Preserve Existing Instructions

The scoring change SHALL add only the main-path instructions required to execute scoring and SHALL route detailed scoring semantics, examples, and techniques to a dedicated reference document.

#### Scenario: Agent reads SKILL.md
- **WHEN** the updated Skill is loaded
- **THEN** it contains the scoring input/output contract, command, stage order, hard constraints, and failure routing needed to execute the current workflow
- **AND** existing instructions unrelated to the new workflow remain unchanged.

#### Scenario: Agent enters scoring
- **WHEN** scoring is the current action
- **THEN** the Skill directs the agent to the dedicated scoring reference and runtime-generated scoring context for detailed guidance.

