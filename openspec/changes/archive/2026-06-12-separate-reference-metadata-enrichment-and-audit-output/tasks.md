## 1. OpenSpec

- [x] 1.1 Create proposal, design, spec delta, and task checklist.

## 2. Runtime

- [x] 2.1 Reject `reference_reviews[].metadata` and keep core reference payload metadata-free.
- [x] 2.2 Make valid core reference submit return metadata review packages and keep `next_action = persist_references`.
- [x] 2.3 Implement metadata review submit keyed by `reference_key`, with full coverage validation and alias normalization warnings.
- [x] 2.4 Move metadata allowed/locked fields to instruction-level workset/JIT payloads.
- [x] 2.5 Filter public references render output to remove audit fields.
- [x] 2.6 Generate tmp reference parse audit sidecar.

## 3. Guidance

- [x] 3.1 Update `SKILL.md` reference stage to document prepare, core submit, and metadata submit.
- [x] 3.2 Update `reference_extraction.md` examples and subagent prompts for the split contract.
- [x] 3.3 Document public artifact vs tmp audit sidecar boundaries.

## 4. Tests

- [x] 4.1 Add runtime tests for core metadata rejection and metadata review round trip.
- [x] 4.2 Add render tests for public reference filtering and audit sidecar.
- [x] 4.3 Add guidance tests for current-state reference payload examples.
- [x] 4.4 Run targeted runtime, guidance, render, and OpenSpec validation.
