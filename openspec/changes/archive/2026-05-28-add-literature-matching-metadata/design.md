## Design

Stage 02 becomes the single authoring point for literature matching metadata. The agent submits a structured `literature_matching_metadata` object alongside `outline_nodes`, `references_scope`, and `citation_scope`; the runtime validates it and persists it in a dedicated one-row SQLite table. Stage 06 renders the table into `literature_matching_metadata.json`, registers the path in `artifact_registry`, and includes it in the final stdout/result mirror.

## Data Shape

The persisted and rendered object is:

```json
{
  "schema": "literature_matching_metadata.v1",
  "key_terms": [],
  "methods": [],
  "problems": [],
  "datasets": [],
  "exclude_terms": []
}
```

All fields are required. Arrays may be empty, but must contain only strings. The runtime trims strings and filters empty strings before persistence; it rejects type errors, missing fields, schema mismatch, and over-limit arrays. Limits are `key_terms <= 12`, `methods <= 8`, `problems <= 8`, `datasets <= 8`, and `exclude_terms <= 6`.

## Rendering And Compatibility

`literature_matching_metadata.json` is a public artifact with a fixed filename under `runtime_inputs.output_dir`. `build_public_output_payload()` always includes `literature_matching_metadata_path`, using an empty string before render or on schema-compatible failure. Existing digest, references, citation analysis, report, and representative image behavior is unchanged.

Old databases can initialize because the table is created with `CREATE TABLE IF NOT EXISTS`. New successful runs require the Stage 02 payload to include matching metadata, matching the updated public contract.

## Tests

Use focused runtime tests rather than an end-to-end LLM fixture. The tests cover Stage 02 persistence and rejection cases, render output and result mirror path, public output validation, schema acceptance, and guidance documentation.
