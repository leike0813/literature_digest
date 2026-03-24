# Tasks: add-reference-preparse-workset

- [x] 1. Add `reference_parse_candidates` schema and runtime DB helpers
- [x] 2. Add `prepare_references_workset` and convert stage 4 to prepare -> persist
- [x] 3. Rewrite `persist_references` to accept only refined items with `entry_index` and `selected_pattern`
- [x] 4. Update gate stage ordering, prerequisites, and SQL examples
- [x] 5. Update `SKILL.md`, runtime interface docs, gate docs, and step 4 guidance
- [x] 6. Add tests for multi-pattern preparse, candidate validation, title-boundary rejection, and DB roundtrip
