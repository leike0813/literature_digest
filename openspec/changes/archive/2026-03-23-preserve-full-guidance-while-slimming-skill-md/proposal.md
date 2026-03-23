## Why

The recent SKILL refactor correctly separated runtime contract from execution detail, but it over-compressed the detailed guidance. As a result, a large amount of previously explicit instruction, examples, and templates from the long-form `SKILL.md` no longer exists anywhere in the refactored repository in usable form.

That is not an acceptable refactor boundary. We want a slim `SKILL.md`, not a lossy one.

## What Changes

- Keep `SKILL.md` slim, but preserve the removed detailed guidance by relocating it into the refactored repo structure.
- Treat the current Git `HEAD` long-form `literature-digest/SKILL.md` as the source inventory for migration.
- Expand `references/step_*.md`, `references/rendering_contracts.md`, and related docs so they carry the original detailed instructions rather than summaries.
- Expand templates and guidance docs so the original examples and template intent remain discoverable.

## Capabilities

### Modified Capabilities
- `literature-digest`
- `sqlite-gated-skill-runtime`

## Impact

- `literature-digest/SKILL.md` remains concise but gains a durable detailed-content index
- `literature-digest/references/` becomes the primary home of migrated detailed guidance
- `literature-digest/assets/templates/` preserves original template intent without changing final output semantics
- gate and runner guidance point at full-content docs instead of thin summaries
