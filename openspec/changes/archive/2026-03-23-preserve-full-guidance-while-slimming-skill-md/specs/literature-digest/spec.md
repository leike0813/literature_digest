## ADDED Requirements

### Requirement: Guidance Refactors SHALL Preserve Detailed Content

When detailed guidance is moved out of `SKILL.md`, the skill repository MUST preserve that content in external docs instead of replacing it with summaries.

#### Scenario: Long-form guidance migrated
- **WHEN** `SKILL.md` is slimmed down
- **THEN** the removed detailed instructions, examples, and templates remain present elsewhere in the skill package
- **AND** the refactor does not discard their operational content.

### Requirement: SKILL Contract SHALL Be Concise But Indexed

`SKILL.md` MAY remain concise, but it MUST include an explicit index to the rich external guidance docs.

#### Scenario: Agent reads SKILL.md
- **WHEN** an agent starts from `SKILL.md`
- **THEN** it can locate the detailed stage/topic guidance through explicit links
- **AND** those links point to docs that contain the preserved full detail.
