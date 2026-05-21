## Why

`literature-digest` currently returns text artifacts only, so downstream hosts cannot identify a representative figure for preview, card, or bundle workflows. The skill already reads normalized textual source, making digest generation the right stage to select a representative image from caption and nearby-text evidence without adding image extraction responsibilities.

## What Changes

- Add an optional `representative_image` object to the final stdout JSON and mirrored `literature-digest.result.json`.
- Extend the digest-stage payload so the agent can persist a representative-image decision alongside `digest_slots` and `section_summaries`.
- Support selected Markdown/HTML image references and PDF figure-caption metadata, while returning `{"status": "none"}` when no reliable figure evidence exists.
- Keep existing artifact filenames, CLI parameters, required output fields, and lite skill behavior unchanged.

## Capabilities

### New Capabilities

<!-- No standalone capability; this extends the existing main skill contract. -->

### Modified Capabilities

- `literature-digest`: Add optional representative image selection and output metadata to the main skill.

## Impact

- Affected code: `literature-digest/scripts/runtime_db.py`, `literature-digest/scripts/stage_runtime.py`, main-skill schemas, docs, and tests.
- Public API impact: additive optional `representative_image` field only.
- Dependency impact: none.
