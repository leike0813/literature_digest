# Tasks: improve-citation-analysis-guidance-and-summary-quality

- [x] 1. Tighten `persist_citation_semantics` validation to require `topic`, `usage`, and `is_key_reference`
- [x] 2. Tighten `persist_citation_summary` validation to require `basis.research_threads`, `basis.argument_shape`, and `basis.key_ref_indexes`
- [x] 3. Extend citation report rendering with `summary_basis` and a “Key References” section
- [x] 4. Update `SKILL.md`, `step_05_citation_pipeline.md`, and `stage_runtime_interface.md` with stronger stage-5 guidance and payload examples
- [x] 5. Add regression tests for the stricter stage-5 payloads and the new rendered section
- [x] 6. Record the change in OpenSpec delta specs
