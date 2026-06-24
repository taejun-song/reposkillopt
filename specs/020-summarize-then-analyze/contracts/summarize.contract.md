# Contract — `summarize.py` (deterministic enumeration; model prose)

- `enumerate_source_files(repo) -> list[str]` — deterministic, reproducible (== `evidence._list_code_files`).
- `summarize_file(provider, repo, rel) -> FileSummary` — deterministic skeleton (symbols+lines via
  `structure`) + model role/notes; citations normalized **repo-relative**; on model failure, returns the
  skeleton (never empty). Zero-config keyless via any provider.
- `summarize_repo(provider, repo, *, char_budget) -> SummarizeReport` — a summary for EVERY enumerated
  file written under `.reposkillopt/summaries/`; reports coverage + peak/total. MUST cover 100% (FR-004).
- `normalize_repo_relative(text, repo) -> str` — strip absolute repo prefix from citations; idempotent.
- `assemble_from_summaries(repo, *, char_budget) -> FromSummariesEvidence` — read all summaries; if a
  summary is missing, raise/report (no partial-coverage silence); bound + list omissions.
- `generate_spec_from_summaries(provider, skill, repo, *, char_budget) -> (spec, stats)` — generate from
  the assembled summaries, run `ensure_symbol_completeness`, keep citations repo-relative; stats carry
  peak/total. Reuses `judge.generate_spec` + `sanitize`.
**Guarantees**: deterministic enumeration; repo-relative resolvable citations; 100% file + symbol
coverage; frozen metrics unchanged.
