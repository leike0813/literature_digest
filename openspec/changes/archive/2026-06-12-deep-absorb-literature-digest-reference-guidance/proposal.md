## Why

The current `literature-analysis/references/` files have the right stage split, but they still read like summaries. The old `literature-digest/references/` files carried much more operational value: source-of-truth boundaries, payload shapes, positive and negative examples, quality gates, failure codes, and recovery guidance.

This change deeply absorbs that reusable guidance into the new `literature-analysis` reference set while preserving the six-stage `literature-analysis` workflow and avoiding the old gate-loop main path.

## What Changes

- Deepen the five `literature-analysis/references/*.md` files into executable stage manuals.
- Preserve the current `literature-analysis/SKILL.md` shape, with only minimal index wording if needed.
- Absorb reusable rules from old source/planning, digest, reference extraction, citation, render, and failure recovery documents.
- Add guidance tests that check high-risk rule anchors without snapshotting long prose.

## Capabilities

### Modified Capabilities

- `literature-analysis`: gains full reference guidance for source planning, digest generation, reference extraction, citation analysis, and finalization/recovery.

## Impact

- **Guidance impact**: Agents can load one stage reference and get enough detail to execute that stage without consulting old `literature-digest` references.
- **Runtime impact**: No intended runtime or algorithm changes.
- **Compatibility impact**: Existing public output contracts remain unchanged; old `literature-digest` remains unchanged.
