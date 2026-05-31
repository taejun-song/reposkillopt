---
id: SP-2026-06-01-003
proposed: 2026-06-01
target_section: Operating Principles
edit_kind: ADD
scope: repository-scoped
supporting_feedback:
  - FB-2026-05-31-001
  - FB-2026-05-31-003
expected_effect: Would add Click-specific vocabulary and conventions ("multi command" as the umbrella term; the decorator-factory-vs-invocable-Command distinction) directly into the canonical skill's Operating Principles.
risk_notes: High. The content is true only of Click. Promoting it would inject repository-specific assumptions into a vendor- and repository-neutral artifact, misleading the skill on every other codebase (other CLI libraries use different terms and different entrypoint conventions).
review_time_estimate_minutes: 2
status: rejected
decided: 2026-06-01
decision_rationale: Repository-scoped — not eligible for canonical SKILL.md per FR-016/FR-022. Both supporting Feedback Items are explicitly scope:repository-scoped (FB-2026-05-31-001 is a Click entrypoint convention; FB-2026-05-31-003 is Click documentation vocabulary). Neither generalizes — "multi command" means different things across CLI libraries, and the decorator-vs-instance distinction is Click's decorator model, not a universal one. Rejected for canonical acceptance and routed to per-repository notes instead. The underlying facts already live, correctly scoped, as **[human]** claims in the click@8.1.7 Repository Specification.
---

# Skill Edit Proposal SP-2026-06-01-003

## Proposed text

(Would-be canonical addition under **Operating Principles** — **not applied**, see decision rationale and the routing note below.)

> Treat the resulting command *instance* (not the decorator factory) as the user-facing entrypoint, and use "multi command" as the umbrella term for any object that dispatches to subcommands.

## Diff against current canonical

```diff
--- skills/repo-skillopt/SKILL.md (current)
+++ skills/repo-skillopt/SKILL.md (proposed — REJECTED, not applied)
@@ Operating Principles @@
 - **Preserve human feedback as reusable knowledge only when properly scoped.** ...
+- **Entrypoints are command instances, and dispatchers are "multi commands."** Treat the resulting command instance (not the decorator factory) as the user-facing entrypoint, and use "multi command" as the umbrella term for any object that dispatches to subcommands.
```

## Justification

The supporting feedback (`FB-2026-05-31-001` decorator-factory-vs-invocable-Command; `FB-2026-05-31-003` "multi command" terminology) is real and useful — but it is **repository-scoped Click vocabulary and Click's decorator model**, not a generalizable rule.

**This proposal is flagged and rejected per FR-022, and preserved per FR-021.** Promoting it would specialize the generic skill to one repository: "multi command" is Click's term and is wrong or absent elsewhere; "the decorator factory is not the entrypoint" is true of Click's decorator API but not of CLIs built without decorators. Per FR-016/FR-022 a `scope: repository-scoped` proposal MUST NOT enter the canonical SKILL.md; it is rewritten to generalize, rejected, or routed to a per-repository scope-decision artifact.

**Routing.** No generalization survives the rewrite test, so this is rejected for canonical use and routed to the target repository's own artifacts. The facts already live there, correctly scoped, as `**[human]**` claims in the click@8.1.7 Repository Specification (*Major entrypoints* and *Domain model*) citing `FB-2026-05-31-001` and `FB-2026-05-31-003`. The canonical skill stays repository-neutral.
