## Context

The existing command surface is stable, but `persist_references` and `persist_citation_analysis` still ask the main agent to submit runtime-oriented fields. This creates avoidable failures:

- `selected_pattern` values are hard to discover.
- `ref_index` is confused with source numeric references.
- timeline closure is manual and iterative.
- large citation payloads are hard to maintain.
- subagent delegation is suggested but not operationalized as structured work packages.

## Goals / Non-Goals

**Goals:**

- Hard-cut to a current-state agent-facing payload contract.
- Keep internal deterministic code free to use `ref_index`, parse patterns, and function enums.
- Generate review packages, merge contracts, and subagent prompts during prepare.
- Aggregate validation failures so the agent can repair in one pass.
- Keep public CLI and final artifacts unchanged.

**Non-Goals:**

- Do not redesign final render schemas.
- Do not change SQLite schema unless required.
- Do not preserve old agent-facing payload compatibility.
- Do not modify old `literature-digest`.

## Decisions

### Decision 1: Pattern is explicit but enumerated

`selected_parse_pattern` remains a required agent decision because it represents the parse hypothesis. Prepare responses must list allowed values by `reference_key`.

### Decision 2: Agent identifiers are stable work keys

Reference submissions use `reference_key`; citation submissions use `citation_work_key`. Internal `ref_index` can appear in review output only as audit context, not as the primary key the agent must submit.

### Decision 3: Timeline closure is runtime-owned

The agent writes narrative `timeline_summaries`. Runtime derives bucket membership from item years and validates the result.

### Decision 4: Subagents draft batches only

Subagents receive batch packages and return draft arrays. The main agent merges and submits one payload.

## Risks

- Tests using the old payload need updating.
- Some existing deterministic error messages still mention internal fields. The agent-facing wrappers should intercept common submit errors and return current-state diagnostics.
