# Design: add-render-output-override-and-final-output-guardrail

## Overview

This change adds one internal runtime capability and one gate-side guidance field:

1. `render_and_validate --mode render` may optionally accept `--out-dir`.
2. `gate_runtime.py` returns a short `execution_note` for each main-path action.

The default contract remains DB-authoritative:

- render still reads all business content from SQLite
- render still uses fixed filenames
- render still rejects late overrides for `source_path`, stdin payload, and preprocess artifacts

The only new override is the final output directory.

## Render output override

`render_and_validate --mode render` currently derives:

- `output_root = Path(runtime_inputs.source_path).parent`

After this change, the decision becomes:

- if `--out-dir` is provided, `output_root = Path(--out-dir).expanduser()`
- otherwise, `output_root = Path(runtime_inputs.source_path).parent`

The filenames remain fixed:

- `digest.md`
- `references.json`
- `citation_analysis.json`
- `citation_analysis.md`

`artifact_registry` and the final stdout payload must reflect the actual written paths.

Render-mode validation remains strict:

- reject `--source-path`
- reject `--preprocess-artifact`
- reject `--in`
- accept `--out-dir`

## Gate execution notes

The gate payload gains:

- `execution_note: string`

This field is a short action-specific instruction that complements:

- `instruction_refs`
- `sql_examples`

It is not a replacement for either one.

The important special case is stage 6:

- when `next_action=render_and_validate`, the `execution_note` tells the agent to run render mode next
- and to directly use the render script stdout JSON as the final assistant output

That guidance is intentionally scoped to the stage-6 `execution_note` only, so it does not compete with possible outer instruction injection layers.

## Documentation boundaries

- `SKILL.md` explains the optional `--out-dir` on the stage-6 main path.
- `stage_runtime_interface.md` documents the exact render CLI contract.
- `step_06_render_and_validate.md` explains the practical stage-6 behavior.
- `gate_runtime_interface.md` defines `execution_note`.
- `runner.json` tells agents to obey both `instruction_refs` and `execution_note`, without restating the stage-6 final-output wording globally.

## Compatibility

- No public schema change.
- No filename change.
- Existing callers that omit `--out-dir` keep current behavior.
- Existing gate consumers that ignore unknown fields remain compatible; new consumers can use `execution_note`.
