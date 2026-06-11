# Design: Reference Metadata Enrichment Stage

## Runtime Flow

Stage 4 normal mode becomes:

`prepare_references_workset -> persist_references -> review_reference_quality? -> prepare_reference_metadata_enrichment -> persist_reference_metadata_enrichment -> prepare_citation_workset`

`decide_reference_extraction decision=abandon` remains reference-free and skips enrichment.

## Data Model

Add `reference_metadata_enrichment_workset` keyed by `ref_index`. Each row stores a locked reference snapshot, existing rich metadata, metadata-only context text, allowed field names, batch index, status, and evidence note. The workset is the DB proof used by `persist_reference_metadata_enrichment`; payload claims alone are not trusted.

## Payload Contract

`persist_reference_metadata_enrichment` receives `items[]`, one object per workset row. `status` is one of `enriched`, `confirmed_existing`, or `no_metadata_found`. `enriched` requires at least one non-empty allowed metadata field. Core fields such as author, title, year, raw, and confidence are locked and rejected if submitted.

## Gate Behavior

Gate routes to the enrichment prepare step after reference rows and quality issues are resolved. In normal mode, Stage 5 and render prerequisites require `action_receipts.persist_reference_metadata_enrichment`. Reference-free abandoned mode skips that prerequisite.

## Subagent Policy

The exported enrichment workset can be split by `batch_index` for subagent drafting. Subagents do not write SQLite or advance gate. The main agent merges fragments, removes unsupported fields, checks evidence, and submits a single persist payload.
