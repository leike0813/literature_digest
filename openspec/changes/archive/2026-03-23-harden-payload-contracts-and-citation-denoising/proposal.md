## Why

Recent real runs showed that the runtime had become DB-first in code, but several examples and appendix docs still described looser or older payload shapes. That mismatch increases agent ambiguity, makes failures harder to recover, and leaves citation mention extraction too vulnerable to common markdown noise such as images, URLs, resource paths, and date strings.

## What Changes

- Align `persist_outline_and_scopes`, `persist_references`, and `persist_citation_semantics` documentation with the exact payload fields accepted by `stage_runtime.py`.
- Harden `persist_outline_and_scopes` validation so `outline_nodes`, `references_scope`, and `citation_scope` must use the runtime shape already implied by the DB schema.
- Extend `prepare_citation_workset` with deterministic false-positive filtering and a lightweight review export beside the full workset export.
- Standardize warning categories for low-confidence reference parsing, citation false-positive filtering, scope fallback, and digest undercoverage.
- Add failure recovery guidance and small regression fixtures so real-run regressions are easier to reproduce and debug.

## Capabilities

### New Capabilities

- `sqlite-gated-skill-runtime`: internal runtime contracts for strict payload validation, citation workset denoising, lightweight review export, warning taxonomy, and failure recovery guidance.

### Modified Capabilities

- `literature-digest`: payload examples, references extraction rules, citation denoising behavior, warning propagation, and execution guidance now follow the exact runtime contract.

## Impact

- Affected code: `literature-digest/scripts/stage_runtime.py`, `literature-digest/scripts/gate_runtime.py`
- Affected guidance: `literature-digest/SKILL.md`, `literature-digest/references/stage_runtime_interface.md`, `literature-digest/references/step_02_outline_and_scopes.md`, `literature-digest/references/step_04_references_extraction.md`, `literature-digest/references/step_05_citation_pipeline.md`, `literature-digest/references/step_06_render_and_validate.md`, `literature-digest/references/gate_runtime_interface.md`, new `literature-digest/references/failure_recovery.md`
- Affected tests: `tests/test_stage_runtime.py`, `tests/test_guidance_docs.py`, and a new small regression fixture set
