## Why

`literature-analysis` prepare responses can exceed tool stdout truncation limits because they inline large reference and citation work packages. Subagent delegation also becomes impractical when the main agent must manually extract and pass large package subsets through prompt strings. The runtime should own work package materialization and batch splitting.

## What Changes

- Prepare stdout becomes path-first for reference core review, metadata enrichment, and citation semantic review.
- Runtime writes manifest and batch JSON files under `.literature_analysis_tmp/agent_work/`.
- Each subagent batch contains at most 10 items and is self-contained.
- Stdout returns small contract fields, counts, manifest paths, and batch paths instead of large package arrays.
- Submit payload schemas, CLI stages, SQLite SSOT, and final artifacts remain unchanged.

## Impact

- Prepare output stays below truncation risk for larger papers.
- Main agents no longer manually split full worksets for subagents.
- Subagents can receive a concise prompt with a batch file path, read exactly one batch, and return a draft.
