# Contract — Section-Scoped Retrieval

## `retrieve_section_evidence(repo_path, section, *, char_budget=8000) -> SectionEvidence`

- **MUST** be deterministic & model-free: same `(repo_path, section, char_budget)` ⇒ byte-identical
  `text` (FR-003, SC-003). Zero model calls.
- **MUST** return `text` with `len(text) ≤ char_budget` **and** `len(text) ≤` full-pack size for the
  repo (FR-004).
- **MUST** map `section` to its categories via `SECTION_EVIDENCE`; for an unmapped/empty result it
  **MUST** fall back to the structure inventory and set `fell_back=True` (FR-005).
- **MUST** reuse `evidence` selection/numbering and `structure.extract_symbols`/`extract_schema`;
  **MUST NOT** import any embedding/vector library (FR-002, FR-011).
- Unknown `section` name → `ValueError`.

## `build_retrieval_report(repo_path, *, char_budget) -> RetrievalReport`

- **MUST** compute `baseline_chars` from the full single-pack, `peak_section_chars`, `total_chars`,
  and `fallbacks` across all 19 sections (FR-008, SC-005). Model-free.

## `--section-scoped` generation mode (engine)

- **MUST** be opt-in; absent the flag, the single-pack path is **byte-for-byte unchanged** (FR-007, SC-004).
- **MUST** generate sections in template order, each from only its slice, append to the on-disk spec,
  then run `ensure_symbol_completeness` **once** at the end (FR-006).
- The produced spec **MUST** still satisfy: all 19 sections present, 100% symbol coverage, citations
  resolvable, ER diagram grounded when a schema exists — via existing metrics, unchanged (FR-009, FR-010, SC-002).
- The run **MUST** print peak/baseline/total evidence figures and log inventory fallbacks (FR-008).

## Non-goals (enforced)
- No embeddings, no vector DB, no heavyweight dependency (FR-011).
- Section-scoped is never the default (FR-007).
