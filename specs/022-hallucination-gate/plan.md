# Implementation Plan: Deterministic Hallucination Catcher (Claim-Support Verifier)

**Branch**: `022-hallucination-gate` (stacked on `021-commit-gate-hook`) | **Date**: 2026-07-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/022-hallucination-gate/spec.md`

## Summary

Citation resolution (frozen `grounding`) proves a cited location *exists*; it does not prove that
location *supports the claim*. Weak, small-context models exploit exactly that gap. This feature adds a
**deterministic, model-free lexical claim-support verifier** with four checks — claim↔cited-code token
match, fabricated-symbol, unlabeled-claim, unsupported-quantity — that read the repo **from disk**
(never the context window, so it suits small models and cannot itself hallucinate). It ships as a new
engine module `hallucination.py` + a zero-install POSIX-`sh` `scripts/hallucination-gate.sh`, is wired
into `refine.spec_gaps` (the loop targets hallucinations) and as a new gate in the feature-021 commit
gate, and is measured by a **mutation benchmark** (`halluc_bench.py`) that injects each hallucination
class into a clean spec and reports per-class **recall** + overall **precision**, per model.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine); POSIX `sh` (the gate, authored/tested under `bash` and `dash`).
**Primary Dependencies**: None new. Reuses `grounding` (**frozen** — `parse_citations`, `Citation`, `_resolve`), `structure.extract_symbols`/`_read`, `quality` (label-rate notion), `refine.spec_gaps`, `commit_gate` (feature 021 — adds a gate), `benchmark` (007/008 report conventions), `evidence._list_code_files`. Stdlib only (`re`, `pathlib`, `dataclasses`).
**Storage**: Filesystem. Calibration reports under `rubric/benchmarks/` (Markdown + YAML front matter, additive). The catcher itself is stateless.
**Testing**: `unittest` for the engine; POSIX-`sh` tests under `bash` **and** `dash` for the gate (matching `scripts/tests/`); a parity test asserts the gate and the engine agree on shared fixtures.
**Target Platform**: Any POSIX shell + Python ≥ 3.10.
**Project Type**: Deterministic verification tooling on top of the optional engine + the portable skill package.
**Performance Goals**: Model-free and disk-local — no model call, no repo content in context. Linear in artifact size × claims; reads only the cited files (windowed), not the whole repo into memory.
**Constraints**: Deterministic/reproducible (same artifact + repo ⇒ byte-identical findings); stdlib + POSIX sh; **no new deps**; `grounding` and every metric/rubric/reward definition **unchanged** (new module + new gate, not an edit to grounding). The window size and the "code-like identifier" rule are documented + adjustable. Honest blind spot: purely semantic paraphrase hallucinations (no shared lexical token) are NOT caught (FR-014); the optional model-judge tier is deferred.
**Scale/Scope**: One new engine module + one benchmark module + one shell gate; small edits to `refine.py`, `commit_gate.py`, `cli.py`; tests + docs. Scope = `.reposkillopt/` claim-bearing artifacts.

## Constitution Check

*GATE: must pass before Phase 0 and re-checked after Phase 1.*

| Principle | Assessment |
|-----------|------------|
| **I. Evidence-Grounded Output** | **Directly strengthens it.** The catcher raises the bar from "citation resolves" to "citation *supports* the claim", and enforces the R10 label discipline (unlabeled-claim check). No artifact ships with a fabricated/mis-cited claim. ✅ |
| **II. Vendor Neutrality** | No canonical `SKILL.md` normative content touched; the catcher is engine/script tooling. Weak-model motivation (Qwen) is a rationale, not skill content. ✅ |
| **III. Adapter-Equivalence** | No skill modified → no `canonical_version` bump. ✅ |
| **IV. Deterministic & Reproducible, Stdlib-Only** | The catcher is **entirely model-free and reproducible** — its whole point. Stdlib Python + POSIX sh; no new deps; no SaaS/DB/network. The benchmark's *mutations* are deterministic; only the (optional) model whose output is *being measured* is nondeterministic, and that is the subject, not the tool. ✅ |
| **V. Bounded, Gated Self-Improvement** | Findings feed the existing bounded/monotonic refine loop + commit gate; nothing new is silently promoted. The mutation benchmark is the meta-gate that measures the detector itself. ✅ |
| **VI. Test-First for Engine Code** | `hallucination.py` + `halluc_bench.py` built TDD (positive *and* negative per check); full suite stays green; `grounding` is **not** modified (stays frozen). ✅ |

**Result: PASS, no violations.** Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/022-hallucination-gate/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/
│   ├── hallucination-checker.contract.md   # the engine catcher + the shell gate (checks, findings, exit codes)
│   └── mutation-benchmark.contract.md       # mutators, recall/precision, calibration report
├── checklists/requirements.md               # written (all-pass)
└── tasks.md                                 # /speckit.tasks output
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── hallucination.py      # NEW — Finding + the four checks + detect_hallucinations(repo, path, text)
├── halluc_bench.py       # NEW — mutators, run_mutation_benchmark, recall/precision, calibration report
├── refine.py             # EDIT — spec_gaps() also yields hallucination findings (loop targets them)
├── commit_gate.py        # EDIT — add HALLUCINATION gate to select_gates/run_gates (claim-bearing kinds)
└── cli.py                # EDIT — `check-hallucination` + `halluc-bench` subcommands

scripts/
├── hallucination-gate.sh # NEW — zero-install POSIX-sh gate (same 4 checks; grep/sed/awk)
└── tests/test_hallucination_gate.sh  # NEW — checks + engine-parity, under bash AND dash

engine/tests/
├── test_hallucination.py # NEW (TDD) — 4 checks (positive+negative), reproducibility, refine/commit wiring
└── test_halluc_bench.py  # NEW (TDD) — mutators + recall/precision computed vs the known injection set

engine/README.md          # EDIT — "Hallucination catcher" section (checks, blind spot, gate, benchmark)
```

