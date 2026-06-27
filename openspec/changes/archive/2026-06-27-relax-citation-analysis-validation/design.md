## Context

`literature-analysis` currently prepares citation work packages, expects complete semantic review coverage, persists citation semantics/timeline/summary, then renders public artifacts. The strict validation is useful for clean papers but becomes counterproductive for irregular source text: missing reviews, empty semantic fields, empty timeline summaries, or missing citation worksets can block final rendering even after digest and references were produced.

The user preference for this change is explicit: do not add new business fields, do not synthesize pseudo-semantic fallback content, and do not create citation items for missing reviews. The runtime should persist what it can, tolerate empty fields, and still render the citation artifact.

## Goals / Non-Goals

**Goals:**

- Allow citation analysis persistence with empty or partial `citation_semantic_reviews`.
- Preserve submitted semantic content without inventing substitute citation meaning.
- Merge duplicate review entries deterministically when they use the same known `citation_work_key`.
- Allow empty global summary and empty timeline bucket summaries through render validation.
- Keep unsafe structural errors as hard failures.

**Non-Goals:**

- No new agent-facing payload fields.
- No changes to public artifact filenames.
- No runtime-generated low-confidence citation items for keys the agent did not review.
- No weakening of unknown key or forbidden internal field protection.

## Decisions

- Split citation submit validation into hard validation and tolerant normalization. Hard validation rejects only unsafe structure: unknown `citation_work_key`, forbidden fields, malformed review containers, and invalid top-level shapes. Tolerant normalization converts missing semantic fields to `""` or `[]`, accepts partial coverage, and merges duplicate known keys.
- Persist only reviewed keys. If a workset key is missing from payload, runtime does not create a placeholder citation item. This keeps output honest and prevents noisy invented content.
- Keep timeline derivation runtime-owned. Existing year-based bucket membership remains, but bucket summaries can be empty strings.
- Store empty citation summary rows. Render prerequisites should require the row to exist, not the text to be non-empty.
- Let no-workset citation preparation proceed when the source and citation scope are valid. The runtime records a warning and stores empty workset state so the final stage can still produce an artifact.

## Risks / Trade-offs

- Empty citation reports are less informative → The report still reflects mapped/unmapped data that exists, and empty content is preferable to fabricated semantics.
- Partial coverage may hide missing review effort → Warnings record partial or duplicate normalization without blocking output.
- Existing tests encode strict behavior → Tests must be updated to distinguish unsafe structure from acceptable incomplete content.
