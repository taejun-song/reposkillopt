# Contract — Human Feedback Item (`.reposkillopt/feedback/<id>.md`)

**Scope**: A single piece of human feedback recorded against a Repository Specification.
**Consumers**: The current Repository Specification revision; the Skill Convergence Loop; future maintainers reading the audit trail.

## Filename / id convention

`FB-YYYY-MM-DD-NNN-<slug>.md` where `NNN` is a zero-padded ordinal within the date. The id (`FB-YYYY-MM-DD-NNN`) is the stable handle used by Repository Specifications and Skill Edit Proposals.

## Required front matter (FR-013)

```yaml
---
id: FB-YYYY-MM-DD-NNN
timestamp: <ISO datetime>
author: <optional, free-form>
type: <correction|confirmation|missing-context|terminology|quality-rating|avoid-path|deeper-analysis|criticism-of-claim|format|detail-level|cross-agent-difference>
references:
  - spec_id: <Repository Specification id>
    claim_ref: <section header or quoted snippet>
scope: <repository-scoped|candidate-for-generic>
status: <open|applied|deferred|withdrawn>
---
```

## Required sections

1. `## Feedback` — what the human said (verbatim or close paraphrase).
2. `## Suggested action` — what should change as a result.

## Rules

- `scope: repository-scoped` items MUST NOT enter the canonical skill (FR-016, FR-022).
- `scope: candidate-for-generic` items become input to the Skill Convergence Loop. Promotion to canonical still requires an accepted Skill Edit Proposal (FR-016, FR-022).
- An item MUST be recorded before being applied (FR-014). The agent does not "apply then log."
- `type` MUST be one of the FR-013 enumerated values.
- `references` MUST point at least one specific claim or section in a Repository Specification.
- Withdrawn items are kept (not deleted) with `status: withdrawn` and a one-line reason in the body.

## Acceptance checklist

A Feedback Item passes when:

- [ ] Filename matches the id convention.
- [ ] Front matter present and valid; `id` matches filename prefix.
- [ ] `type` is one of the FR-013 values.
- [ ] `scope` is `repository-scoped` or `candidate-for-generic`.
- [ ] `references` non-empty and resolves to an existing Repository Specification.
- [ ] Body has `## Feedback` and `## Suggested action` sections.
- [ ] If `status: applied`, the referenced Repository Specification's matching claim shows the applied change and (for changed `**[fact]**` claims) updated citations.
- [ ] If `scope: candidate-for-generic` and the item was used to support a Skill Edit Proposal, the supporting proposal id appears in the body's *Suggested action* or in a *Trace* subsection.
