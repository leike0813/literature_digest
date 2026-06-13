## 1. OpenSpec

- [x] 1.1 Create proposal, design notes, delta spec, and task checklist.

## 2. Runtime

- [x] 2.1 Add token conservation helpers for split review source/corrected text.
- [x] 2.2 Replace exact split text equality with token conservation diagnostics.
- [x] 2.3 Downgrade post-review suspect blocks to warnings after conservation succeeds.
- [x] 2.4 Write split review audit data to tmp runtime sidecar.
- [x] 2.5 Keep public CLI and payload shape unchanged.

## 3. Guidance

- [x] 3.1 Update `SKILL.md` split review guidance for token conservation and warning downgrade.
- [x] 3.2 Update `reference_extraction.md` split review rules and web/resource missing year guidance.
- [x] 3.3 Ensure docs do not mention `accept_reviewed_entries`.

## 4. Tests

- [x] 4.1 Add runtime tests for tolerated Unicode/punctuation/whitespace differences.
- [x] 4.2 Add runtime tests for missing token diagnostics.
- [x] 4.3 Add runtime test for post-review heuristic warning downgrade.
- [x] 4.4 Add guidance tests for token coverage and warning downgrade.
- [x] 4.5 Run targeted runtime, guidance, render, and OpenSpec validation.
