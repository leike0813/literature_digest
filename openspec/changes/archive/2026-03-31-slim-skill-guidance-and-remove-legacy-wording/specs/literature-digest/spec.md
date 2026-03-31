## ADDED Requirements

### Requirement: Active guidance stays focused on the current contract

Agent-facing literature-digest guidance MUST describe the current runtime contract without teaching historical payload migrations.

#### Scenario: Guidance uses current-contract wording

- **WHEN** `SKILL.md` or active stage guidance explains a stage payload or execution rule
- **THEN** it describes the currently accepted structure directly
- **AND** it does not rely on “old payload”, “legacy interface”, or similar historical comparison wording

### Requirement: SKILL.md remains compact at the step level

The main `SKILL.md` guidance MUST avoid per-step “common mistakes” blocks.

#### Scenario: Stage sections omit common-mistake lists

- **WHEN** a reader follows the per-step sections in `SKILL.md`
- **THEN** each step keeps the execution essentials
- **AND** it does not include a `本步最常见错误` subsection
