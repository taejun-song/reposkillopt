# Research & Decisions — 007 Grounding Benchmark

## R1. Manifest format
- **Decision**: a TAB-separated, comment-friendly text file (the engine has zero deps; no YAML/jq). One entry per line: `name<TAB>repo<TAB>spec`. `repo` is a local path **or** `url@commit`. `#` lines and blanks ignored.
- **Rationale**: matches the project's existing line-based manifest convention (the install manifest), keeps the engine dependency-free, and is trivially diffable/pinnable.
- **Alternatives**: JSON/YAML (rejected — adds a parser/dep or fragile hand-rolling).

## R2. Making a pinned repo available
- **Decision**: `ensure_repo(repo, scratch)`: if `repo` is an existing local path → use as-is, pin = current `git rev-parse HEAD` (or "local"). If `url@commit` → shallow-fetch that commit into `scratch/<safe-name>` (`git init` + `git fetch --depth 1 <url> <commit>` + `git checkout FETCH_HEAD`); pin = commit.
- **Rationale**: pinning by commit makes the metric reproducible; shallow fetch keeps it fast. Uses only `git`.
- **Edge**: a fetch/checkout failure → entry error (FR-009), not a crash.

## R3. The metric (reuse, don't reinvent)
- **Decision**: scoring is exactly `grounding.ground_spec(repo_path, spec_text)` → `GroundingResult{resolved, resolvable_total, rate, checks, failures}`. The benchmark records those verbatim; "resolved" is feature-005's rule.
- **Rationale**: the benchmark and the optimizer must agree by construction; the metric is already model-free and unit-tested.

## R4. Aggregate
- **Decision**: across non-error entries — `mean_rate`, `median_rate` (stdlib `statistics`), and `checks_pass_share` = fraction of entries where all 7 checks pass. Report also counts `skipped` (error entries).
- **Rationale**: mean + median guards against a single outlier; pass-share is the headline "how many specs are fully clean."

## R5. Report layout (`rubric/benchmarks/<date>-grounding.md`)
- **Decision**: YAML front matter (mode, date, entry count, aggregate); a human table (name · pin · resolved/total · rate · checks ✓/✗); an aggregate block; the reproduce command; and a **machine-readable** fenced TSV block (`name	pin	resolved	total	rate	checks_pass`) so downstream tooling needs no parser.
- **Rationale**: one artifact serves humans and scripts; commit pins make it reproducible and citable.
- **Note**: the `<date>` is passed in (the engine forbids `Date.now()`-style nondeterminism is not a constraint here, but to keep reports reproducible the date is an explicit arg/param defaulting to the run date supplied by the CLI).

## R6. Default vs generate mode
- **Decision**: **score mode (default)** reads a pre-written spec file and grounds it — zero model calls (SC-003). **generate mode (opt-in)** calls `build_evidence_pack` + `generate_spec` (engine provider) to regenerate the spec for the current canonical skill, then grounds it. Generate mode is LLM-dependent and excluded from deterministic acceptance (validated by running), mirroring how feature-005's live loop is treated.
- **Rationale**: keeps the acceptance fully deterministic/offline while still enabling a live "current-skill" number.

## R7. Seed suite
- **Decision**: seed `rubric/benchmarks/seed-manifest.tsv` from repos the project already references — `pallets/click` and the held-out reference repos — pinned by the `target_repository_commit` recorded in each shipped reference spec, scoring `examples/reference-output/*/.reposkillopt/specs/repository-specification.md` (and `examples/reference-output/held-out/*/...`).
- **Rationale**: reuses existing, already-grounded artifacts; gives an immediate, real number on first run.

## R8. Determinism & tests
- **Decision**: unit tests build 2-3 tiny fixture repos (a file with N lines + a symbol) and matching specs with known-resolving and known-broken citations; assert exact resolved/total, rate, aggregate, report fields, and that an error entry is skipped without aborting. No network, no LLM.
- **Rationale**: SC-001/002/003/005 are all checkable offline.
