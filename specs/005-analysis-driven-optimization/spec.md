# Feature Specification: Real-Analysis-Driven Per-Repo Skill Optimization

**Feature Branch**: `005-analysis-driven-optimization`
**Created**: 2026-06-07
**Status**: Draft
**Input**: User description: "Make per-repo SKILL.md optimization driven by how well the skill produces a thorough, evidence-grounded Repository Specification of the legacy repo — replacing the thin 8 KB-digest proxy with a cached evidence pack and deterministic citation-resolution scoring, so a run yields a specialized SKILL.md and the spec it earned."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Optimize a skill against real repository evidence (Priority: P1)

A practitioner points the optimizer at a legacy repository. Instead of scoring the skill on a one-shot generation from a tiny README+manifest digest, the optimizer gathers a rich, cached **evidence pack** from the actual repository once, then for each candidate skill produces a Repository Specification grounded in that evidence and scores it. The score reflects real grounding, not surface plausibility.

**Why this priority**: This is the core correction. Without a fitness signal tied to real repository evidence, optimizing the skill cannot reliably improve thorough, grounded analysis — which is the entire point of the project. Everything else builds on this.

**Independent Test**: Run the optimizer on a known repository with the evidence pack enabled; confirm the spec generated during scoring references real files/paths from that repository (not invented ones) and that the same evidence pack is reused across rounds rather than rebuilt.

**Acceptance Scenarios**:

1. **Given** a target repository, **When** an optimization run starts, **Then** the optimizer builds one evidence pack from the repository (tree, manifests, entrypoints, selected file contents, targeted searches) and reuses it for every candidate and round in that run.
2. **Given** the evidence pack is built, **When** a candidate skill is scored, **Then** the Repository Specification used for scoring is generated from that evidence pack, and its scoring is recorded.

### User Story 2 - Reward grounded specs, penalize hallucinated ones (Priority: P1)

The reward combines the existing rubric quality score with **deterministic checks evaluated against the real repository**: every `file:line` / `file:Symbol` citation in the spec is resolved against the actual files, all required specification sections must be present, and claim labels must be applied. A spec that invents citations scores lower than one whose citations resolve, even if both read fluently.

**Why this priority**: Deterministic, repo-grounded checks are the non-gameable backbone of the signal. They make "thorough and grounded" measurable and prevent the optimizer from rewarding confident fabrication.

**Independent Test**: Score two specs for the same repository — one with citations that resolve to real lines and one with fabricated citations — and confirm the resolving spec earns a strictly higher reward.

**Acceptance Scenarios**:

1. **Given** a spec with citations, **When** it is scored, **Then** each citation is checked against the repository and the proportion that resolve contributes to the reward.
2. **Given** a spec missing a required section or an uncited factual claim, **When** it is scored, **Then** the deterministic component of the reward is reduced and the specific failure is recorded.

### User Story 3 - Drive edits from the real gaps, and emit both outputs (Priority: P2)

The concrete deterministic failures (e.g. "cited a line that does not exist", "a required section is missing", "a factual claim has no citation") are passed to the edit-generation step as the reason the current skill underperforms, so proposed skill edits target the repository's real gaps. When the run finishes, it writes out **both** deliverables: the specialized SKILL.md for this repository and the highest-scoring Repository Specification it produced.

**Why this priority**: This turns the signal into useful, repo-specific edits and guarantees the user receives the two artifacts the project promises from a single run. It depends on Stories 1 and 2 being in place first.

**Independent Test**: Run the optimizer end-to-end on a real repository; confirm the edit-generation step receives the actual failure descriptions, and that on completion both a specialized skill file and a specification file are written to known locations.

**Acceptance Scenarios**:

1. **Given** a scored candidate with deterministic failures, **When** an edit is proposed, **Then** those failure descriptions are supplied as the improvement target.
2. **Given** a completed run, **When** the user inspects the output location, **Then** a specialized SKILL.md and the best Repository Specification are both present, and the canonical neutral skill is unchanged.
3. **Given** a completed run on the validation repository, **When** results are reviewed, **Then** at least one repository-specialized edit was accepted by the gate.

### Edge Cases

