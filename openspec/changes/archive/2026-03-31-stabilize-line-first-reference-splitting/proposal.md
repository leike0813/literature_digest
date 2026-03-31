# Proposal

## Summary

Stabilize stage 4 references splitting by making deterministic preprocessing line-first for all bibliography styles, and route only suspicious boundaries into a block-level split review step.

## Why

The current references preprocessing can still over-trust year-tail markers and produce unstable raw entries for author-year bibliographies. This is especially visible when multiple references share one physical line, or when a single reference is wrapped across lines after PDF-to-Markdown normalization.

The runtime already has a split review action, but its old whole-scope `entries[]` contract is too coarse and pushes too much work onto the model.

## Goals

- Make deterministic splitting line-first across numeric, author-year, and mixed bibliographies.
- Avoid silent multiline merges in deterministic preprocessing.
- Change split review to operate only on suspect blocks with `split` / `keep` / `merge`.
- Expose block-level diagnostics in workset exports and gate behavior.

## Non-Goals

- No change to the public `references.json` schema.
- No change to stage 4 final artifact names.
- No direct SQL-first write path for references refinement.
