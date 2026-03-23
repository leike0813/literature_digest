## 1. OpenSpec

- [x] 1.1 Add `proposal.md`
- [x] 1.2 Add `design.md`
- [x] 1.3 Add `tasks.md`
- [x] 1.4 Add delta specs for `literature-digest`
- [x] 1.5 Add delta specs for `sqlite-gated-skill-runtime`

## 2. Runtime Data Model

- [x] 2.1 Add active digest SSOT helpers for `digest_slots`
- [x] 2.2 Add active digest SSOT helpers for `digest_section_summaries`
- [x] 2.3 Stop treating `digest_sections` as the final digest truth source
- [x] 2.4 Stop treating LLM-written citation reports as the final citation truth source

## 3. Stage Runtime

- [x] 3.1 Change `persist_digest` to accept structured slot payloads only
- [x] 3.2 Reject deprecated `sections[]` digest payloads
- [x] 3.3 Change `persist_citation_semantics` to reject `report_md`
- [x] 3.4 Derive final citation report during `render_and_validate`

## 4. Templates And Contracts

- [x] 4.1 Update digest templates to consume structured slots
- [x] 4.2 Update citation report template to consume structured report context
- [x] 4.3 Update render-context schemas
- [x] 4.4 Update runtime guidance and interface docs
- [x] 4.5 Realign `references/step_01` through `references/step_06` with DB-truth and final render-stage publication semantics

## 5. Verification

- [x] 5.1 Update runtime DB tests
- [x] 5.2 Update stage runtime tests
- [x] 5.3 Update render / validation / guidance tests
- [x] 5.4 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`
- [x] 5.5 Run `conda run --no-capture-output -n DataProcessing pytest -q`
