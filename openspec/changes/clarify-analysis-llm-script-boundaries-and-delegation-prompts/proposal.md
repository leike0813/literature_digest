## Why

Agents still overuse temporary scripts for semantic reference review, metadata enrichment, and citation semantic analysis. They can also miss citation subagent delegation because the prompts are present but not attached strongly enough to the exact task points. The skill needs clearer current-state boundaries: scripts may parse, validate, serialize, and render; LLM/subagents must perform semantic review.

## What Changes

- Strengthen `SKILL.md` LLM/script responsibility rules with explicit prohibited temporary-script substitutions.
- Add mandatory delegation points for reference core review, reference metadata enrichment, and citation semantic review.
- Add LLM/script responsibility sections to each detailed reference guide.
- Reorganize reference and citation subagent guidance so each delegatable task names the prompt to use at that point.
- Keep public CLI, payload schema, SQLite SSOT, and artifacts unchanged.

## Impact

- Agents get less room to confuse JSON helper scripts with semantic review automation.
- Subagent delegation becomes a task-level instruction rather than a general suggestion.
- Existing runtime tests and output contracts remain stable.
