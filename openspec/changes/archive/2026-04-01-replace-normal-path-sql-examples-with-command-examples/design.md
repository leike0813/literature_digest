# Design

## Overview

The gate payload already returns `next_action`, `instruction_refs`, `core_instruction`, and `execution_note`. This change adds `command_example` as the explicit normal-path execution hint and demotes `sql_examples` to repair-only guidance.

## Decisions

- `command_example` is returned for every non-repair `next_action`.
- `command_example` includes the exact stage runtime command plus a minimal payload example when that action requires `--payload-file`.
- `sql_examples` remains in the payload for compatibility, but normal-path values are always `[]`.
- Repair actions continue to return `sql_examples`, and `command_example` is `null` for those actions.
- Command examples use `--db-path "<DB_PATH>"` explicitly to reduce ambiguity about which runtime DB the next command should target.
- Bootstrap command examples use placeholders for `source_path`, `language`, and `output_dir` because gate cannot recover prompt inputs from the database before bootstrap runs.

## Affected Areas

- `literature-digest/scripts/gate_runtime.py`
  - Add `command_example` generation.
  - Suppress `sql_examples` for non-repair actions.
- `literature-digest/references/gate_runtime_interface.md`
  - Document `command_example` and the repair-only role of `sql_examples`.
- `literature-digest/SKILL.md`
  - Point normal-path execution to `command_example` and repair-only SQL to `sql_examples`.
- Tests
  - Verify normal-path vs repair payload behavior and updated guidance text.
