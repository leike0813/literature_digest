## Why

The current scoring stage makes the agent reconstruct rubric-owned keys, enums, score limits, statuses, and evidence line ranges in a large payload. That duplicates the rubric contract in prompts and creates avoidable validation failures, so the runtime should instead generate a locked, self-describing review form that the agent only fills with semantic judgments.

## What Changes

- Generate an immutable scoring review form and a reusable agent-editable draft from the normalized source and rubric snapshot.
- Replace the hand-authored scoring payload with direct submission of the generated draft; runtime-owned fields are prefilled and locked.
- Derive paper type from a single selected choice, criterion status from `applicable`, and evidence line ranges by matching submitted source quotations.
- Validate stale forms, locked-field changes, incomplete answers, invalid selections, and unlocatable evidence with structured reason codes.
- Make `scoring_rubric.json` the sole definition of paper-type choices, dimension/criterion labels, prompts, ordering, weights, and maximum scores.
- Keep SQLite score state, scoring formulas, N/A weighting, full/score-only routing, and the public `literature_score.v1` artifact unchanged.
- **BREAKING**: the internal agent-facing `persist_literature_score` payload is now the generated review-form draft; manually assembled legacy score payloads are not accepted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `literature-scoring`: Replace manual canonical coverage and evidence line-range submission with a runtime-generated, locked review form and deterministic evidence-location validation.

## Impact

- Affects the scoring runtime, rubric asset, gate/JIT action contract, scoring guidance, Skill/core runner instructions, and scoring behavior tests.
- Adds per-form temporary JSON files under the existing agent-work directory without adding database tables, dependencies, or public artifacts.
- Preserves the public output schema and all downstream score calculations.
