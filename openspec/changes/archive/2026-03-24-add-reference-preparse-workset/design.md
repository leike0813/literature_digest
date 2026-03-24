# Design: add-reference-preparse-workset

## Overview

Stage 4 becomes a workset-first flow similar in spirit to the citation pipeline:

1. `prepare_references_workset`
   - reads `source_documents.normalized_source`
   - reads `section_scopes.references_scope`
   - splits raw references
   - detects numbering anomalies
   - generates multiple deterministic pattern candidates
   - stores `reference_entries`, `reference_batches`, and `reference_parse_candidates`
   - exports a full workset plus a lightweight review sidecar
2. `persist_references`
   - accepts only refined `items[]`
   - validates `entry_index` and `selected_pattern`
   - derives `ref_index` from `entry_index`
   - rejects suspicious title boundaries
   - writes final `reference_items`

## Data Model

### New table

- `reference_parse_candidates`
  - `entry_index`
  - `candidate_index`
  - `pattern`
  - `author_text`
  - `author_candidates_json`
  - `title_candidate`
  - `container_candidate`
  - `year_candidate`
  - `confidence`
  - `metadata_json`
  - `updated_at`

### Existing tables kept

- `reference_entries`
- `reference_batches`
- `reference_items`

## Pattern strategy

Each raw entry must attempt at least:

- `authors_period_title_period_venue_year`
- `authors_colon_title_in_year`
- `authors_year_paren_title_venue`
- `thesis_or_book_tail_year`
- `fallback_raw_split`

If multiple patterns match, all candidates are stored.

## Validation

`persist_references` must fail when:

- `selected_pattern` is missing
- `selected_pattern` does not exist in prepared candidates
- `title` begins with `, . ; :`
- `entry_index` cannot be mapped to a prepared reference entry

Warnings added or preserved:

- `reference_parse_low_confidence`
- `reference_pattern_ambiguous`
- `reference_title_boundary_suspect`

## Compatibility

This change is intentionally not backward compatible for the stage-4 payload contract:

- reject old `entries + batches + items` payload
- require `prepare_references_workset` before `persist_references`
