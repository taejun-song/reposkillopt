# Contract — `artifact_checks.py` (deterministic, stdlib, model-free)

Each returns `CheckResult{passed: bool, failures: list[str]}`; reuses `grounding.parse_citations`/`_resolve`.

- `check_architecture_view(repo_path, text)` — every component/edge line carries a **resolvable**
  `file:line`; fails listing each uncited/unresolved node or edge.
- `check_impact_analysis(repo_path, text)` — every impact row has a citation **and** a confidence
  label in {high, medium, low}; fails listing rows missing either.
- `check_task_ledger(text)` — every task has non-empty `goal` + `acceptance`; every `depends_on` id
  exists; the dependency graph is **acyclic** (else lists a cycle); `topological_order` covers all ids
  and lists each dependency before its dependent (else lists the offending edge).
- `check_adr(text)` — ≥2 options considered; a Decision and Consequences section present.

**Guarantees**: deterministic (same input ⇒ same result), zero model calls, stdlib only. These are the
deterministic half of the validation gate for the two new skills; the rubric (0–3) is the model/human half.
