## Why

Reference extraction currently requires agent review for every prepared bibliography entry even when the source paper has a stable identifier and public bibliographic APIs expose most of its references. Adding a deterministic API-first resolution pass reduces semantic review work while preserving the locally prepared bibliography as the authority for entry boundaries, order, and raw evidence.

## What Changes

- Add an optional `identifier` parameter accepting DOI and arXiv identifiers, with an analysis-plan source identity as the fallback lookup input.
- After deterministic local entry/candidate preparation and before split-review packages are externalized, query Crossref and Semantic Scholar through a bounded, cached runtime-owned provider cascade.
- Suppress a suspect block only when every mapped local entry is API-accepted; retain the complete block for review when any mapped entry remains unresolved.
- Normalize and conservatively match complete API records to local reference entries, persist accepted records directly, and generate core and metadata review batches only for unresolved local entries.
- Record provider fetches and match decisions in SQLite and a temporary audit sidecar; treat unavailable, incomplete, or ambiguous API data as a warning-only fallback to the existing local review path.
- Keep final stdout, public artifact names, reference ordering, and public reference shape unchanged.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `literature-analysis`: Extend the input, analysis-plan, reference review, metadata evidence, and public rendering requirements for API-first reference resolution.
- `sqlite-gated-skill-runtime`: Add DB-backed source identity, provider fetch caching, per-entry resolution audit, receipt invalidation, and partial-workset state transitions.

## Impact

- Affects the `literature-analysis` runner parameter schema, runtime initialization, analysis-plan payload, accepted-aware split prepare/persist flow, SQLite schema, gate guidance, skill documentation, and behavioral tests.
- Uses unauthenticated public Crossref and Semantic Scholar endpoints with timeouts, bounded retry/pagination, per-run caching, and a complete offline path.
- Adds no dependency, no public artifact, no new agent-facing command, and no change to the final output schema.
