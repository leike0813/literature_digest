## 1. OpenSpec

- [x] 1.1 Add `proposal.md`
- [x] 1.2 Add `design.md`
- [x] 1.3 Add `tasks.md`
- [x] 1.4 Add delta specs for `literature-digest`
- [x] 1.5 Add delta specs for `sqlite-gated-skill-runtime`

## 2. Runtime

- [x] 2.1 Add citation workset tables and summary table to the SQLite runtime schema
- [x] 2.2 Rename `prepare_citation_mentions` to `prepare_citation_workset`
- [x] 2.3 Make citation workset preparation persist mentions, mention links, workset items, batches, and unmapped mentions
- [x] 2.4 Restrict `persist_citation_semantics` to ref-index keyed semantic payloads only
- [x] 2.5 Add `persist_citation_summary`
- [x] 2.6 Render final citation artifacts from workset + semantics + summary

## 3. Guidance

- [x] 3.1 Inline the minimal main-path playbook into `SKILL.md`
- [x] 3.2 Mark `references/` docs as on-demand appendices only
- [x] 3.3 Remove `references/runtime_playbook.md`
- [x] 3.4 Remove `references/rendering_contracts.md`
- [x] 3.5 Update stage/gate interface docs and citation/reference step docs
- [x] 3.6 Expand `SKILL.md` main-path guidance so each action is readable and self-explanatory
- [x] 3.7 Add a project-wide parameter glossary to `SKILL.md` and align appendix terminology to it
- [x] 3.8 Rewrite `SKILL.md` main-path guidance around script calls, payload meaning, and minimal examples
- [x] 3.9 Expand `stage_runtime_interface.md` into a payload-oriented interface manual

## 4. Verification

- [x] 4.1 Update runtime and guidance tests for the new action set and citation summary contract
- [x] 4.2 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing pytest -q`
