# harden-literature-digest-runtime-2026-05-15

## Why

Recent end-to-end runs exposed several runtime and parsing weaknesses in
`literature-digest`: repaired runs can still emit stale errors, `repair_db_state`
does not have a safe scripted path, reference split review can loop on false
positives, warnings are too noisy for the final JSON contract, and some Windows
/ conda execution paths remain brittle.

## What Changes

- Add lifecycle handling for runtime errors and warnings while keeping the
  public stdout JSON schema unchanged.
- Add a formal `repair_db_state` stage command and route gate output to that
  command.
- Harden reference splitting against venue text, initials, inline numeric
  references, and split-review false positives.
- Make citation function constraints more visible and keep timeline validation
  strict.
- Reduce agent overhead by auto-persisting built-in runtime templates for
  `zh-*` and `en-*` languages, aggregating final warnings, and documenting
  `--payload-file` as the primary JSON payload path.

## Impact

- Public artifact filenames and stdout keys remain unchanged.
- Runtime SQLite schema gains internal lifecycle columns with automatic
  compatibility migration.
- Existing runs continue to work; old DBs are migrated on initialization.
