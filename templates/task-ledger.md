---
target_repository: <name>
goal: <the stated goal>
design_ref: .reposkillopt/design/design-doc.md
topological_order: [T001, T002, T003]
created: <YYYY-MM-DD>
status: draft
---

# Task Ledger — <goal>

<!-- An ARTIFACT, not an executor: any orchestrator parses this. Each task is INDEPENDENT and
     individually acceptance-tested, with declared dependencies. The dependency graph is a DAG and
     `topological_order` lists every id with each dependency before its dependent (check_task_ledger). -->

| id | goal | acceptance | depends_on |
|----|------|------------|------------|
| T001 | <crisp goal> | <how a reviewer verifies it, alone> | |
| T002 | <crisp goal> | <acceptance> | T001 |
| T003 | <crisp goal> | <acceptance> | T001, T002 |
