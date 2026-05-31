---
id: SP-YYYY-MM-DD-NNN
proposed: <YYYY-MM-DD>
target_section: <one of: Purpose | Trigger Conditions | Operating Principles | Repository Understanding Workflow | Repository Specification Format | Human Feedback Loop | Skill Convergence Loop | Output Discipline>
edit_kind: <ADD|REPLACE|DELETE|REORDER|SPECIALIZE|GENERALIZE>
scope: <generic|repository-scoped>
supporting_feedback:
  - FB-YYYY-MM-DD-NNN
  - FB-YYYY-MM-DD-NNN
expected_effect: <one short paragraph>
risk_notes: <one short paragraph>
review_time_estimate_minutes: <integer 1–5>
status: proposed
decided: <YYYY-MM-DD; required when status becomes accepted or rejected>
decision_rationale: <required when status becomes accepted or rejected>
---

# Skill Edit Proposal <SP-YYYY-MM-DD-NNN>

<!--
Filename convention: SP-YYYY-MM-DD-NNN-<slug>.md
Location:           .reposkillopt/proposals/ inside the target repository

Boundedness (FR-020, SC-009):
- One accept/reject unit per file. If the change does not fit
  review_time_estimate_minutes ≤ 5, split it into multiple proposals.

Scope discipline (FR-016, FR-022):
- scope: repository-scoped MUST NOT be accepted into the canonical SKILL.md.
  Such proposals are either rewritten to generalize, or rejected, or routed
  to a per-repository scope-decision artifact.
- scope: generic is the only kind eligible for canonical acceptance.

edit_kind values:
- ADD          add new content
- REPLACE      substitute existing content
- DELETE       remove content
- REORDER      change order of existing content
- SPECIALIZE   narrow an existing rule (more specific case)
- GENERALIZE   broaden an existing rule (cover more cases)

Preservation (FR-021):
- Rejected proposals are KEPT on disk with status: rejected and a
  populated decision_rationale. Do not delete.

On acceptance:
- Apply the diff to skills/repo-skillopt/SKILL.md (in the RepoSkillOpt
  project, NOT in the target repository).
- Bump the canonical version per Keep-A-Changelog + semver:
  major if the diff breaks the adapter-equivalence checklist,
  minor if additive,
  patch if clarifying.
- Add an entry to skills/repo-skillopt/CHANGELOG.md.
-->

## Proposed text

<!-- The exact text to apply (ADD / REPLACE), to remove (DELETE), the reordering specification (REORDER), or the rewrite (SPECIALIZE / GENERALIZE). -->

## Diff against current canonical

```diff
--- skills/repo-skillopt/SKILL.md (current)
+++ skills/repo-skillopt/SKILL.md (proposed)
@@ ... @@
- <existing text>
+ <proposed text>
```

## Justification

<!-- Name the recurring pattern in the supporting feedback ids. Explain why this calls for an edit to the canonical skill rather than just a Repository Specification change. Keep concise — the reviewer needs to decide accept/reject in ≤5 minutes. -->
