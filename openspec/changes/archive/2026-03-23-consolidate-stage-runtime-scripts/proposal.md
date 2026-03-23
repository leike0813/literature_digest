## Why

The SQLite + gate runtime refactor established a stable execution model, but the Python entrypoints remained fragmented across too many small scripts.

That made the runtime harder to audit and evolve because:

- phase actions were spread across multiple CLI entrypoints,
- `gate_runtime.py` had to point into a diffuse script surface,
- and docs/tests had to track several runtime executables even though the state machine already grouped work by stage.

The implementation has already been consolidated in the codebase. This change records that consolidation so the runtime history remains traceable in OpenSpec.

## What Changes

- Introduce `literature-digest/scripts/stage_runtime.py` as the single stage-action entrypoint.
- Keep `literature-digest/scripts/gate_runtime.py` as the sole state-machine / next-action authority.
- Keep `literature-digest/scripts/runtime_db.py` as the sole DB access and render-context helper layer.
- Remove the old standalone runtime entry scripts rather than preserving CLI compatibility wrappers.
- Update runner/docs/tests so `next_action` maps directly to `stage_runtime.py <subcommand>`.

## Capabilities

### Modified Capabilities
- `literature-digest`
- `sqlite-gated-skill-runtime`

## Impact

- New unified runtime entrypoint:
  - `literature-digest/scripts/stage_runtime.py`
- Retained infrastructure:
  - `literature-digest/scripts/gate_runtime.py`
  - `literature-digest/scripts/runtime_db.py`
- Removed standalone runtime entrypoints:
  - `literature-digest/scripts/dispatch_source.py`
  - `literature-digest/scripts/citation_preprocess.py`
  - `literature-digest/scripts/init_runtime_db.py`
  - `literature-digest/scripts/provenance.py`
  - `literature-digest/scripts/render_final_artifacts.py`
  - `literature-digest/scripts/validate_output.py`
- Updated guidance and verification:
  - `literature-digest/SKILL.md`
  - `literature-digest/assets/runner.json`
  - `literature-digest/references/*.md`
  - `docs/dev_paper_digest_skill.md`
  - `tests/test_stage_runtime.py`
  - migrated runtime tests under `tests/`
