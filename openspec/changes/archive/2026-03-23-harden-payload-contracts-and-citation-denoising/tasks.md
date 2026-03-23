## 1. Runtime contract hardening

- [x] 1.1 Tighten `persist_outline_and_scopes` validation to the runtime shape for `outline_nodes`, `references_scope`, and `citation_scope`
- [x] 1.2 Tighten `persist_references` minimum accepted fields and propagate conservative parsing / year normalization warnings
- [x] 1.3 Keep `persist_citation_semantics` aligned with the existing ref-index keyed contract and legacy-field rejection

## 2. Citation denoising and review export

- [x] 2.1 Add deterministic mention filters for markdown image links, URLs, resource paths, image/PDF suffixes, and date-like strings
- [x] 2.2 Emit `citation_false_positive_filtered` and related scope / digest warning categories through runtime warnings
- [x] 2.3 Add a lightweight citation review export beside the full workset export

## 3. Guidance and recovery docs

- [x] 3.1 Align `SKILL.md` and `stage_runtime_interface.md` examples with the exact script payload fields
- [x] 3.2 Update `step_02`, `step_04`, `step_05`, and `step_06` with hardened payload, conservative references, denoising, and warning guidance
- [x] 3.3 Add `references/failure_recovery.md` and reference it from repair-oriented guidance

## 4. Verification

- [x] 4.1 Add or update runtime tests for payload validation, denoising, lightweight workset export, and reference year normalization
- [x] 4.2 Add a 4-fixture small regression corpus and verify the gate can reach render
- [x] 4.3 Run `mypy literature-digest/scripts` and `pytest -q`
