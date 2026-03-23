## Context

The runtime is already SQLite-first and gate-driven, but several main-path actions still accepted explicit inputs for data that should already have been decided earlier in the pipeline:

- `normalize_source` still accepted direct source/language overrides,
- `prepare_citation_mentions` still accepted late scope/source/language overrides,
- `render_and_validate --mode render` still exposed utility-style explicit inputs.

That weakened the gate contract: DB rows were supposed to be the single source of truth, but later stages could still bypass them.

## Decisions

1. Main-path actions become DB-authoritative
- `bootstrap_runtime_db` remains the only action that seeds `runtime_inputs.source_path`, `runtime_inputs.language`, `runtime_inputs.generated_at`, and `runtime_inputs.input_hash`.
- Later main-path actions read those values from DB only.

2. Citation scope is persisted once, then read-only
- `persist_outline_and_scopes` writes the authoritative `citation_scope`.
- `prepare_citation_mentions` reads `section_scopes.citation_scope` only.
- Fallback is allowed only when the stored scope is now out of range for the persisted normalized source.

3. Auxiliary tools are separated from the gate path
- `export_citation_workset` is read-only and not a gate `next_action`.
- `render_and_validate --mode fix|check` remains utility-only and separate from the formal publish path.

4. Audit metadata and warnings become first-class
- `citation_scope` metadata carries source/selection/fallback details.
- references numbering anomalies are stored in metadata and warnings.
- citation function labels are normalized to a fixed vocabulary with warning-based fallback.

## Runtime Implications

### DB-authoritative inputs

- `normalize_source`
  - reads `runtime_inputs.source_path`, `runtime_inputs.language`
- `prepare_citation_mentions`
  - reads `source_documents.normalized_source`, `section_scopes.citation_scope`, `runtime_inputs.language`
- `render_and_validate --mode render`
  - reads output root and provenance from DB only

### Scope auditability

`section_scopes.citation_scope.metadata_json` must carry:

- `scope_source`
- `selection_reason`
- `covered_sections`
- `fallback_from`
- `fallback_reason`

The final citation artifact meta mirrors those fields.

### Warning and quality propagation

- source normalization stores quality markers
- references persistence detects numbering anomalies
- citation semantics normalizes `function`
- final render aggregates non-blocking semantic warnings

## Documentation

The runtime docs must explicitly distinguish:

- gate-driven main-path actions,
- auxiliary helper tools,
- the rule that once a decision is in DB, later stages cannot re-specify it.
