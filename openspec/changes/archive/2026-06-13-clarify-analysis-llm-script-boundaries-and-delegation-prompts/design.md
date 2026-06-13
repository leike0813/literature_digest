## Design Notes

- The boundary is behavioral, not technical: helper scripts may serialize already-decided payloads, count keys, or check JSON syntax, but must not infer authors, titles, metadata, topics, citation usage, or summaries.
- Subagent delegation remains conditional on environment support and batchability, but the named task points should be mandatory-first.
- Detailed references should repeat only stage-specific responsibility splits, not restate the whole `SKILL.md`.
- The runtime already returns `subagent_prompt_template` and batch prompts; documentation should tell the main agent exactly when to use them.

## Non-Goals

- No new runtime command.
- No new payload fields.
- No restriction on scripts for deterministic validation, serialization, or renderer-owned output.
- No change to final public artifacts.
