# Proposal: add-render-output-override-and-final-output-guardrail

## Why

The current stage-6 render path is fully DB-authoritative and always writes the final artifacts next to `source_path`. That default is good, but it leaves no supported way to redirect the final files when an outer instruction layer wants them under another directory such as `artifacts/`.

At the same time, the runtime already has a clean terminal step: `render_and_validate --mode render`. The gate should give the agent a short, explicit execution hint at every step, and the final step should clearly tell the agent to adopt the render script stdout JSON directly instead of manually reconstructing the final response.

## What Changes

- Add an optional `--out-dir` override to `scripts/stage_runtime.py render_and_validate --mode render`.
- Keep the default render behavior unchanged when `--out-dir` is absent.
- Add `execution_note` to the gate payload for all main-path actions.
- Use the stage-6 `execution_note` to tell the agent to directly use the render script stdout JSON as the final output.
- Document `--out-dir` only in the base execution docs and interfaces, not as a gate-level prompt rule.
- Update runner guidance so agents follow both `instruction_refs` and `execution_note`.

## Impact

- Public input, parameter, and output schemas stay unchanged.
- Public artifact filenames stay unchanged.
- Stage-6 render gains an internal CLI-only output-directory override.
- Gate payload grows by one new field: `execution_note`.
