# Proposal

## Summary

Add a fixed `core_instruction` field to gate payloads so every stage returns the same compact execution rules, while keeping stage-specific behavior in `execution_note`.

Also replace field-only descriptions of the final stdout JSON with concrete success and failure examples throughout the main skill guidance.

## Why

Agents can lose track of the main execution discipline when context grows. The current short `execution_note` helps for one step, but there is no stage-by-stage replay of the cross-stage rules. At the same time, several docs still describe final stdout JSON only as field lists, which is weaker than a concrete example.

## Goals

- Return a fixed Markdown `core_instruction` string from gate at every main-path stage.
- Keep `execution_note` for stage-specific prompts only.
- Make the final stdout JSON contract visually prominent in the core instruction.
- Ensure every doc that discusses final stdout JSON includes a concrete JSON example.

## Non-Goals

- No new workflow stages or actions.
- No changes to `output.schema.json`.
- No change to existing payload contracts for stage writes.
