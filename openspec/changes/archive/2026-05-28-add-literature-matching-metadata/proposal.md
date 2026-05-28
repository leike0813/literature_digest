## Why

Downstream discovery needs lightweight, structured matching signals from successful `literature-digest` runs without reading full digest artifacts. Adding a small DB-rendered sidecar keeps discovery metadata consumable while preserving the existing digest, references, and citation artifacts as the reading source of truth.

## What Changes

- Add a required public sidecar artifact `literature_matching_metadata.json`.
- Extend Stage 02 so `persist_outline_and_scopes` persists `literature_matching_metadata` with outline and scope decisions.
- Add `literature_matching_metadata_path` to final stdout JSON and mirrored `literature-digest.result.json`.
- Render and validate the sidecar through the existing DB-first Stage 06 path.
- Keep `literature-digest-lite`, existing artifact meanings, dependencies, and `bm25_text` generation unchanged.

## Capabilities

### New Capabilities

<!-- No standalone capability; this extends existing skill/runtime contracts. -->

### Modified Capabilities

- `literature-digest`: Adds a public matching metadata sidecar and stdout path.
- `sqlite-gated-skill-runtime`: Adds DB-first persistence, rendering, and validation for the matching metadata artifact.

## Impact

- Affected code: `literature-digest/scripts/runtime_db.py`, `literature-digest/scripts/stage_runtime.py`, render schemas/templates, output schema, docs, and focused tests.
- Public API impact: additive required `literature_matching_metadata_path` in the main skill stdout and result mirror.
- Dependency impact: none.
