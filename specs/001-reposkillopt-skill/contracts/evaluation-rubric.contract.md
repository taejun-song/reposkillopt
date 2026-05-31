# Contract — Evaluation Rubric (`rubric/evaluation-rubric.md` + `rubric/deterministic-checks.md`)

**Scope**: The rubric reviewers use to score Repository Specifications and compare skill versions (FR-028, FR-029, FR-030; supports SC-012).
**Consumers**: Reviewers; researchers; the skill maintainer reading aggregate scores when prioritizing Skill Edit Proposals.

## Required content — qualitative rubric (`evaluation-rubric.md`)

Fifteen dimensions, in the order given in FR-028:

1. Architectural correctness
2. Evidence quality
3. Citation validity
4. File and symbol grounding
5. Hallucination avoidance
6. Change-localization accuracy
7. Usefulness to an engineer
8. Risk awareness
9. Distinction between verified facts and hypotheses
10. Test strategy quality
11. Responsiveness to human feedback
12. Repository specification completeness
13. Repository specification maintainability
14. Cross-agent portability
15. Resistance to agent-specific failure modes

For each dimension, the rubric MUST include:
- The dimension name and a one-sentence definition.
- Four one-line anchor descriptions, one per score level (0 = absent, 1 = poor, 2 = adequate, 3 = strong), per Phase 0 R9.

Aggregate rules:
- Per-dimension scores are recorded individually.
- An aggregate (sum or mean) MAY be reported but MUST NOT replace per-dimension scores for cross-version comparison (FR-029).

## Required content — deterministic checks (`deterministic-checks.md`)

Pass/fail checks (FR-030):

| Check | Pass criterion |
|---|---|
| Cited file paths exist | Every cited path resolves to a file in the target repository at the recorded commit |
| Cited symbols exist | Every cited symbol can be located in its cited file (best effort) |
| Required output sections present | All 19 FR-005 sections appear in the Repository Specification |
| Unsupported claims marked or removed | Every claim labeled `**[fact]**` carries a citation; every unverifiable claim is labeled `**[inference]**` or `**[unknown]**` |
| Hallucinated files / modules / APIs flagged | Zero claims reference a path or symbol that does not exist |
| Prior human feedback addressed | Every open Feedback Item referencing this spec is either applied or explicitly deferred |
| Exported skill preserves canonical intent | Adapter passes the Adapter Equivalence contract |

Each check is binary; results are recorded in the per-rollout scoring sheet (data-model section 8).

## Scoring sheet format

For each rollout being scored, produce a Markdown file under `rubric/scoring/<spec_id>-<rollout_id>.md` containing:

- Front matter linking back to `spec_id`, `rollout_id`, `skill_version`, `adapter`, `scored_by`, `scored_at`.
- A 15-row qualitative table (`Dimension | Score (0–3) | Notes`).
- A 7-row deterministic table (`Check | Result (pass/fail) | Notes`).
- (Optional) Aggregate sum or mean of qualitative scores.

## Acceptance checklist for the rubric documents

- [ ] `evaluation-rubric.md` covers all 15 FR-028 dimensions, in the FR-028 order.
- [ ] Each dimension has a one-sentence definition and four anchor lines (0, 1, 2, 3).
- [ ] `deterministic-checks.md` covers all seven FR-030 checks with explicit pass criteria.
- [ ] Scoring-sheet schema is documented (front matter + the two tables).
- [ ] Anchor wording is one line each and references concrete observable signals (per Phase 0 R9).
- [ ] Document states explicitly that the aggregate score MUST NOT replace per-dimension scores when comparing skill versions (FR-029).
