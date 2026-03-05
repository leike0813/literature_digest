# Design: Introduction-Scoped Citation Analysis (`citation_analysis.json`)

## Context

The skill is used in background automation. It must:
- never ask the user questions at runtime,
- always output exactly one JSON object on stdout,
- avoid stdout truncation by writing large artifacts to files under `md_path` directory.

## Design Goals

1. Add a new artifact to support literature review drafting.
2. Restrict analysis scope to Introduction (Chapter 1, including subsections).
3. Support both numeric and author-year citation styles; treat author-year as first-class.
4. Provide stable linking between in-text citations and `references.json` items when mapping is reliable.
5. Avoid hallucination: uncertain mappings go to `unmapped_mentions`.

## Decision: Add `citation_analysis_path` + `citation_analysis.json`

### Stdout contract

Top-level stdout JSON required keys include:
- `digest_path`, `references_path`, `citation_analysis_path`
- `provenance.generated_at`, `provenance.input_hash`
- `warnings`, `error`

Artifacts are written to `<dir_of_md_path>` with fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

### Artifact schema (minimum)

`citation_analysis.json` MUST be a JSON object with:
- `meta`:
  - `language` (`zh-CN` / `en-US`)
  - `scope`: `{ section_title, line_start, line_end }` (1-based md lines)
- `items`: array (grouped by reference)
- `unmapped_mentions`: array
- `report_md`: string (markdown)

### Scope interpretation

“Introduction only” means:
- from the `Introduction` heading line (e.g. `# 1 Introduction`) to the next heading of the same or higher level,
- including all subsections under Introduction.

### Citation parsing & mapping rules (LLM behavior)

1. Numeric citations:
   - patterns like `[5, 36]`, `[4,15,38]`, `[40–42]` (expand ranges),
   - map `ref_number -> ref_index` (usually `ref_index = ref_number - 1`),
   - if numbering is anomalous, use best-effort mapping and reduce confidence.
2. Author-year citations:
   - must parse `(Author, YEAR)`, `Author (YEAR)`, multi-cites separated by `;`, `&/and`, `et al.`,
   - mapping prefers `year` + first-author surname match against `references.json`,
   - if ambiguous or missing evidence: put into `unmapped_mentions` with a `reason`.

### Deterministic validation (validator behavior)

`scripts/validate_output.py` will:
- materialize `citation_analysis.json` when an inline `citation_analysis` object is provided,
- validate that `citation_analysis.json` contains required keys and correct types,
- enforce internal scope consistency: all mention line ranges must lie within `meta.scope.line_start..line_end` when scope is valid.

## Acceptance Criteria

1. All schema/documentation updates are consistent across:
   - `literature-digest/SKILL.md`
   - `docs/dev_paper_digest_skill.md`
   - `docs/dev_overview.md`
   - `literature-digest/assets/output.schema.json`
2. Validator supports new field and tests cover:
   - fix mode materialization,
   - check mode missing required keys,
   - check mode citation analysis schema validation,
   - scope consistency failure.

