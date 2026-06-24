# Phase 1 — Data Model

## FileSummary (one per source file, under `.reposkillopt/summaries/<path>.md`)
Markdown: a header (`# <repo-relative path>`), **Role**, **Key symbols** (`name` — what `path:line`),
**Depends on**, **Notes**. All citations repo-relative.
In-memory: `{file, role, key_symbols:[{name,line,what}], depends_on:[…], notes, skeleton_only:bool}`.
**Invariant**: every enumerated source file has exactly one summary; citations resolve repo-relative.

## SummarizeReport
`{files_total, files_summarized, skeleton_fallbacks, peak_chars, total_chars, summaries_dir}`.
**Invariant**: `files_summarized == files_total` (FR-004); `peak_chars ≤ total_chars`.

## FromSummariesEvidence
The assembled reduce input = concatenated summaries (bounded). `{text, included:[…], omitted:[…]}`.
**Invariant**: `omitted` is reported, never silent (FR-005/FR-007).

## (reused, unchanged) Repository Specification, the completeness "Symbols not yet analyzed" listing.
