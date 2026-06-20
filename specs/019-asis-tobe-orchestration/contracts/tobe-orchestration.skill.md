# Contract — `repo-orchestration` skill (to-be)

- **Activation**: "design the to-be / plan the work / produce a task plan for goal X". Vendor-neutral.
- **Consumes**: the as-is artifacts (Architecture View + Change-Impact Analysis) + a stated goal.
- **Produces**: **ADRs** (`.reposkillopt/decisions/ADR-NNN-*.md`), a **Design Doc**
  (`.reposkillopt/design/design-doc.md`), and a **Task Ledger** (`.reposkillopt/plan/task-ledger.md`),
  per the templates. The Task Ledger is an **artifact, not an executor** — the skill MUST NOT run anything.
- **Discipline**: every design claim traceable to as-is evidence; every task independent +
  acceptance-tested with declared `depends_on`; the dependency graph acyclic + a valid `topological_order`.
- **Deterministic checks** (gate): `check_adr`, `check_task_ledger` pass.
- **Rubric**: decision quality, design–evidence traceability, task independence, acceptance crispness,
  dependency/topo correctness, scope discipline (0–3 each).
- **Feedback / convergence / adapters / versioning**: identical to the as-is skill's contract.
