# Rubric — To-Be Design & Orchestration (`repo-orchestration`)

Score each dimension 0–3. Gate: no dimension regresses on the held-out set AND deterministic checks pass.

| # | Dimension | What 3 looks like |
|---|-----------|-------------------|
| 1 | Decision quality | ADRs weigh ≥2 real options with honest pros/cons; the decision follows |
| 2 | Design–evidence traceability | Every design claim ties to as-is evidence (cited) |
| 3 | Task independence | Each task is executable + reviewer-verifiable on its own |
| 4 | Acceptance crispness | Every task has a concrete, checkable acceptance criterion |
| 5 | Dependency/topo correctness | Declared deps exist; graph acyclic; topological order valid |
| 6 | Scope discipline | Plan is an artifact; no execution; out-of-scope stated; no repo facts leak to the generic skill |

## Deterministic checks (model-free, must pass)
- `check_adr(adr)` — ≥2 options; Decision + Consequences present.
- `check_task_ledger(ledger)` — every task has goal+acceptance; deps exist; acyclic; valid topological_order.
