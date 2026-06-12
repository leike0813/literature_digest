## 1. OpenSpec artifacts

- [x] 1.1 Create change directory for `rewrite-literature-digest-as-analysis`
- [x] 1.2 Add proposal, design, tasks, and `literature-analysis` delta spec

## 2. Skill skeleton

- [x] 2.1 Add `literature-analysis/SKILL.md`
- [x] 2.2 Document the agent-facing stages and reuse boundary
- [x] 2.3 Document output compatibility and subagent policy

## 3. Runtime skeleton

- [x] 3.1 Add `literature-analysis/scripts/runtime_db.py` as a compatibility wrapper
- [x] 3.2 Add `literature-analysis/scripts/run_analysis.py`
- [x] 3.3 Implement `init_runtime`
- [x] 3.4 Implement `persist_analysis_plan`
- [x] 3.5 Implement separate `persist_digest`
- [x] 3.6 Implement prepare/persist behavior for `persist_references`
- [x] 3.7 Implement prepare/persist behavior for `persist_citation_analysis`
- [x] 3.8 Implement `finalize_outputs`

## 4. Tests

- [x] 4.1 Add tests for runtime initialization and source normalization
- [x] 4.2 Add tests proving references can be prepared without digest payload
- [x] 4.3 Add tests for compatible final artifact output

## 5. Validation

- [x] 5.1 Run targeted tests for the new runtime
- [x] 5.2 Run existing related runtime/render tests
