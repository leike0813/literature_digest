## ADDED Requirements

### Requirement: Skill SHALL Define Global Subagent Delegation Contract

`literature-analysis` SHALL document subagent delegation as a global execution contract for batchable review work.

#### Scenario: Batchable work and subagents are available
- **WHEN** runtime returns `batch_work_packages`
- **AND** the execution environment supports subagents
- **AND** the work is reference core review, metadata enrichment, or citation semantic review
- **THEN** the main agent defaults to delegating batches to subagents.

#### Scenario: Delegation is skipped
- **WHEN** the main agent does not delegate batchable work
- **THEN** the reason is retained in execution notes or review notes.

### Requirement: Main Agent SHALL Remain Single Writer

Subagents SHALL only produce draft JSON for their assigned batch.

#### Scenario: Subagent batch work
- **WHEN** a subagent reviews a batch
- **THEN** it returns only the documented draft array for that batch
- **AND** it does not write DB, run runtime commands, submit payloads, modify stable keys, fill internal audit fields, or generate final artifacts.

### Requirement: Runtime JIT SHALL Reinforce Delegation Contract

Runtime prepare/status payloads SHALL include delegation policy and merge contract guidance that matches the global contract.

#### Scenario: Reference or citation prepare output
- **WHEN** prepare returns batch work packages
- **THEN** the payload includes `subagent_policy`, `batch_work_packages[].subagent_prompt`, and `merge_contract.single_writer = "main_agent"`.

#### Scenario: Status guidance
- **WHEN** `status` returns field guidance for a batchable stage
- **THEN** `field_guidance.subagents` states the default-to-delegate policy and main-agent single-writer rule.
