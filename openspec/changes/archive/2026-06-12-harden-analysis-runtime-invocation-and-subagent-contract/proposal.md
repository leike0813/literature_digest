## Why

Recent `literature-analysis` runs exposed avoidable agent friction: some invocation forms failed before the runtime could start, malformed hand-written JSON caused tracebacks, and subagent batch drafts used inconsistent metadata field names that the main agent had to normalize manually.

The skill needs to keep its current six-stage runtime while making invocation, submit-time validation, and subagent contracts more robust and portable.

## What Changes

- Make `run_analysis.py` bootstrap its own script path before importing `analysis_runtime`.
- Keep payload validation inside existing submit handlers; do not add a standalone validation stage.
- Return schema-compatible JSON for unreadable or invalid payload files.
- Strengthen reference/citation batch contracts and subagent prompts with canonical fields, forbidden fields, examples, and merge guidance.
- Normalize deterministic metadata aliases as a runtime fallback and report warnings.
- Update skill guidance so formal runtime instructions use portable bare `python` commands, not local `uv` or `$HOME/.ar` assumptions.

## Capabilities

### New Capabilities

- `literature-analysis`: Harden the current runtime invocation, payload handling, and subagent batch contract for the `literature-analysis` skill.

### Modified Capabilities

None.

## Impact

- **Public CLI**: unchanged command names and stage sequence.
- **Agent-facing payloads**: unchanged top-level current payload names; metadata aliases can be normalized with warnings.
- **Stdout/final artifacts**: unchanged successful artifact contract; payload read failures become stable JSON errors.
- **Skill docs/assets**: formal execution examples become portable bare `python`.
- **Old skill**: unchanged.
