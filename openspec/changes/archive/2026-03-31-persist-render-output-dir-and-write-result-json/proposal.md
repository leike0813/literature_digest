# Proposal

## Summary

Move final artifact-directory selection into step 1 so the runtime DB becomes the single source of truth for render output location.

At final render time, stop accepting ad hoc output-directory overrides, read the directory from SQLite, fall back to the current working directory when that record is missing, and always mirror the final stdout JSON into `./literature-digest.result.json`.

## Why

The current render path still allows a late `--out-dir` override. That keeps the final publish step partially outside the DB-authoritative workflow and makes output placement harder to reason about from gate state alone.

At the same time, external orchestration needs one fixed location for the final stdout-compatible JSON payload without relying on terminal capture.

## Goals

- Persist the final public artifact directory during `bootstrap_runtime_db`.
- Make `render_and_validate --mode render` use only the DB-stored output directory, with `cwd` fallback when the DB record is missing.
- Write the final render stdout JSON to a fixed file `./literature-digest.result.json`.
- Update gate notes, guidance, and tests so the new output-dir contract is the only documented path.

## Non-Goals

- No change to public artifact filenames.
- No change to stdout schema shape.
- No change to `render_and_validate --mode fix|check` helper behavior.
