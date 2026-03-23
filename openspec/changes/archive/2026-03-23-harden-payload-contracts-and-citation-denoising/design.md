## Context

The skill is already SQLite-first and gate-driven, but real runs still exposed three concrete gaps: documentation drift from the runtime payload contract, mention extraction noise from markdown artifacts, and missing recovery guidance when the gate blocks or a payload is malformed. The current code already has pieces of this behavior, such as numbering anomaly detection and scope override rejection, so this change extends and standardizes those behaviors instead of replacing the runtime architecture.

## Goals / Non-Goals

**Goals:**
- Make runtime payload docs field-for-field consistent with the accepted script inputs.
- Enforce the outline/scope payload contract in code instead of leaving it as a documentation convention.
- Filter common false-positive citation markers before workset persistence.
- Expose a lightweight workset review artifact for later semantic stages.
- Standardize warning categories and add a dedicated failure recovery appendix.
- Add a small regression corpus that proves the gate can still reach render across representative source variants.

**Non-Goals:**
- Changing public artifact filenames or required stdout fields.
- Reworking the broader DB schema or state machine.
- Reintroducing deprecated staged-file contracts or pre-DB intermediate files.
- Large-scale prose slimming beyond what is needed to remove ambiguity.

## Decisions

1. Payload contract is code-owned and docs must match exactly
- `persist_outline_and_scopes` now validates a single required shape for `outline_nodes`, `references_scope`, and `citation_scope`.
- `persist_references` keeps the existing top-level arrays but tightens the minimum required fields for `entries`, `batches`, and `items`.
- `persist_citation_semantics` remains workset-item keyed and explicitly rejects legacy mention/reference/report fields.
- Rationale: the code already acts as the true contract; making docs narrower than code is acceptable, but having docs broader than code creates avoidable failure loops.

2. Citation denoising happens before mention persistence
- `prepare_citation_workset` strips markdown image links, URLs, resource paths, image/PDF suffix matches, and date-like strings before deciding whether a candidate mention is valid.
- Filtered candidates increment a dedicated count and emit `citation_false_positive_filtered`.
- Rationale: these false positives are deterministic noise, so the runtime should handle them once instead of pushing cleanup back onto later semantic stages.

3. References parsing prefers conservative correctness
- Low-confidence or weakly structured reference items add `reference_parse_low_confidence`.
- Author parsing may remain conservative as a single-element `author` array.
- Trailing publication year takes precedence over misleading numeric prefixes such as arXiv identifiers.
- Rationale: downstream citation workset quality is better served by stable raw/title/year anchoring than by over-aggressive author splitting.

4. Workset export includes a lightweight review view
- The full workset export remains the richest sidecar.
- A second lightweight view containing only `ref_index`, `title`, `mention_count`, and `snippets` is emitted beside it.
- Rationale: later semantic analysis frequently needs a compact review surface, not the full link-level structure.

5. Failure recovery becomes a first-class appendix
- Recovery guidance lives in a dedicated appendix and is referenced by repair-oriented gate flows.
- Rationale: repair guidance is operational, not stage-specific, and should not be buried inside step docs.

## Risks / Trade-offs

- [Stricter payload validation] → Some payloads that used to fail late will now fail immediately. This is intentional; docs and tests are updated in the same change to reduce surprise.
- [Reference year normalization] → A heuristic could over-normalize a malformed raw string. Mitigation: only prefer trailing publication years and preserve low-confidence warnings.
- [False-positive filtering] → Over-filtering could suppress rare legitimate mentions embedded in unusual syntax. Mitigation: keep the filter list narrow and regression-test numeric, author-year, noise-heavy, and appendix-containing inputs.
- [More sidecar output] → Extra review exports add a little I/O. Mitigation: keep them internal and small; no change to public contract.
