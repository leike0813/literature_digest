## Why

The current SQLite + template runtime still leaves a gap between “structured process data” and “final artifact rendering”.

In practice:

- digest persistence still resembled storing near-final markdown sections,
- citation semantics still expected the agent to provide `report_md`,
- and the template layer often acted more like a light wrapper around LLM-written final text than a true renderer.

That weakens the DB-first architecture. The runtime should treat SQLite as the only truth source for both process state and final artifact content. Any content that requires LLM judgment should be written as structured rows first, and the final public files should then be rendered deterministically by scripts.

## What Changes

- Switch digest persistence from near-final `sections[]` content to structured `digest_slots + section_summaries`.
- Stop accepting LLM-written `report_md` in citation semantics persistence.
- Derive `citation_analysis.json.report_md` and `citation_analysis.md` from structured citation DB content during rendering.
- Update templates, render schemas, gate guidance, and runtime docs so final artifacts are truly database-driven.
- Realign `references/step_01` through `references/step_06` so each stage document describes DB truth, stage-local inputs/outputs, and gate-constrained publication timing instead of near-final text generation.
- Keep the public output contract unchanged.

## Capabilities

### Modified Capabilities
- `literature-digest`
- `sqlite-gated-skill-runtime`

## Impact

- Runtime data model updates in:
  - `literature-digest/scripts/runtime_db.py`
  - `literature-digest/scripts/stage_runtime.py`
  - `literature-digest/scripts/gate_runtime.py`
- Render asset updates in:
  - `literature-digest/assets/templates/*`
  - `literature-digest/assets/render_schemas/*`
- Guidance updates in:
  - `literature-digest/SKILL.md`
  - `literature-digest/references/*.md`
  - `docs/dev_paper_digest_skill.md`
- Verification updates in:
  - `tests/test_runtime_db.py`
  - `tests/test_stage_runtime.py`
  - `tests/test_render_final_artifacts.py`
  - related guidance / validation tests
