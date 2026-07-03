# Contract: hallucination checker (engine) + zero-install gate (shell)

The deterministic, model-free claim-support verifier. Two implementations that agree on shared
fixtures: the engine (wired into the loop + commit gate) and the standalone shell gate (zero-install).

## Engine — `detect_hallucinations(repo, artifact_path, text, *, window=3) -> list[Finding]`

- Pure function of the repo **on disk** + the artifact text. No model, no network, reproducible.
- Runs four checks (see data-model "Check semantics"); returns findings sorted by `(line, kind, token)`.
- Reuses `grounding.parse_citations`/`_resolve` (frozen), `structure.extract_symbols`/`_read`,
  `commit_gate.classify_artifact` (to scope `unlabeled_claim`). Does **not** modify any of them.

### CLI — `check-hallucination`

```
reposkillopt-engine check-hallucination --repo <dir> --file <artifact> [--window N] [--json]
```
- Prints one line per finding (`<file>:<line> <kind>: <reason>`), or `clean`.
- Exit `0` = no findings · `1` = findings present · `2` = usage (missing/unreadable path).
- `--json` emits the findings as a JSON array (for tooling).

## Shell gate — `scripts/hallucination-gate.sh`

```
scripts/hallucination-gate.sh <repo> <artifact> [--window N] [--max N]
```
- POSIX `sh` + `grep/sed/awk/sort/find` only. No Python, no engine — runs in CI, a pre-commit hook, or
  a reviewer's box (sibling to `coverage-gate.sh`).
- Implements the same four checks with the same window (D6) and code-like rule (D2).
- Exit `0` = clean · `1` = findings · `2` = bad usage. Prints `<artifact>:<line> <kind>: …` per finding.

## Parity contract (FR-008 / SC-004)

On the curated shared fixture set (one clean artifact + one carrying each of the four hallucination
classes), the shell gate and the engine MUST agree on:
- the **clean-vs-flagged verdict** for every fixture, and
- the **set of finding kinds** produced for every fixture.

They need NOT produce byte-identical messages. A parity test runs both over the fixtures and asserts
the (verdict, kinds) match. The shell test suite runs under **`bash` and `dash`**.

## Wiring (engine)

- **Refine loop** — `refine.spec_gaps(repo, spec)` additionally yields one gap string per finding, so
  the existing bounded/monotonic loop (and `commit_gate.remediate`, which shares `spec_gaps`) drives a
  hallucinated spec toward clean. Additive; existing gap sources unchanged. After a refine pass the
  finding count MUST NOT increase (FR-010).
- **Commit gate** — a new `hallucination` gate: `select_gates` includes it for
  `repo_spec`/`architecture`/`impact`; `run_gates` adds a verdict `detect_hallucinations(...) == []`.
  With a provider the artifact is remediated; without one it is blocked-and-reported (feature 021).

## Guarantees

- **Deterministic** — same artifact + repo ⇒ byte-identical findings (SC-003).
- **No false confidence** — purely semantic paraphrase (no shared code token) is out of scope and is
  neither flagged nor implied verified (FR-014).
- **Frozen respected** — `grounding` and every metric/rubric/reward definition unchanged (SC-007).
