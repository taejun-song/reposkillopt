# Phase 1 — Data Model: Section-Scoped Retrieval

All structures are in-memory (no persistence); the only file output is the incrementally-written
spec under `<repo>/.reposkillopt/specs/`.

## SectionEvidence
The bounded slice returned for one section.

| Field | Type | Notes |
|---|---|---|
| `section` | str | canonical section name (e.g. "Data model") |
| `text` | str | line-numbered evidence block, ≤ `char_budget` and ≤ full-pack size |
| `categories` | list[str] | evidence categories that contributed (e.g. `["schema", "er-entities"]`) |
| `files` | list[str] | repo-relative paths included (deterministic order) |
| `fell_back` | bool | True when the section used the shared structure inventory (FR-005) |
| `omitted` | list[str] | items dropped to fit the budget (never silent) |

**Invariants**: deterministic for a given `(repo, section, char_budget)`; `len(text) ≤ char_budget`;
`len(text) ≤ len(full_pack.text)`.

## SECTION_EVIDENCE (static map)
`dict[str, tuple[str, ...]]` — canonical section name → ordered evidence categories (per research D2).
Categories: `readme`, `manifests`, `ci`, `entrypoints`, `top_modules`, `symbols`, `schema`,
`er_entities`, `config`, `tests`, `deploy`, `imports`, `inventory` (fallback).

## RetrievalReport (per run)
Honest peak-vs-total instrumentation.

| Field | Type | Notes |
|---|---|---|
| `baseline_chars` | int | full single-pack size (the status-quo peak) |
| `peak_section_chars` | int | largest per-section slice (the new peak) |
| `total_chars` | int | sum of all section slices (may exceed baseline — the tradeoff) |
| `fallbacks` | list[str] | sections that fell back to the inventory |
| `per_section` | list[tuple[str,int]] | (section, slice size) for the table |

**Derived**: `peak_reduction = 1 - peak_section_chars / baseline_chars` (SC-001 target ≥ 0.5).
