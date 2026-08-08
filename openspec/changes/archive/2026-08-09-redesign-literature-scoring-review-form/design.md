## Context

`literature-analysis` is a Tier-6 SQLite state-machine and Tier-7 automation-facing Skill. The scoring stage currently prepares a context file containing the normalized source and rubric, then expects the agent to construct a nested payload with canonical keys, enums, maximum scores, status values, and evidence line ranges. The runtime validates and normalizes that payload before storing the public score state. See `proposal.md` for the motivation and `specs/literature-scoring/spec.md` for the observable contract.

The existing rubric snapshot is persisted per run, the score document is stored atomically in SQLite, and both full and score-only rendering consume that normalized document. Those boundaries remain intact.

## Goals / Non-Goals

**Goals:**

- Reduce the agent's scoring input to semantic judgments while keeping deterministic ownership in the runtime.
- Make review drafts recoverable without overwriting partial agent work.
- Detect stale or structurally altered drafts before score normalization.
- Locate submitted evidence quotations robustly in normalized Markdown and derive line ranges deterministically.
- Keep all score calculation and public rendering behavior unchanged.

**Non-Goals:**

- Reducing the canonical criterion set or changing its scoring semantics.
- Supporting manually assembled score payloads alongside the generated form.
- Adding database state for drafts or changing the public score schema.
- Judging whether a quotation semantically supports a score.
- Adding external text-matching libraries or network services.

## Decisions

### 1. Generate paired original and draft forms keyed by source and rubric hashes

Prepare loads the current rubric snapshot and normalized source, hashes their canonical contents, and derives `form_id` from both hashes. It writes an immutable original form plus an editable draft beneath the existing scoring agent-work directory using hash-specific file names. The original is the locked-field authority during submit.

An existing original must equal the newly generated form. An existing draft is always preserved for the same `form_id`, so repeated prepare calls are safe after context loss. Hash-specific paths allow a new source or rubric snapshot to coexist with an old draft and make stale-form rejection explicit.

Storing form data in SQLite was considered, but draft content is agent-owned temporary work and is not workflow truth until validated. Existing agent-work files already serve this boundary without a schema migration.

### 2. Treat the rubric asset as executable review-form configuration

`scoring_rubric.json` gains paper-type choice objects plus prompts for dimensions and criteria. The form generator copies keys, names, descriptions/prompts, ordering, weights, and maximum scores directly from the rubric. Runtime validation derives all expected locked values from the original generated form and current hashes.

Keeping a second Python constant set or documentation table was rejected because it recreates the drift this change is intended to remove. Guidance explains how to fill generated fields without enumerating canonical definitions.

### 3. Validate locked structure before semantic answers

Submit accepts the draft object directly. Validation first checks `form_id`, current source/rubric identity, top-level field coverage, list lengths/order, and every locked value against the original. It then validates exactly one selected paper type and all editable answers.

Errors share top-level code `score_review_invalid` and carry structured detail records with stable reason codes: `stale_form`, `locked_field_changed`, `incomplete_answer`, and `invalid_selection`. This preserves one machine-facing failure category while making recovery specific.

Criterion `applicable` is converted internally to `scored` or `not_applicable`; no status appears in the draft. Applicable criteria require an integer score within the prefilled maximum plus a non-empty reason. Inapplicable criteria require a null score and a non-empty reason. Every dimension requires a non-empty summary; confidence is required for active dimensions and must be null for wholly inapplicable dimensions.

### 4. Locate quotations with normalized exact matching before bounded fuzzy matching

The matcher builds one-to-five-line source windows, normalizes source and quote text using NFKC, case folding, collapsed whitespace, and Unicode punctuation removal, and tries containment first. Exact ties resolve to the earliest line range.

For unmatched quotations with at least eight normalized characters, it computes Dice similarity over character n-gram multisets: bigrams for lengths 8–11 and trigrams for longer text. The best similarity at or above 0.45 is accepted; equal candidates resolve to the earliest range. Failure details include the best score and candidate lines so the agent can repair the quote.

The runtime only establishes location. It does not infer semantic relevance, preserving the LLM/script responsibility boundary.

### 5. Keep normalized score and renderer contracts unchanged

After form validation, the runtime converts answers into the existing internal review shape and reuses the existing N/A normalization, Decimal arithmetic, SQLite persistence, receipts, and render functions. This limits the breaking change to the agent-facing stage payload while preserving public `literature_score.v1`, full workflow routing, and score-only completion.

## Risks / Trade-offs

- **[Risk] Short or heavily transformed PDF quotations may not meet the fuzzy threshold.** → Require at least eight normalized characters, expose the best candidate range and similarity, and let the agent choose a clearer source quotation.
- **[Risk] A 0.45 n-gram threshold can accept a nearby but imperfect passage.** → Bound windows to five lines, prefer normalized exact matches, choose deterministically, and keep semantic support judgment with the agent.
- **[Risk] Partial drafts can linger after source or rubric changes.** → Hash paths by form identity and reject stale identities without deleting files.
- **[Risk] Rubric prompts become a larger configuration surface.** → Validate the complete rubric structure during prepare and test that generated forms mirror the asset exactly.

## Migration Plan

1. Extend the rubric with paper-type choices and review prompts.
2. Replace scoring context generation with paired review-form generation and update submit validation/conversion.
3. Update gate/JIT and Skill guidance to expose form paths, editable fields, and direct draft submission.
4. Expand behavior tests for recovery, validation, evidence matching, formulas, and both workflow modes.
5. Validate the OpenSpec change and focused runtime suite.

Rollback reverts these files. Existing SQLite score state and public artifacts require no migration because their schemas do not change.
