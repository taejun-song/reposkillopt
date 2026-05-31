---
id: FB-YYYY-MM-DD-NNN
timestamp: <YYYY-MM-DDTHH:MM:SSZ>
author: <optional, free-form>
type: <correction|confirmation|missing-context|terminology|quality-rating|avoid-path|deeper-analysis|criticism-of-claim|format|detail-level|cross-agent-difference>
references:
  - spec_id: <Repository Specification id>
    claim_ref: <section header or quoted snippet of the claim being addressed>
scope: <repository-scoped|candidate-for-generic>
status: open
---

# Feedback Item <FB-YYYY-MM-DD-NNN>

<!--
Filename convention: FB-YYYY-MM-DD-NNN-<slug>.md
Location:           .reposkillopt/feedback/ inside the target repository

Rules:
- One Feedback Item per file. Multiple corrections = multiple files.
- Record the feedback BEFORE applying it to the Repository Specification.
- scope: repository-scoped → never enters the canonical SKILL.md.
- scope: candidate-for-generic → may be cited by a future Skill Edit Proposal,
  but promotion still requires an accepted proposal (FR-016, FR-022).
- type MUST be one of the eleven enumerated values.
- status lifecycle: open → applied | deferred | withdrawn.
- Withdrawn items are preserved (not deleted) with a one-line reason in the body.
-->

## Feedback

<!-- What the human said, verbatim or close paraphrase. -->

## Suggested action

<!-- What should change in the Repository Specification as a result. If this is candidate-for-generic and a Skill Edit Proposal is later created from it, append the proposal id to a "## Trace" subsection. -->
