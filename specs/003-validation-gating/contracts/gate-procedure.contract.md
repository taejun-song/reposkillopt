# Contract — Gate Procedure (`rubric/validation-gate.md`) and Convergence-Loop integration

**Scope**: The step-by-step gate procedure, its acceptance criterion, and how it binds the Skill Convergence Loop (FR-001, FR-004, FR-006, FR-013).
**Consumers**: The maintainer running a gate; the canonical Skill Convergence Loop; adapter authors.

## The procedure (`rubric/validation-gate.md` MUST document these steps in order)

1. **Confirm eligibility** — the proposal is `scope: generic`. `repository-scoped` proposals are rejected upstream and never gated.
2. **Confirm disjointness** — none of the proposal's `supporting_feedback` repositories are in the held-out set; else record `verdict: HELD` and stop.
3. **Ensure baselines** — a baseline scoring sheet exists for each held-out member at the current released version; if the released version changed, recompute baselines first (FR-007).
4. **Build the candidate version** — apply the proposal's diff to a working copy of the canonical skill (unreleased).
5. **Regenerate** — for each held-out member, run the candidate skill to produce a fresh Repository Specification under that repo's `.reposkillopt/specs/` (FR-003).
6. **Score** — the scorer-of-record applies the rubric (15 dimensions + 7 checks) to each regenerated spec, recording candidate scores beside the baselines.
7. **Decide** — apply the deterministic verdict rule; write the Validation Gate Report.
8. **Route** — PASS → the proposal becomes eligible for `status: accepted` (then the normal version-bump flow runs, FR-013). FAIL/HELD → the proposal is rejected/held and the report is preserved (FR-012).

## Acceptance criterion (FR-004)

PASS iff **all**:
- No per-dimension score regresses (`candidate ≥ baseline`) on **every** held-out member.
- All 7 deterministic checks remain `pass` on every member.
- The proposal's `expected_effect` is realized on ≥1 dimension, OR it is a clarifying edit with an explicit recorded waiver.

Per-dimension only; an aggregate MUST NOT decide (FR-005).

## Convergence-Loop integration (the binding edit)

- `skills/repo-skillopt/SKILL.md` → *Skill Convergence Loop* gains one additive rule: **"A proposal may move to `status: accepted` only when it references a passing Validation Gate Report (`rubric/validation-gate.md`); the report authorizes — it does not replace — the version-bump flow."**
- Canonical `version` bumps `0.1.0 → 0.2.0` (minor/additive); `CHANGELOG.md` gets a `0.2.0` entry.
- All four adapters mirror the new sentence and set `canonical_version: 0.2.0` (FR-024/025/027a).
- `templates/skill-edit-proposal.md` gains an optional `validation_gate_report:` field; acceptance requires it to reference a PASS report.

## Rules

- The gate is methodology + Markdown; the verdict helper (`rubric/scripts/gate-verdict.sh`) is OPTIONAL and outside acceptance (FR-014).
- The gate never edits the canonical skill except via the normal accepted-proposal path (FR-013).
- Vendor-neutral throughout; no runtime named in the canonical addition (FR-002).

## Acceptance checklist

- [ ] `rubric/validation-gate.md` documents steps 1–8 and the FR-004 criterion verbatim in intent.
- [ ] The SKILL.md Convergence-Loop rule is present, additive, and vendor-neutral; `version: 0.2.0`.
- [ ] All four adapters mirror the rule and carry `canonical_version: 0.2.0` (re-run adapter-equivalence).
- [ ] `CHANGELOG.md` has the `0.2.0` entry.
- [ ] `templates/skill-edit-proposal.md` documents the `validation_gate_report:` field and the PASS-required-for-acceptance rule.
- [ ] A worked report gates an existing `scope: generic` demo proposal (not the bootstrapping canonical edit) to avoid circularity.
