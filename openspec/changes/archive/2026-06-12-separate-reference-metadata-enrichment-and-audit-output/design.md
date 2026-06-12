## Context

The current reference runtime stores audit metadata in `reference_items.metadata_json`, and `fetch_reference_items()` flattens that metadata into public render output. This made internal fields visible in `references.json`. The same path also accepts rich metadata during core reference review, before the metadata enrichment workset exists.

The public CLI should stay stable, but the reference stage needs a stricter stateful handshake: prepare references, submit core fields, prepare metadata enrichment packages, submit metadata, then continue to citation analysis.

## Goals / Non-Goals

**Goals:**

- Keep core reference review focused on parse hypothesis and locked bibliographic fields.
- Require metadata review to use metadata work packages and stable `reference_key` values.
- Keep internal parse audit available for debugging without exposing it in public artifacts.
- Avoid repeating static allowed/locked field lists on every metadata workset item.

**Non-Goals:**

- Do not add a new public CLI command.
- Do not change final artifact filenames.
- Do not remove internal parse candidate validation.
- Do not modify `literature-digest`.

## Decisions

- **Same command, two submit rounds.** `persist_references` remains the public command. Payload shape determines whether the submit is core review or metadata review.
- **Core payload forbids metadata.** This prevents agents from bypassing enrichment context.
- **Metadata workset uses reference keys.** Agent-facing metadata payloads use `reference_key`; internal deterministic handlers can still use `ref_index`.
- **Public render context filters audit fields.** Runtime DB may keep audit fields in metadata for quality checks, but render context only exposes public bibliographic metadata.
- **Audit sidecar is tmp-only.** Parse choice details are written to `.literature_analysis_tmp/reference_parse_audit.json`, not to stable public artifacts.

## Risks / Trade-offs

- **Risk: More reference-stage round trips.** Mitigation: the second round is still inside `persist_references` and can be delegated by batch.
- **Risk: Existing tests/payload examples using `reference_reviews[].metadata` break.** Mitigation: update tests and guidance to the new current-state contract.
- **Risk: Public references lose debug visibility.** Mitigation: audit sidecar retains selected parse pattern and candidate details.
