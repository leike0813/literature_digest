# Tasks: add-citation-keywords-and-timeline-analysis

- [x] 1. Add `citation_timeline` storage and fetch/render helpers in the runtime DB layer
- [x] 2. Extend `persist_citation_semantics` to require and normalize `keywords`
- [x] 3. Add `persist_citation_timeline` and update the stage-5 gate order
- [x] 4. Render richer citation entries with `citation_label`, `author_year_label`, `title`, and `keywords`
- [x] 5. Replace the old ordered-citation section with timeline analysis in the Markdown report
- [x] 6. Update `SKILL.md`, `step_05_citation_pipeline.md`, `stage_runtime_interface.md`, and `gate_runtime_interface.md`
- [x] 7. Add regression tests for keywords, timeline validation, synthetic `[AY-k]` labels, and the new report layout
