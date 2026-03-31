# Proposal

## Summary

Slim the active literature-digest guidance by removing per-step “common mistakes” blocks from `SKILL.md` and by deleting legacy-evolution wording from agent-facing docs.

## Why

The current guidance still carries historical migration phrasing such as “old payload”, “legacy snapshot”, and “deprecated staged pipeline” language. That context is not useful for runtime execution and makes the active instructions longer and noisier than necessary.

## Goals

- Remove every `本步最常见错误` section from `SKILL.md`.
- Rewrite active guidance so it describes only the current contract.
- Remove runtime-guidance references to historical traceability materials.
- Update guidance tests to enforce the slimmer wording.

## Non-Goals

- No runtime behavior changes.
- No schema changes.
- No gate state-machine changes.
- No deletion of archive or traceability files themselves.
