## Why

The previous SQLite + gate refactor established a durable runtime truth, but the execution contract is still too diffuse:

- final artifacts are rendered directly in Python without explicit templates,
- `SKILL.md` still mixes core rules with long step-by-step instructions and examples,
- and the gate output tells the agent what to do next without showing where to read or what SQL shape to use.

That makes the runtime harder to audit, harder to keep aligned across prompts/docs/scripts, and harder to evolve safely.

## What Changes

- Add explicit templates and render-context schemas for all final artifacts.
- Refactor `SKILL.md` into a compact runtime contract and move detailed instructions into split `references/step_*.md` files plus shared reference docs.
- Extend the gate payload with:
  - `instruction_refs` pointing to the relevant step/reference docs
  - `sql_examples` containing minimal SQL examples for the current `next_action`

## Capabilities

### Modified Capabilities
- `literature-digest`
- `sqlite-gated-skill-runtime`

## Impact

- New render assets under `literature-digest/assets/templates/` and `literature-digest/assets/render_schemas/`
- New reference docs under `literature-digest/references/`
- Updated runtime modules:
  - `literature-digest/scripts/render_final_artifacts.py`
  - `literature-digest/scripts/gate_runtime.py`
  - `literature-digest/scripts/runtime_db.py`
- Updated skill guidance:
  - `literature-digest/SKILL.md`
  - `literature-digest/assets/runner.json`
  - `docs/dev_paper_digest_skill.md`
