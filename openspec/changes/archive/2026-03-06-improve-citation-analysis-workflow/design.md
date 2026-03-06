## Context

The current citation-analysis behavior relies heavily on unconstrained model behavior. In practice, this causes low mention recall and generic summaries. The skill already has deterministic helper scripts for validation/provenance, and this change extends that pattern to citation preprocessing while preserving the existing output contract.

Constraints:
- Keep public output schema stable.
- Do not modify `literature-digest/assets/runner.json`.
- Keep runtime non-interactive.
- Temporary artifacts should be written to `<cwd>/.literature_digest_tmp/` and retained by default.

## Goals / Non-Goals

**Goals:**
- Define an explicit multi-stage citation pipeline in `literature-digest/SKILL.md`.
- Improve recall by introducing deterministic mention extraction before semantic tasks.
- Add strict mention-accounting and fallback rules to prevent silent citation drops.
- Clarify semantic post-processing steps after preprocessing (mapping, grouping, function tagging, summary writing).

**Non-Goals:**
- Redesigning `citation_analysis.json` fields.
- Changing runner prompt text.
- Building a full citation parser framework beyond current skill needs.

## Decisions

1. Multi-stage pipeline as normative workflow
- Decision: Specify mandatory stage order in SKILL:
  1) preprocess extraction,
  2) mapping/accounting,
  3) semantic analysis,
  4) gate checks and fallback.
- Rationale: Separates deterministic extraction from model reasoning to increase recall and reproducibility.
- Alternative considered: single-stage LLM-only flow.
- Why not: too much variance and poor mention coverage.

2. Deterministic preprocess helper script
- Decision: Introduce `literature-digest/scripts/citation_preprocess.py` for mention extraction and normalization within agent-provided `citation_scope`.
- Rationale: Citation marker detection is mechanical and better done deterministically.
- Alternative considered: embed extraction rules only in prompt text.
- Why not: harder to audit and regression-test.

3. Scope decision ownership and shape
- Decision: Scope decision is owned by LLM/agent and emitted as a single `citation_scope` definition object.
- Rationale: Prevents scripts from making semantic scope decisions and avoids dual-scope ambiguity (`review_scopes + analysis_scope`).
- Alternative considered: deterministic script-side scope detection.
- Why not: chapter responsibilities vary by paper and require semantic judgment.

4. Temporary artifact policy
- Decision: Write preprocess artifacts to `<cwd>/.literature_digest_tmp/` and keep files by default.
- Rationale: Enables forensic debugging and avoids complexity from cleanup failures.
- Alternative considered: cleanup on success.
- Why not: adds failure modes and offers little value for this skill workflow.

5. Keep public contract unchanged
- Decision: Keep output schema and artifact protocol unchanged.
- Rationale: Avoids downstream compatibility churn while improving quality internally.
- Alternative considered: simplify citation-analysis schema.
- Why not: user preference is to keep schema mostly unchanged.

## Risks / Trade-offs

- [Risk] More stages may increase latency by ~1-2x.
- Mitigation: Keep deterministic preprocess lightweight and bounded to the provided `citation_scope` line range.

- [Risk] Agent may output overly narrow scope when review content spans multiple sections.
- Mitigation: Require cross-section coverage rules (e.g., `Introduction + Related Works`) and mandatory child-subsection inclusion for selected parent chapters.

- [Risk] More strict gates can increase `unmapped_mentions` volume.
- Mitigation: Document explicit reason codes and preserve high-recall behavior.

- [Risk] Temporary artifacts may accumulate over time.
- Mitigation: Use stable filenames in one directory to overwrite prior runs rather than append-only naming.

- [Risk] Over-constrained semantic steps could reduce narrative quality.
- Mitigation: Keep `report_md` generation flexible while requiring evidence-grounded mention accounting.
