# Tasks: add-render-output-override-and-final-output-guardrail

- [x] 1. Add optional `--out-dir` support to `render_and_validate --mode render` while keeping fixed filenames and current defaults
- [x] 2. Add `execution_note` to gate payloads and populate it for each main-path action
- [x] 3. Make the stage-6 `execution_note` instruct the agent to directly use render stdout JSON as the final output
- [x] 4. Update `SKILL.md`, `stage_runtime_interface.md`, `gate_runtime_interface.md`, and `step_06_render_and_validate.md`
- [x] 5. Update `runner.json` so agents follow both `instruction_refs` and `execution_note`
- [x] 6. Add regression coverage for render `--out-dir` and gate `execution_note`
