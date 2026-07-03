# Contract: mutation benchmark (`halluc_bench.py` + `halluc-bench` CLI)

Measures the catcher: inject known hallucinations into a clean grounded spec, measure per-class recall
and overall precision, write a calibration report. This is the meta-loop (mutate → measure → tune →
re-measure) and lets weak-model gains be proven with real numbers.

## Mutators (deterministic)

Each takes a clean spec + repo and returns `(mutant_text, Mutation)` with a known ground-truth site:

| Mutator | Injects | Expected finding kind |
|---|---|---|
| `flip_citation_line` | changes a valid `:line` to a different valid line whose window lacks the claim's tokens | `claim_code_mismatch` |
| `rename_cited_symbol` | renames a cited symbol to a non-existent one | `fabricated_symbol` (or `claim_code_mismatch`) |
| `invent_api` | inserts a backticked code-like identifier absent from the repo | `fabricated_symbol` |
| `strip_label` | removes the R10 label from a claim that names a real symbol | `unlabeled_claim` |
| `alter_quantity` | changes a supported number to one absent from the cited window | `unsupported_quantity` |

Each mutator is a pure function of the clean spec (fixed input ⇒ fixed mutant + site); no randomness.

## Measurement

```
run_mutation_benchmark(repo, clean_spec, *, window=3, model="fixtures") -> CalibrationReport
```
- For each class, generate the available injections, run `detect_hallucinations` on each mutant, and
  count an injection **flagged** iff a finding of the expected kind lands at (or adjacent to) the
  injection site.
- **recall(class)** = flagged / injected (by construction from the known set).
- **precision** = `1.0` iff `detect_hallucinations(clean_spec) == []` else `0.0`.
- Writes the report (data-model "CalibrationReport") under `rubric/benchmarks/`, labeled with `model`.

### CLI — `halluc-bench`

```
reposkillopt-engine halluc-bench --repo <dir> --spec <clean-spec> [--window N] [--model <id>] [--out <path>]
```
- Prints the per-class recall table + overall precision; writes the calibration report.
- Exit `0` always on a completed run (it is a *measurement*, not a gate); `2` on usage error.

## Guarantees

- **Verifiable measurement (SC-006)** — recall/precision equal the values computed from the known
  injection set; the benchmark asserts its own arithmetic in tests.
- **Deterministic** — fixed clean spec ⇒ fixed mutants ⇒ fixed recall/precision (the only
  nondeterminism is an *optional* model whose output is the subject of a calibration run, never the
  ground truth).
- **Additive** — reuses the 007/008 report conventions; `benchmark.py` untouched; report lives under
  `rubric/benchmarks/`.
