## ADDED Requirements

### Requirement: Runtime Entry SHALL Bootstrap Local Imports

`literature-analysis` runtime entry SHALL make direct script-path invocation work without requiring callers to preconfigure `PYTHONPATH`.

#### Scenario: Direct script invocation
- **WHEN** `python literature-analysis/scripts/run_analysis.py <stage>` is executed from outside the scripts directory
- **THEN** `run_analysis.py` imports `analysis_runtime` successfully
- **AND** returns the normal stage stdout JSON.

### Requirement: Payload Read Failures SHALL Return Structured JSON

Submit stages SHALL convert payload file read failures into schema-compatible JSON errors instead of Python tracebacks.

#### Scenario: Invalid JSON payload
- **WHEN** a submit stage receives a payload file that is not valid JSON
- **THEN** stdout contains exactly one JSON object
- **AND** the error code is `payload_json_invalid`
- **AND** the error includes the stage, payload file, line, column, and repair hint.

#### Scenario: Unreadable payload file
- **WHEN** a submit stage receives a missing or unreadable payload file
- **THEN** stdout contains exactly one JSON object
- **AND** the error code is `payload_file_unreadable`.

### Requirement: Subagent Work Packages SHALL Specify Canonical Batch Contracts

Reference, metadata, and citation prepare/JIT payloads SHALL include enough batch contract detail for subagents to draft canonical current-state payloads without using internal DB fields.

#### Scenario: Reference prepare returns batch guidance
- **WHEN** `persist_references` prepare succeeds
- **THEN** the response includes batch work packages with stable batch ids, stable reference keys, canonical metadata fields, forbidden fields, allowed parse pattern guidance, a minimal valid draft example, and merge guidance.

#### Scenario: Citation prepare returns batch guidance
- **WHEN** `persist_citation_analysis` prepare succeeds
- **THEN** the response includes batch work packages with stable citation work keys, forbidden internal fields, a minimal valid draft example, and merge guidance.

### Requirement: Reference Metadata SHALL Normalize Deterministic Aliases

Reference submit handlers SHALL normalize deterministic metadata aliases from reference reviews and metadata reviews, and SHALL report warnings for normalization or unknown metadata fields.

#### Scenario: Metadata alias normalized
- **WHEN** a reference payload includes metadata such as `journal`, `doi`, or a bare arXiv id
- **THEN** the persisted metadata uses canonical fields such as `publicationTitle`, `DOI`, and `archiveID`
- **AND** the stage response includes normalization warnings.

#### Scenario: Unknown metadata field
- **WHEN** a reference payload includes a metadata field outside the supported canonical set and aliases
- **THEN** the stage does not fail solely for that field
- **AND** the stage response includes a warning identifying the unrecognized field.

### Requirement: Skill Guidance SHALL Remain Portable

Formal `literature-analysis` guidance SHALL use portable bare-Python runtime commands and SHALL NOT present repository-local `uv` or `$HOME/.ar` commands as the skill execution contract.

#### Scenario: Agent reads skill guidance
- **WHEN** an agent reads `SKILL.md`, references, or assets
- **THEN** formal runtime examples use `python`
- **AND** they do not require `uv run --project` or `$HOME/.ar`.
