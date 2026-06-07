# Contract — Benchmark Harness (007)

## `engine/reposkillopt_engine/benchmark.py`

```python
@dataclass
class BenchmarkEntry: name: str; repo: str; spec: str
@dataclass
class EntryResult: name; pin; resolved; total; rate; checks; checks_pass; failures; error
@dataclass
class Aggregate: n; skipped; mean_rate; median_rate; checks_pass_share
@dataclass
class BenchmarkReport: mode; date; entries: list[EntryResult]; aggregate: Aggregate

def parse_manifest(text: str) -> list[BenchmarkEntry]
    # TAB-separated name<TAB>repo<TAB>spec; skip blank / '#' lines; error on malformed line.

def ensure_repo(repo: str, scratch_dir: str) -> tuple[str, str]
    # local path -> (path, 'local' or HEAD sha); 'url@commit' -> shallow fetch+checkout -> (path, commit).
    # raises on failure (caller records an EntryResult.error).

def run_entry(entry: BenchmarkEntry, scratch_dir: str, *, mode='score',
              provider=None, skill_text=None) -> EntryResult
    # score: read entry.spec -> ground_spec(repo, spec_text)
    # generate: build_evidence_pack(repo)+generate_spec(provider, skill_text, name, pack.text) -> ground_spec
    # any exception -> EntryResult(error=...); never raises.

def aggregate(results: list[EntryResult]) -> Aggregate
    # over non-error results: mean/median rate (stdlib statistics), checks_pass_share; skipped = error count.

def render_report(report: BenchmarkReport, *, manifest_path: str) -> str
    # YAML front matter + human table + aggregate + reproduce cmd + machine-readable TSV block.

def run_benchmark(manifest_text: str, *, mode='score', date: str, provider=None,
                  skill_text=None, scratch_dir=None) -> BenchmarkReport
    # parse -> per-entry run -> aggregate; returns the report object.
```

### Invariants
- **Score mode makes zero model calls** (SC-003). `ground_spec` is the only scorer; numbers match feature-005.
- **Determinism**: same manifest + same spec files + same pinned commits ⇒ identical `EntryResult` numbers (SC-002).
- **No abort on failure**: a bad entry yields `EntryResult.error`; `run_benchmark` completes; `aggregate.skipped` counts them (FR-009).
- **No new heavyweight dep**: stdlib + `git`. Canonical skill / rubric / feature-005 untouched (FR-011).

## CLI (`cli.py`)

```
reposkillopt-engine benchmark --manifest <path> [--mode score|generate] [--out <dir>]
                              [--date <YYYY-MM-DD>] [--skill <path>] [--rollout-provider <p>]
```
- writes `rubric/benchmarks/<date>-grounding.md` (or `--out`); prints the aggregate (mean/median rate, pass-share, skipped).
- `--mode generate` requires `--skill` + `--rollout-provider`.

## Seed manifest (`rubric/benchmarks/seed-manifest.tsv`)
- pinned `url@commit` (or local) rows for `pallets/click` + held-out reference repos, each pointing at the shipped `examples/reference-output/.../specs/repository-specification.md`.
