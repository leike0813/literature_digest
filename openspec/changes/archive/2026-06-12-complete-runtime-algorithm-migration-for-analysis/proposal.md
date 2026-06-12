## Why

`literature-analysis` now owns the public command orchestration, but its runtime algorithms still reach into `literature-digest` through migration shims. That means the new skill cannot evolve independently and still depends on another skill package at execution time.

This change completes runtime ownership: deterministic algorithms, SQLite access, render assets, and status guidance become local to `literature-analysis`.

## What Changes

- Vendor the mature runtime DB schema, deterministic algorithms, render validation, and public payload building into `literature-analysis`.
- Remove migration-only legacy bridges from the normal package.
- Copy render templates and schemas into `literature-analysis/assets`.
- Add tests that forbid `literature-analysis/scripts/**` from importing, loading, or reading `literature-digest/scripts/**` or `literature-digest/assets/**`.
- Keep old `literature-digest` unchanged.

## Capabilities

### Modified Capabilities

- `literature-analysis`: owns all normal runtime algorithms and assets while preserving the six-stage CLI and compatible public artifacts.

## Impact

- **Runtime impact**: no cross-skill package calls remain in `literature-analysis/scripts/**`.
- **Compatibility impact**: public CLI, stdout keys, DB-backed flow, and fixed artifact names remain unchanged.
- **Maintenance impact**: algorithms are now forked locally; future cleanup can split the local algorithm core into smaller domain modules without relying on the old skill.
