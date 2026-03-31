# Design

## Line-First Splitting

`prepare_references_workset` now treats each non-empty line in `references_scope` as a source block before any inline splitting happens.

Rules:

- First split by line.
- Then optionally split a single line into multiple proposed entries only when a second strong reference start is detected.
- If adjacent lines look like the continuation of one reference, mark the block as suspicious instead of merging deterministically.

This keeps deterministic preprocessing conservative and shifts ambiguous boundary repair into the review action.

## Suspect Blocks

The stage 4 workset exports now expose `suspect_blocks` instead of `suspect_entries`.

Each suspect block contains:

- `block_index`
- `source_text`
- `line_start`
- `line_end`
- `reasons`
- `proposed_entries`
- `suspicion_kind`

`suspicion_kind` distinguishes at least:

- `grouped_entries_in_single_line`
- `possible_multiline_entry`
- `mixed_or_ambiguous_boundary`

## Block-Level Split Review

`persist_reference_entry_splits` now accepts only suspect blocks:

```json
{
  "blocks": [
    {
      "block_index": 11,
      "resolution": "split",
      "entries": ["...", "..."]
    }
  ]
}
```

Rules:

- Only current suspect blocks may be reviewed.
- `resolution` is limited to `split`, `keep`, or `merge`.
- Reviewed entries must preserve the exact original block text after normalization.
- After review, the runtime regenerates `reference_entries`, `reference_parse_candidates`, and `reference_batches`.

## Gate Behavior

Stage 4 keeps a dual path:

- normal path: `prepare_references_workset -> persist_references`
- review path: `prepare_references_workset -> persist_reference_entry_splits -> persist_references`

When `requires_split_review=true`, gate must route to `persist_reference_entry_splits` and its execution note must emphasize block-boundary review only.
