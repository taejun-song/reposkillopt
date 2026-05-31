# Quickstart — Running the Gate in Majority Mode

**Audience**: A maintainer gating a high-stakes `scope: generic` proposal who wants the decision backed by multiple independent scorers rather than one.

**Estimated time**: ~N× a single-scorer run (one session for N=3 on a small held-out set).

> Majority mode is a refinement of *how the gate is scored* (feature 003). It changes nothing the gate *requires* — so it needs no canonical-skill or adapter change. Single-scorer mode (feature 003) remains valid for low-risk edits.

## When to use majority mode

Required when **any** holds (see `contracts/scoring-modes.contract.md`):
1. the edit touches the **Operating Principles** section, **or**
2. the proposal **previously failed** a gate, **or**
3. the single scorer-of-record had **low confidence** on a decisive dimension.

Otherwise single mode is fine.

## Steps

1. **Pick the roster.** Choose an **odd N ≥ 3** of independent scorers (human and/or agent). Default N = 3; use 5/7 for the highest-stakes edits.
2. **Score blind.** Each scorer applies `rubric/evaluation-rubric.md` (15 dims) and `rubric/deterministic-checks.md` (7 checks) to each regenerated held-out spec **without seeing the others' scores**.
3. **Aggregate per dimension.** For each dimension, take the **majority** value; if all differ, the **median**, marked low-agreement. Record each scorer's value, the aggregate, the method, and the range.
4. **Handle contested dimensions.** A dimension that is **low-agreement and at or below baseline** is a possible masked regression — **adjudicate** it (re-score to resolution and record who/what). If left unresolved, the verdict is **HELD**, not PASS.
5. **Decide.** Apply the verdict rule:
   - **FAIL** — any dimension aggregate below baseline, or any check fails.
   - **HELD** — no FAIL, but a contested at-or-below dimension is unadjudicated.
   - **PASS** — no regression, every contested at-or-below dimension adjudicated, effect realized/waived.

   Optional convenience:
   ```sh
   rubric/scripts/majority-aggregate.sh rubric/gates/VG-2026-06-02-001-majority-pass.md   # prints PASS|FAIL|HELD
   ```
6. **Record.** Write a Majority Gate Report (`rubric/gates/VG-…md`, `mode: majority`) per `contracts/majority-gate-report.contract.md` — roster + independence attestation, per-scorer matrix, aggregated table, adjudications, verdict. Reference it from the proposal.

## What you have now

| Path | Content |
|---|---|
| `rubric/gates/VG-…-majority-pass.md` | A majority verdict with the full per-scorer matrix + aggregation |
| `rubric/gates/VG-…-majority-held.md` | A HELD example (unadjudicated contested potential-regression) |
| `rubric/scoring/<repo>-…-majority-baseline.md` | N-scorer aggregated baselines |

## Notes

- A single outlier scorer can't flip a dimension when the rest agree — that's the point.
- "Aggregation" here is **across scorers within one dimension** — not the cross-dimension aggregate the rubric forbids from replacing per-dimension comparison.
- The verdict is reproducible from the recorded per-scorer matrix: re-aggregating yields the same PASS/FAIL/HELD.
