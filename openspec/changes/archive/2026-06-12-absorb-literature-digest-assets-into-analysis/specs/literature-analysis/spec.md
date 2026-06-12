# literature-analysis Delta Specification

## Requirements

### Requirement: Guidance SHALL Be Owned By literature-analysis

`literature-analysis` SHALL provide its own references for source planning, digest generation, reference extraction, citation analysis, and finalization.

#### Scenario: Skill entry indexes guidance
- **WHEN** an agent reads `literature-analysis/SKILL.md`
- **THEN** it can identify which `literature-analysis/references/*.md` file to read for each stage
- **AND** it is not instructed to read old `literature-digest` gate or SQL playbooks.

### Requirement: Runtime SHALL Prefer Local Domain Modules

`run_analysis.py` SHALL call local `analysis_runtime` modules for initialization, source normalization, reference workset preparation, and citation workset preparation.

#### Scenario: Reference workset preparation
- **WHEN** `persist_references` runs without a payload
- **THEN** the workset is prepared through local runtime modules
- **AND** the command does not spawn old `stage_runtime.py` as a subprocess.

#### Scenario: Citation workset preparation
- **WHEN** `persist_citation_analysis` runs without a payload
- **THEN** the workset is prepared through local runtime modules
- **AND** the command does not spawn old `stage_runtime.py` as a subprocess.

### Requirement: Output Compatibility SHALL Remain Unchanged

Absorbing guidance and runtime modules SHALL NOT change the public output contract.

#### Scenario: Final artifacts
- **WHEN** a full run completes
- **THEN** stdout still reports the same full-compatible artifact keys and fixed filenames.
