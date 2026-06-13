## Design Notes

- "Must use subagents" means default delegation when all three conditions are true: the environment supports subagents, the runtime returned `batch_work_packages`, and the batch is suitable for parallel review.
- The main agent remains the only writer. Subagents never run `scripts/run_analysis.py`, write SQLite, submit payloads, or generate public artifacts.
- Skipping delegation is allowed only for clear reasons such as no subagent capability, trivially small batches, or work that cannot be split without losing context. The reason should be retained in execution notes or review notes.
- JIT payloads should reinforce the same contract with `subagent_policy`, `merge_contract.single_writer = "main_agent"`, canonical return shapes, forbidden fields, and batch prompts.

## Non-Goals

- No payload schema change.
- No new runtime stage.
- No change to final artifact names or stdout schema.
- No requirement to simulate subagents in environments that do not provide them.
