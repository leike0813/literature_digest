# Design: Stage 4 Reference Quality Gate

## Runtime Model

`reference_quality_issues` records active and resolved quality issues:

- `issue_id`
- `entry_index`
- `ref_index`
- `severity`: `hard_block` or `warning`
- `reason_code`
- `field`
- `current_value`
- `raw_excerpt`
- `recommendation`
- `status`
- `created_at`
- `resolved_at`

The gate reads active rows as the source of truth for agent-facing instructions.

## Classifier Contract

The classifier mirrors the plugin-compatible contract without importing plugin code.

Input priority:

- `title`: `title || parsed_title || parsedTitle || paper_title`
- `raw`: `raw || raw_reference || reference`
- `authors`: `authors || author`
- `year`: explicit `year`, otherwise first `19xx/20xx` in raw

`normalizedTitle`:

- cast to string
- trim and collapse whitespace
- NFKC normalize
- lowercase English text
- replace punctuation/symbol runs with spaces
- collapse spaces again

`contentTokens` exclude stopwords, tokens shorter than 2 chars, and pure numbers.

Hard reason codes:

- `empty_title`
- `bare_identifier_or_url_title`
- `publication_metadata_only_title`
- `author_only_title`
- `no_usable_title_tokens`

Soft reason codes:

- `bibliographic_suffix_in_title`
- `possible_author_prefix_noise`
- `very_long_title`
- `short_title_requires_context`
- `missing_year`
- `missing_authors`

## Flow

`persist_references` validates structure and prepared candidate selection first. It then normalizes each row and classifies quality.

If any hard issue exists:

- Do not write `reference_items`.
- Replace active `reference_quality_issues`.
- Keep workflow at `stage_4_references / persist_references`.
- Gate returns `quality_directives` with affected rows, stable reason codes, evidence, and repair recommendations.

If only soft issues exist:

- Write `reference_items`.
- Add `metadata.title_quality = {"status": "warning", "flags": [...]}` for affected rows.
- Replace active `reference_quality_issues`.
- Advance workflow to `stage_4_references / review_reference_quality`.
- Gate instructs the agent to correct or explicitly accept each warning.

If no issues exist:

- Write `reference_items`.
- Resolve active quality issues.
- Continue to `stage_5_citation / prepare_citation_workset`.

## Review Action

`review_reference_quality` accepts:

- `resolution: "corrected"` with corrected reference fields.
- `resolution: "accept_warning"` for soft warnings only.

Hard rows are repaired by resubmitting `persist_references` with corrected rows or omitting unrecoverable rows from the new full payload. This preserves the existing Stage 4 DB-first model where `reference_items` are written only after the final accepted set is known.

