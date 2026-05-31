# Quickstart — Running the Validation Gate

**Audience**: A skill maintainer deciding whether to accept a `scope: generic` Skill Edit Proposal.

**Estimated time**: one working session (depends on held-out set size).

> This is methodology layered on the existing rubric. It requires no service or tooling — an optional `rubric/scripts/gate-verdict.sh` can compute the verdict from a report, but the rule is fully written out in `rubric/validation-gate.md`.

## Prerequisites

- A `scope: generic` Skill Edit Proposal (`SP-…`) you are considering accepting.
- The held-out reference set (`rubric/held-out-set.md`) with current baseline scoring sheets for the released skill version.

## Steps

1. **Eligibility + disjointness.** Confirm the proposal is `scope: generic`, and that none of its `supporting_feedback` repositories appear in the held-out set. If one does, the gate is `HELD` — fix the set or the proposal first.

2. **Baselines current?** Ensure each held-out member has a baseline sheet for the *current released* version. If the released version changed since, recompute baselines first.

3. **Build the candidate.** Apply the proposal's diff to a working copy of `skills/repo-skillopt/SKILL.md` (do not release it).

4. **Regenerate.** For each held-out repo, run the candidate skill and produce a fresh Repository Specification under that repo's `.reposkillopt/specs/`.

5. **Score.** As scorer-of-record, apply `rubric/evaluation-rubric.md` (15 dims) and `rubric/deterministic-checks.md` (7 checks) to each regenerated spec; record candidate scores next to the baselines.

6. **Decide.** Write a Validation Gate Report (`rubric/gates/VG-…md`) per `contracts/validation-gate-report.contract.md`. Verdict:
   - **PASS** — no dimension regressed on any repo, all checks still pass, and the proposal's expected effect shows on ≥1 dimension (or is a waived clarifying edit).
   - **FAIL** — any regression or check flip, or no realized effect. Name the dimension(s)/check(s) and repo(s).

   Optional convenience:
   ```sh
   rubric/scripts/gate-verdict.sh rubric/gates/VG-2026-06-01-001-*.md   # prints PASS or FAIL
   ```

7. **Route.** On **PASS**, set `validation_gate_report: VG-…` on the proposal and proceed with the normal acceptance flow (apply the diff, bump the canonical version, add a CHANGELOG entry, mirror to adapters). On **FAIL/HELD**, leave the proposal unaccepted and **keep** the report.

## What you have now

| Path | Content |
|---|---|
| `rubric/gates/VG-…md` | The gate decision with per-dimension baseline-vs-candidate evidence |
| `rubric/scoring/<repo>-<ver>-baseline.md` / `-candidate.md` | The scored sheets behind the verdict |
| `<held-out-repo>/.reposkillopt/specs/…` | The regenerated specs that were scored |

## Notes

- Only `scope: generic` proposals are gated; repository-scoped ones never reach the gate.
- The verdict is reproducible from the report's recorded scores — re-reading the tables yields the same PASS/FAIL.
- The held-out set deliberately **excludes `pallets/click`**, since click motivates the project's demo proposals (you must not validate a change on the very repo that prompted it).
