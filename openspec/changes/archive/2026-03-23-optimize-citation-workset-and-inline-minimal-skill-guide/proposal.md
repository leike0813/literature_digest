# Proposal: optimize-citation-workset-and-inline-minimal-skill-guide

## Summary

The SQLite-gated runtime already removed most near-final text generation from the agent path, but two gaps remain:

- citation analysis still makes the agent reconstruct mention-to-reference joins instead of consuming a reusable database workset
- `SKILL.md` is still a contract-plus-index, not a minimal standalone execution guide

This change deepens the runtime so that:

- references extraction and citation analysis share a first-class citation workset in SQLite
- the agent only fills citation semantics and a global citation summary over prelinked workset rows
- `SKILL.md` becomes the minimal complete execution guide, while `references/` docs become on-demand appendices
- `citation_analysis.json` gains a required top-level `summary`

## Why

- Rebuilding mention-reference associations during citation semantics wastes effort and increases inconsistency risk.
- Agents should not need to preload the entire `references/` directory to execute the skill.
- The final citation artifact currently lacks a single natural-language synthesis over all analyzed citation items.

## Scope

- Refactor the citation runtime schema and stage flow around a reusable workset
- Inline the minimal main-path playbook into `SKILL.md`
- Remove `references/runtime_playbook.md` and `references/rendering_contracts.md` from the skill package
- Add the required `citation_analysis.summary` field and render it into `citation_analysis.md`
