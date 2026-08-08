## Why

The current digest guidance uses normal journal-paper item ranges as practical upper bounds. That produces reasonable digests for ordinary articles, but it compresses long, information-dense sources such as theses into the same fixed amount of content.

The OpenSpec capability layout also still reflects the earlier `literature-digest-lite` name, while the current `literature-digest` main spec describes the archived full-analysis implementation.

## What Changes

- Make digest depth adapt to source length and information density through agent judgment, without page/character thresholds or a new runtime gate.
- Replace narrow item caps with wider soft reference ranges that may be exceeded when the source contains enough distinct, grounded content.
- Expand section summaries with substantive chapters and subtopics while preventing padding, repetition, or invented detail.
- Consolidate duplicate count guidance so each active skill has one authoritative wording location.
- **BREAKING (OpenSpec organization only):** realign the `literature-digest` capability with the current digest-only skill and retire the stale `lite-skill` capability. Runtime inputs, outputs, and artifact names do not change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `literature-analysis`: Require digest depth to scale semantically with source length and information density while preserving the existing structured payload and runtime boundary.
- `literature-digest`: Replace the archived full-analysis requirements with the current digest-only contract and add adaptive digest-depth behavior.
- `lite-skill`: Retire the stale capability after its current digest-only requirements are represented by `literature-digest`.

## Impact

- Agent guidance changes in `literature-analysis/SKILL.md`, `literature-analysis/references/digest_generation.md`, and `literature-digest/SKILL.md`.
- OpenSpec deltas realign `literature-digest`, retire `lite-skill`, and add adaptive digest requirements to both active skills.
- No script, template, JSON schema, runner, dependency, public payload, stdout field, or artifact filename changes.
