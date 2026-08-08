## Context

The current reference path deterministically prepares local entries and parse candidates, then requires complete `reference_reviews[]` coverage before replacing `reference_items`. A separate local-evidence round enriches every persisted item. Runtime state is SQLite-backed and final artifacts are rendered from the DB.

The reference project obtains bibliography data for DOI-bearing papers from Crossref's CSL JSON transform. A probe against `10.1109/CVPR.2016.90` showed that Crossref exposes useful but sparse records, while Semantic Scholar exposes a more complete but differently sized and ordered bibliography. Provider data therefore cannot replace local preparation wholesale.

## Goals / Non-Goals

**Goals:**

- Resolve complete bibliography entries through exact public API lookups before split or core semantic review.
- Preserve local reference boundaries, ordering, raw evidence, and stable keys as the authority.
- Make network behavior bounded, cached, auditable, optional, and non-blocking.
- Reduce both core and metadata evidence packages to entries that still need agent work.

**Non-Goals:**

- Title-based source paper search, Google Scholar scraping, authenticated API support, or per-reference DOI hydration.
- Replacing local preprocessing, changing the public reference schema, or exposing API provenance publicly.
- Letting agent-facing metadata evidence review perform external lookup.

## Decisions

### Use a runtime-owned provider cascade inside reference prepare

`persist_references` without a payload remains the public entrypoint. Once local entries and parse candidates are deterministically prepared, it resolves the effective identifier before externalizing split work, runs Crossref first for DOI sources, and runs Semantic Scholar only while unresolved entries remain. arXiv sources skip Crossref.

This keeps the state machine at the agent's semantic decision boundary. A new public stage would make the agent mechanically drive a deterministic operation and complicate recovery.

### Store explicit input and semantic source identity separately

`identifier` is an optional runner parameter persisted in `runtime_inputs`. `source_identity` is a required nullable analysis-plan field persisted in a singleton table with source evidence. A valid explicit parameter wins; an invalid non-empty parameter emits a warning and falls through to the plan identity.

Analysis-plan evidence must contain the canonical identifier and sit outside `references_scope`, preventing a cited work's identifier from being mistaken for the source paper.

### Isolate providers, normalization, and matching in one deep module

`analysis_runtime/reference_api.py` owns identifier normalization, an injectable HTTP transport, provider adapters, response normalization, candidate merging, conservative matching, and audit serialization. `references.py` orchestrates this module; `runtime_db.py` remains the DB access boundary.

The internal candidate shape contains provider, provider record ID, identifiers, title, authors, year, canonical optional metadata, and response position. Only recognized existing public metadata fields are retained.

### Match provider records to local candidates, never by response position

Matching is one-to-one. Exact DOI or arXiv evidence wins. Otherwise titles use Unicode NFKC, case folding, punctuation normalization, and mutual-best token overlap. The default title threshold is 0.90. A Semantic Scholar candidate carrying a normalized arXiv identifier uses 0.95 so near-match arXiv records do not distort uniqueness competition. The margin remains 0.05 over the runner-up, and years must agree when both sides provide one. Short or non-segmentable titles require compact exact equality.

An accepted API item must have title, at least one author, a valid publication year, a selected local parse candidate, and no existing quality hard block. Local `entry_index`, `raw`, numbering metadata, and selected parse audit data are retained. Provider count and order are audit-only.

Crossref supplies preferred title, year, and publisher metadata. A longer non-empty author list wins, so Semantic Scholar can replace Crossref's common single-surname author field. Semantic Scholar fills missing identifiers, venue, date, and URL. Conflicting stable identifiers remain unresolved.

### Persist fetches separately from per-entry resolutions

`reference_api_fetches` caches one outcome per canonical identity and provider, including status, HTTP status, response JSON/hash, error JSON, and timestamp. `reference_api_resolutions` stores one decision per local entry. A `source_identity` singleton stores plan evidence.

Split changes clear resolutions but retain fetches for the same identity. A different effective identity invalidates both. A generated tmp audit sidecar summarizes decisions without becoming a public artifact.

### Filter split review by complete accepted block coverage

Each suspect block carries stable `entry_indexes`. Runtime reads accepted decisions from SQLite and suppresses the block only when every mapped entry is accepted. A partially accepted block remains intact: its original `source_text`, fragments, accepted keys, and unresolved keys are externalized together so boundary review sees the complete evidence.

When an agent submits the active partial blocks, runtime adds keep decisions for fully accepted blocks before invoking the deterministic split stage. Any submitted boundary change still invalidates all prior per-entry decisions; the retained provider cache is then rematched against regenerated entry indexes.

### Merge partial worksets transactionally

API-accepted items are pre-seeded with internal `resolution_source=reference_api`. Core packages and payload validation operate only on unresolved keys. The final core submit validates the combined API and agent set, then calls one full-table persistence operation inside the existing transaction.

Metadata evidence preparation filters out API-resolved items. When no unresolved items remain, reference and metadata receipts are completed or skipped internally and prepare returns the citation action directly.

### Bound public network behavior without new dependencies

The implementation uses Python's standard HTTP stack, a descriptive User-Agent, a 10-second timeout, at most two attempts per request, a 16 MiB response limit, and a `Retry-After` wait capped at five seconds. Semantic Scholar pagination follows `next` up to 2,000 records. Every terminal outcome is cached for the run, including failures, so repeated prepare calls are deterministic.

## Risks / Trade-offs

- [Provider schemas or availability change] → Validate shapes defensively, retain raw audit data, and route every unusable result to local review.
- [Conservative matching leaves resolvable entries for the agent] → Prefer false negatives over attaching the wrong citation; thresholds and reasons are tested and auditable.
- [Provider metadata conflicts] → Stable-ID conflicts remain unresolved; optional fields never overwrite stronger non-empty Crossref values without an explicit merge rule.
- [A transient failure is cached for the run] → The run remains deterministic and completes offline; a new run retries external services.
- [SQLite grows from raw provider responses] → Only two parent-bibliography endpoints are used, pagination is capped, and no N+1 child hydration is performed.

## Migration Plan

SQLite tables use `CREATE TABLE IF NOT EXISTS`, so new and resumed databases acquire the additional state without a separate migration command. Existing calls omit `identifier`, submit `source_identity: null`, and follow the same local review path. Rollback consists of removing the new provider invocation and tables; public artifacts require no migration.
