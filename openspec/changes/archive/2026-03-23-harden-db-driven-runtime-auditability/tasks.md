## 1. OpenSpec

- [x] 1.1 Add `proposal.md`
- [x] 1.2 Add `design.md`
- [x] 1.3 Add `tasks.md`
- [x] 1.4 Add delta specs for `literature-digest`
- [x] 1.5 Add delta specs for `sqlite-gated-skill-runtime`

## 2. Runtime Hardening

- [x] 2.1 Make `normalize_source` read DB-authoritative source/language inputs only
- [x] 2.2 Make `prepare_citation_mentions` read DB-authoritative citation scope only
- [x] 2.3 Make `render_and_validate --mode render` reject explicit external input sources
- [x] 2.4 Add scope fallback audit metadata and stdout fields
- [x] 2.5 Add references numbering quality checks and warnings
- [x] 2.6 Add citation function normalization and warnings
- [x] 2.7 Add digest coverage checks and render-time semantic warning aggregation
- [x] 2.8 Add `export_citation_workset` as a read-only auxiliary helper

## 3. Guidance

- [x] 3.1 Add `references/runtime_playbook.md`
- [x] 3.2 Update gate/runtime interface docs
- [x] 3.3 Update step docs to reflect DB-authoritative later stages
- [x] 3.4 Update top-level skill/runtime documentation

## 4. Verification

- [x] 4.1 Update runtime and guidance tests for removed override interfaces
- [x] 4.2 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing pytest -q`
