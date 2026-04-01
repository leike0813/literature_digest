# Proposal

## Summary

Replace normal-path gate `sql_examples` with a new `command_example` field so the runtime gate shows the next script call and minimal payload shape instead of SQL.

Keep `sql_examples` only for repair actions, and keep the field empty on the normal main path for compatibility.

## Why

Recent runs still show agents using `sqlite3` heavily during normal execution. The gate payload currently reinforces that behavior by surfacing SQL examples on every step, even though the intended main interface is `scripts/stage_runtime.py <next_action>`.

## Goals

- Add `command_example` to non-repair gate payloads.
- Remove executable SQL guidance from normal-path gate payloads.
- Preserve `sql_examples` only for repair actions.
- Document the new field split and cover it with tests.

## Non-Goals

- No changes to stage behavior, payload contracts, or render output rules.
- No changes to repair SQL examples.
- No changes to public stdout schema beyond the gate payload itself.
