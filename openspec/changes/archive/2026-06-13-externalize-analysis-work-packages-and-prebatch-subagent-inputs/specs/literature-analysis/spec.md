## ADDED Requirements

### Requirement: Prepare Output SHALL Externalize Large Work Packages

Reference and citation prepare responses SHALL return paths and counts instead of inlining large work package arrays.

#### Scenario: Reference core prepare
- **WHEN** `persist_references` prepare succeeds
- **THEN** stdout includes `reference_core_review_manifest_path`, `reference_core_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `reference_review_packages` or `batch_work_packages`.

#### Scenario: Metadata prepare after core submit
- **WHEN** core `reference_reviews[]` submit succeeds
- **THEN** stdout includes `metadata_review_manifest_path`, `metadata_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `metadata_review_packages` or `batch_work_packages`.

#### Scenario: Citation prepare
- **WHEN** `persist_citation_analysis` prepare succeeds
- **THEN** stdout includes `citation_semantic_review_manifest_path`, `citation_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `citation_work_packages` or `batch_work_packages`.

### Requirement: Runtime SHALL Precut Subagent Batch Files

Runtime SHALL write subagent batch files with at most 10 work items per batch.

#### Scenario: Batch file content
- **WHEN** a batch file is written
- **THEN** it includes `batch_id`, `batch_kind`, `input_package_path`, stable keys, package subset, allowed enum subset, required return shape, forbidden fields, subagent prompt, merge notes, and `suggested_draft_output_path`.

### Requirement: Guidance SHALL Use Path-Based Delegation

The skill guidance SHALL instruct the main agent to pass batch JSON file paths to subagents and SHALL prohibit manual splitting of full worksets.

#### Scenario: Subagent delegation
- **WHEN** runtime returns batch paths
- **THEN** the main agent delegates those paths directly
- **AND** the subagent reads only its assigned batch JSON file.