- **No resolvable citations / empty repo**: A spec with zero citations, or a repository with no inspectable source, yields a defined deterministic score (zero contribution, not a crash) and is recorded as such.
- **Malformed citations**: Citations that don't match any known form are counted as unresolved rather than skipped silently.
- **Evidence pack too large**: The evidence pack is bounded so it remains usable as model input; what was truncated or omitted is recorded rather than silently dropped.
- **No edit accepted**: If the gate rejects every candidate (as happened before), the run still completes and emits the best spec and the unchanged starting skill, clearly reporting zero accepted edits.
- **Citation resolution ambiguity**: A `file:Symbol` citation where the symbol cannot be located is treated as unresolved, not assumed valid.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The optimizer MUST build a repository **evidence pack** from the actual target repository — structure, manifests, identified entrypoints, contents of key files, and results of targeted searches — richer than the prior README+manifest digest.
- **FR-002**: The optimizer MUST build the evidence pack **once per run** and reuse it for every candidate skill and every round (no per-candidate re-exploration), so cost stays bounded.
- **FR-003**: The evidence pack MUST be bounded to a configurable size; when content is omitted to fit the bound, the omission MUST be recorded in the pack.
- **FR-004**: Candidate-skill scoring MUST generate the Repository Specification from the evidence pack.
- **FR-005**: The reward MUST combine the existing rubric quality score with a **deterministic-check component evaluated against the real repository**.
- **FR-006**: The deterministic component MUST resolve each specification citation against the repository: a `file:line` citation resolves only if the file exists and the line is in range; a `file:Symbol` citation resolves only if the symbol is found in the file; other/malformed forms count as unresolved.
- **FR-007**: The deterministic component MUST verify all required specification sections are present and that factual claims carry the required citation label.
- **FR-008**: A specification whose citations resolve MUST score strictly higher (on the deterministic component) than an otherwise-identical specification whose citations are fabricated.
- **FR-009**: The optimizer MUST pass the concrete deterministic failures of the current skill's specification to the edit-generation step as the stated improvement target.
- **FR-010**: On completion the optimizer MUST write **both** outputs: the specialized SKILL.md for the repository and the highest-scoring Repository Specification, to documented locations distinct from the canonical skill.
- **FR-011**: The canonical, vendor/repo-neutral SKILL.md MUST NOT be modified by a per-repo optimization run; specialization is a separate artifact.
- **FR-012**: Edit generation, patch application, and the accept/reject gate MUST remain owned by the existing optimization engine (this feature changes the *signal*, not those mechanics).
- **FR-013**: A run MUST complete and emit its outputs even when zero edits are accepted, reporting the accepted-edit count.
- **FR-014**: The feature MUST reuse the existing 15-dimension + 7-deterministic-check rubric and the existing keyless/API-key providers without adding heavyweight runtime dependencies.
- **FR-015**: The feature MUST be validated end-to-end on the `eco-standard-wiki` repository, producing both outputs and at least one accepted repository-specialized edit.

### Key Entities *(include if feature involves data)*

- **Evidence Pack**: The bounded, cached body of real repository evidence handed to spec generation and used as the basis for citation resolution; records what was included and what was omitted.
- **Repository Specification (candidate)**: The spec generated for a candidate skill from the evidence pack; the unit that gets scored.
- **Reward**: The combined score = rubric quality component + deterministic-against-repo component.
- **Deterministic Failure**: A specific, recorded grounding defect (unresolved citation, missing section, unlabeled claim) used both to lower the reward and to direct the next edit.
- **Run Outputs**: The two artifacts emitted per run — the specialized SKILL.md and the best Repository Specification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a fixed repository, the specification used for scoring references only real paths from that repository; an injected spec with fabricated citations scores strictly lower than the grounded one.
- **SC-002**: The evidence pack is built exactly once per run regardless of the number of rounds or candidates.
- **SC-003**: A completed run always writes both outputs (specialized skill + best spec) and leaves the canonical skill byte-for-byte unchanged.
- **SC-004**: On `eco-standard-wiki`, an end-to-end run accepts at least one repository-specialized edit and the accepted skill's specification scores higher than the starting skill's specification on the combined reward.
- **SC-005**: Across a run, the proportion of specification citations that resolve against the repository is reported, and for the accepted skill it is no lower than for the starting skill.
- **SC-006**: The deterministic-check component is computed without invoking a language model (it is reproducible from the repository and the spec text alone).

## Assumptions

- The starting point is the current engine: SkillOpt owns reflect/apply/gate; the rubric (15 dimensions + 7 deterministic checks) and the keyless `claude-cli` / API-key providers exist and are reused.
- "Specialized SKILL.md is a separate per-repo artifact" follows the previously chosen per-repo-variant approach; the canonical skill stays neutral.
- Spec generation remains a model call; only its *input* (evidence pack vs. 8 KB digest) and the *scoring* (adding repo-grounded deterministic checks) change in this milestone.
- Citation resolution operates on the repository filesystem with standard tools; no language runtime parsing/AST is required for `file:line` (range check) or `file:Symbol` (textual symbol search) resolution.
- The validation target `eco-standard-wiki` is available locally at a known path.
- Full agent-driven re-exploration per candidate is explicitly out of scope for this milestone; the cached evidence pack is the affordability mechanism.
