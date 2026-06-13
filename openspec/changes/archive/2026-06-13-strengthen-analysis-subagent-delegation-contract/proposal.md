## Why

`literature-analysis` already returns batch work packages for reference review, metadata enrichment, and citation semantic review, but the current guidance still presents subagent delegation as a local suggestion. In practice, these stages are the highest-volume, most error-prone manual payload construction points. The skill should make delegation a global execution contract whenever the environment supports subagents and the work is batchable.

## What Changes

- Add a global Subagent Delegation Contract to `literature-analysis/SKILL.md`.
- Require the main agent to default to batch subagent delegation for reference core review, metadata enrichment, and citation semantic review when subagents are available.
- Keep the main agent as the only DB/runtime writer and final payload submitter.
- Add short subagent prompt templates directly to the relevant `SKILL.md` stage cards.
- Strengthen runtime/JIT `subagent_policy`, `merge_contract`, and `field_guidance.subagents` wording.
- Keep public CLI, payload schema, SQLite SSOT, and final artifacts unchanged.

## Impact

- Agents can understand the subagent workflow from `SKILL.md` without first opening deep references.
- Runtime prepare/status payloads communicate the same mandatory-first delegation policy as the written guidance.
- Existing payload contracts remain stable; only guidance and JIT contract wording change.
