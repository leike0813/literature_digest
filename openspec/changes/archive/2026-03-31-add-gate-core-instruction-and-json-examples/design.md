# Design

## Core Instruction Source

Introduce a new asset file `literature-digest/assets/core_instruction.md`. It is the single source of truth for the compact cross-stage rules that gate should replay on every step.

`SKILL.md` will include an equivalent “核心执行指令” section, but gate should load the asset directly instead of hardcoding a duplicate string.

## Gate Payload

Add `core_instruction: string` to the gate payload returned by `gate_runtime.py`.

Rules:

- It must be present for all main-path stages and repair paths.
- It must be identical across stages.
- It must not replace `instruction_refs`.
- It must not replace `execution_note`.

Responsibilities:

- `core_instruction`: fixed cross-stage rules.
- `execution_note`: current-step emphasis.
- `instruction_refs`: detailed appendix navigation.

## Final stdout JSON examples

The final stdout JSON contract should be shown as examples, not just field lists.

Required updates:

- `SKILL.md`: success example and failure example.
- `step_01_bootstrap_and_source.md`: failure example.
- `step_05_citation_pipeline.md`: `citation_analysis.json` object example.
- `step_06_render_and_validate.md`: success and failure stdout examples.
- `stage_runtime_interface.md`: render success output example upgraded to full schema shape and add failure example.

The emphasized line about final stdout JSON should appear in `core_instruction` using Markdown bold.
