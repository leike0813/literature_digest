# Design: optimize-citation-workset-and-inline-minimal-skill-guide

## Decisions

### Citation workset becomes a first-class DB layer

References extraction and citation analysis stay as separate stages, but the bridge between them becomes explicit:

- `citation_mentions` stores raw extracted mentions
- `citation_mention_links` stores the resolved mention-to-reference mapping
- `citation_workset_items` stores the grouped per-reference workset used by semantic analysis
- `citation_items` stores only semantic judgments
- `citation_summary` stores the global natural-language synthesis

This removes `reference_json` / `mentions_json` from `citation_items` as SSOT fields.

### Main-path action set

The stage runtime action set becomes:

- `bootstrap_runtime_db`
- `normalize_source`
- `persist_outline_and_scopes`
- `persist_digest`
- `persist_references`
- `prepare_citation_workset`
- `persist_citation_semantics`
- `persist_citation_summary`
- `render_and_validate --mode render`

`export_citation_workset` remains a read-only auxiliary helper and reads the stored workset instead of rebuilding it.

### Minimal execution guidance lives in SKILL.md

`SKILL.md` becomes the minimal but complete main-path guide:

- action order
- exact script calls for each main-path action
- minimum allowed payloads and field meanings
- gate discipline
- on-demand reading rule for `references/`
- a project-wide parameter glossary reused by appendix docs

Each main-path action description in `SKILL.md` should explain when to run the command, how to invoke it, what payload fields mean, what a minimal valid example looks like, what gate result should follow, and what mistakes are common.

`references/step_*.md`, interface docs, SQL notes, and style heuristics remain as optional quality-improving appendices.

`stage_runtime_interface.md` becomes the authoritative script-facing appendix:

- command form
- supported input channels
- payload top-level shape
- per-field semantics
- minimal valid examples
- representative invalid examples
- success output shape
- common failure causes

### Rendering contracts are code-owned

The renderer is now fully script-owned and deterministic, so a separate `rendering_contracts.md` is no longer necessary.

- minimum artifact shape requirements move into `SKILL.md` and relevant step docs
- interface-level render-source notes stay in `stage_runtime_interface.md`

### Citation summary is required

`citation_analysis.json` adds a required top-level `summary: string`.

- the agent writes it through `persist_citation_summary`
- the renderer uses it in both `citation_analysis.json.report_md` and `citation_analysis.md`
- the markdown artifact remains exactly equal to `report_md`
