## Why

The current `literature-digest` skill already has non-trivial staged behavior, but its execution truth is still split across prompt instructions, helper scripts, and transient files. This makes recovery, auditing, and hard gating difficult as the workflow grows more complex.

We need a single runtime authority for:
- process state,
- intermediate semantic results,
- final artifact payloads,
- and next-step instructions.

SQLite is a good fit for that role. A gate-driven state machine can then constrain the agent to one legal next action at a time.

## What Changes

- Introduce a SQLite runtime database under `<cwd>/.literature_digest_tmp/literature_digest.db` as the single source of truth.
- Add a gate runtime script that reads DB state, enforces stage/substep constraints, and emits the only legal next action.
- Stop persisting hidden intermediate JSON/MD artifacts as process truth.
- Render final outputs from the DB:
  - `digest.md`
  - `references.json`
  - `citation_analysis.json`
  - `citation_analysis.md`
- Extend the public output contract with optional `citation_analysis_report_path`.

## Capabilities

### Modified Capabilities
- `literature-digest`
- `citation-preprocess-pipeline`

### New Capabilities
- `sqlite-gated-skill-runtime`

## Impact

- New runtime modules:
  - `literature-digest/scripts/runtime_db.py`
  - `literature-digest/scripts/init_runtime_db.py`
  - `literature-digest/scripts/gate_runtime.py`
  - `literature-digest/scripts/render_final_artifacts.py`
- Updated public contract:
  - `literature-digest/assets/output.schema.json`
- Updated guidance:
  - `literature-digest/SKILL.md`
  - `docs/dev_paper_digest_skill.md`
  - `literature-digest/assets/runner.json`
