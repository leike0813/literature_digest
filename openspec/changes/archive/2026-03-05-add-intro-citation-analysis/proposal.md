# Change Proposal: Add Introduction-Scoped Citation Analysis Artifact

## Background

The `literature-digest` skill already outputs:
- `digest.md` (markdown digest)
- `references.json` (structured reference entries)

For literature review writing, users also need evidence-oriented notes that answer:
- Which works are cited in the target paper (at least within the Introduction)?
- How the target paper characterizes those cited works (background/baseline/contrast/etc.)?

## Problem

Digest + reference list alone is not enough to quickly draft a literature review section because:
- In-text citations are not connected to the extracted reference items.
- The paper’s framing of prior work (especially in Introduction) is not summarized in an evidence-oriented, cite-linked way.

## Goal

Add a third artifact `citation_analysis.json` that:
1. Only analyzes in-text citations within **Chapter 1 Introduction** (including its subsections).
2. Supports both numeric and author-year citation styles with high quality for author-year parsing/mapping.
3. Links each cited work to `references.json` whenever mapping is reliable.

## Non-Goals

- Do not change the existing required reference item contract.
- Do not require perfect citation disambiguation when evidence is insufficient; prefer `unmapped_mentions`.
- Do not output large content on stdout; all large artifacts must be written to files.

## Success Criteria

- stdout JSON remains a single JSON object and includes a new required key `citation_analysis_path`.
- The new artifact is written to `<dir_of_md_path>/citation_analysis.json` (UTF-8).
- `citation_analysis.json` contains:
  - scope range (Introduction lines),
  - per-reference grouped mentions,
  - `unmapped_mentions` for non-mappable citations,
  - `report_md` suitable for note rendering.

