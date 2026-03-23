## Context

We now have the right architecture split:

- a concise runtime contract,
- step-oriented external guidance,
- template and schema assets,
- and gate-provided navigation.

The problem is content loss. The older long-form `SKILL.md` contained detailed examples, failure-mode guidance, staged semantics, and template skeletons that were valuable operationally. The refactor should have relocated those details, not deleted them.

## Goals / Non-Goals

**Goals**
- Preserve all meaningful guidance from the long-form `SKILL.md`.
- Keep `SKILL.md` concise and navigational.
- Make each external guidance file rich enough to stand alone for its stage/topic.
- Preserve template intent without changing current public artifact semantics.

**Non-Goals**
- Reverting to a monolithic `SKILL.md`.
- Changing public output filenames or the DB-first runtime model.
- Reintroducing hidden files as process truth.

## Decisions

1. `HEAD` long-form `SKILL.md` is the source inventory
- Decision: use the current Git `HEAD` long-form file as the authoritative content source for migration.
- Rationale: gives a concrete, reviewable baseline and prevents ad hoc rewriting.

2. Slim `SKILL.md`, rich external guidance
- Decision: keep only contract + index in `SKILL.md`, move full detail into external docs.
- Rationale: preserves readability without losing instruction density.

3. No summary-only replacements
- Decision: migrated docs must carry original detail, examples, and constraints; thin summaries are insufficient.
- Rationale: the refactor must be lossless in guidance value.

4. Templates preserve intent through comments and contracts
- Decision: keep renderer-compatible template bodies, but add rich guidance in template comments and rendering contracts.
- Rationale: preserves final artifact semantics while keeping original template structure visible.

5. Gate references point to rich docs
- Decision: `instruction_refs` continue to point to step/contract docs, but those docs must now contain the full migrated detail.
- Rationale: the gate remains the navigation layer, not the content layer.