**Structure Decision**: A new `hallucination.py` (mirrors how `artifact_checks`/`summarize` were added —
one focused module), a sibling shell gate to `coverage-gate.sh`, and a separate `halluc_bench.py` so
`benchmark.py` (007) stays untouched. Wiring is two **small additive edits** (`refine.spec_gaps`,
`commit_gate` gate set) — the catcher becomes a first-class gate without changing any metric definition.

## Phase 0 — Research (see research.md)

Decisions: **D1** claim unit = a `[fact]` span + its citation; checkable tokens are *code* tokens (the
pure-prose case is the documented blind spot). **D2** "code-like identifier" rule
(snake_case/CamelCase/dotted/`foo()`/path-like/known-symbol; plain words excluded). **D3**
fabricated-symbol = code-like backtick absent from `extract_symbols` names *and* the file tree
(empty-symbol repo → file-tree fallback). **D4** unlabeled-claim = a prose line naming a resolvable
file/symbol with no R10 label (scoped to claim-bearing kinds). **D5** unsupported-quantity = a number
in a `[fact]` absent from the cited window (excl. citation/line/version numbers). **D6** window default
±3 lines, documented + tunable. **D7** findings sorted by (line, kind) for reproducibility. **D8**
shell-gate parity = same verdict + kinds on a curated shared fixture set (not byte-identical messages).
**D9** `refine.spec_gaps` additively yields hallucination gaps. **D10** commit gate adds a
`hallucination` gate for repo_spec/architecture/impact. **D11** benchmark mutators + recall/precision +
calibration report under `rubric/benchmarks/`.

No `NEEDS CLARIFICATION` remain (the three product forks were resolved before `/speckit.specify`).

## Phase 1 — Design & Contracts

- **data-model.md** — `Finding`, `CheckKind`, `CheckableToken`, `Mutation`, `MutationClass`,
  `CalibrationReport`; the determinism ordering + the window/code-like rules stated normatively.
- **contracts/hallucination-checker.contract.md** — `detect_hallucinations(repo, path, text) ->
  [Finding]`, the `check-hallucination` CLI, `hallucination-gate.sh` (args, exit 0/1/2), and the
  engine↔shell parity contract.
- **contracts/mutation-benchmark.contract.md** — mutator set, recall/precision definitions,
  `halluc-bench` CLI, calibration-report schema.
- **quickstart.md** — catch each class → shell gate in CI → loop drives a hallucinated spec clean →
  benchmark prints per-class recall/precision.
- Update agent context via `.specify/scripts/bash/update-agent-context.sh claude`.
