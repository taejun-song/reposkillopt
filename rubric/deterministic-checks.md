# RepoSkillOpt Deterministic Checks

**Scope**: Seven binary (pass/fail) checks applied to a Repository Specification and its producing rollout (FR-030). These complement the qualitative dimensions in `rubric/evaluation-rubric.md`. Each check is mechanical: a reviewer (or a helper script) can decide pass/fail without judgement.
**Companion**: `rubric/evaluation-rubric.md` (the fifteen qualitative dimensions).

## The seven checks (FR-030)

| # | Check | Pass criterion |
|---|---|---|
| 1 | Cited file paths exist | Every cited path resolves to a file in the target repository **at the recorded `target_repository_commit`**. |
| 2 | Cited symbols exist | Every cited symbol (`path:Symbol`) can be located in its cited file (best effort — line drift tolerated, absence is not). |
| 3 | Required output sections present | All 19 FR-005 sections appear, in order, in the Repository Specification. |
| 4 | Unsupported claims marked or removed | Every `**[fact]**` claim carries at least one citation; every unverifiable claim is labeled `**[inference]**` or `**[unknown]**`. |
| 5 | Hallucinated files / modules / APIs flagged | Zero claims reference a path or symbol that does not exist at the recorded commit. |
| 6 | Prior human feedback addressed | Every open Feedback Item referencing this spec is either applied (and traceable in the Change log) or explicitly deferred. |
| 7 | Exported skill preserves canonical intent | The producing adapter passes the Adapter Equivalence contract (`contracts/adapter-equivalence.contract.md`); its `canonical_version` resolves to an existing canonical `version`. |

Each check yields exactly `pass` or `fail`. There is no partial credit; a single hallucinated path fails check 5, a single missing section fails check 3.

## Relationship to the qualitative rubric

The deterministic checks are necessary but not sufficient. A spec can pass all seven checks (well-formed, no hallucinations, all sections present) and still score low on, e.g., *Usefulness to an engineer* or *Risk awareness*. Conversely, a single deterministic failure (a hallucinated path) caps the related qualitative dimensions: check 5 failing means *Hallucination avoidance* (dimension 5) cannot score above 1.

## Scoring-sheet format

For each rollout being scored, produce a Markdown file at `rubric/scoring/<spec_id>-<rollout_id>.md` with:

1. **Front matter** linking back to the scored artifacts:

   ```yaml
   ---
   spec_id: <Repository Specification id>
   rollout_id: <Rollout Log id>
   skill_version: <canonical version the adapter mirrored>
   adapter: <claude-code|codex|opencode|generic>
   scored_by: <reviewer identifier>
   scored_at: <YYYY-MM-DDTHH:MM:SSZ>
   ---
   ```

2. **Qualitative table** — 15 rows, one per dimension, in FR-028 order:

   | Dimension | Score (0–3) | Notes |
   |---|---|---|

3. **Deterministic table** — 7 rows, one per check:

   | Check | Result (pass/fail) | Notes |
   |---|---|---|

4. **(Optional) Aggregate** — sum or mean of the 15 qualitative scores, explicitly marked *advisory*. The aggregate MUST NOT be used in place of the per-dimension vector when comparing skill versions (FR-029).

## Version comparison

To compare `skill_version: 0.1.0` against a hypothetical `skill_version: 0.2.0`, score each version's rollout with this same schema and diff the **per-dimension** rows (and the per-check rows). A regression on any single dimension is visible even when the advisory aggregate is unchanged. This is the mechanism behind SC-012.
