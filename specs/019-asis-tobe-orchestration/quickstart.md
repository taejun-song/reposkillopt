# Quickstart — the three-stage chain

```text
repo-skillopt (existing)        repo-architecture (new)            repo-orchestration (new)
  Repository Specification  ──►  Architecture View                 ADRs + Design Doc
  (.reposkillopt/specs/)         + Change-Impact Analysis     ──►  + Task Ledger
                                 (.reposkillopt/{architecture,      (.reposkillopt/{decisions,
                                  impact}/)                          design,plan}/)
```

1. **As-is**: in your agent, "map the architecture" / "what would change if we replace X?" →
   `repo-architecture` writes the Architecture View + Change-Impact Analysis (cited, confidence-labeled).
2. **To-be**: "design the to-be for goal G and plan the work" → `repo-orchestration` writes ADRs + a
   Design Doc + a Task Ledger (independent, acceptance-tested, dependency-ordered).
3. **Drive it**: any orchestrator parses `plan/task-ledger.md` (front-matter `topological_order` + the
   task table) and executes tasks in order — the skill itself never executes.
4. **Correct it**: fix any artifact in prose → Feedback Item; recurrent generalizable patterns →
   gated Skill Edit Proposal (held-out validation gate, no rubric regression).

Validate the artifacts model-free:
```sh
python3 -m reposkillopt_engine check-artifact --kind ledger --file .reposkillopt/plan/task-ledger.md
# (also: --kind architecture|impact|adr; architecture/impact also take the repo for citation resolution)
```
