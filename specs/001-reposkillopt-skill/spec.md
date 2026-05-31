# Feature Specification: RepoSkillOpt — Portable Cross-Agent Skill for Evidence-Grounded Repository Understanding

**Feature Branch**: `001-reposkillopt-skill`
**Created**: 2026-05-30
**Status**: Draft
**Input**: User description: "RepoSkillOpt — a portable agent skill package that helps coding agents understand legacy repositories through evidence-grounded analysis, recurrent human feedback, and skill convergence; inspired by SkillOpt; adaptable to Claude Code, Codex, OpenCode, GitHub Copilot-style agents, and generic local agents; MVP is skill-first (no SaaS, no DB, no frontend, no fine-tuning)."

## Overview

RepoSkillOpt is a **portable, skill-first** package. The deliverable is not a service or a CLI; it is a vendor-neutral Markdown skill (the *canonical skill*) plus a small set of templates, adapter examples, and an evaluation rubric. The canonical skill teaches any coding-agent harness a disciplined repository-understanding workflow, accepts human feedback as a first-class input, and supports a bounded *skill convergence* loop that turns recurrent feedback into reviewable edits to the skill itself.

The core hypothesis is: a coding agent's repository-understanding behavior can be improved by iteratively optimizing a reusable external skill artifact — through repeated repository-analysis tasks, agent rollouts, evaluator feedback, and recurrent human feedback — without fine-tuning the underlying model.

## Clarifications

### Session 2026-05-31

- Q: Where should working artifacts (Repository Specifications, Feedback Logs, Rollout Logs, Skill Edit Proposals) live inside a target repository being analyzed? → A: `.reposkillopt/` subtree at the repository root, with fixed subdirectories `specs/`, `feedback/`, `rollouts/`, `proposals/`.
- Q: How should the canonical skill be versioned, and how should adapters reference the canonical version they wrap? → A: Semantic version in YAML front matter of the canonical `SKILL.md`; each adapter mirrors it via a `canonical_version` front-matter field.
- Q: For the four MVP adapter examples (Claude Code, Codex, OpenCode, generic), against what target repository or repositories should the sample Repository Specifications be produced? → A: One small open-source legacy repository, reused across all four adapter examples, so outputs are cross-adapter comparable.
- Q: What scoring scheme should the MVP Evaluation Rubric ship with? → A: Concrete 0–3 scale per qualitative dimension (0=absent, 1=poor, 2=adequate, 3=strong) with brief anchor descriptions, plus pass/fail for each deterministic check.
- Q: How should the spec define "major claim" for the labeling/citation requirements (FR-008, FR-009, SC-002)? → A: A *major claim* is any assertion that fills a non-trivial slot in a required Repository Specification section (e.g., entrypoint identity, technology choice, dependency relationship, control- or data-flow step) OR any standalone assertion that a maintenance reader of the repository would act on. Trivial recitations (literal file contents, raw config dumps, syntactic restatements) are not major claims.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Install and use the canonical skill in a coding-agent environment (Priority: P1)

An engineer copies the canonical skill into their coding-agent environment (Claude Code skill folder, Codex `AGENTS.md`, OpenCode rules, or a generic Markdown prompt fragment). When the engineer asks the agent to understand, map, document, onboard to, refactor, modify, or assess a repository, the agent activates the skill and follows the prescribed repository-understanding workflow.

**Why this priority**: This is the entire reason the project exists. Without portable installation and reliable activation across at least one supported agent, none of the other capabilities are usable.

**Independent Test**: In a clean environment for at least one supported agent (e.g., Claude Code), drop the canonical skill (or its exported adapter) into the documented location, open a sample legacy repository, and issue an analysis request. The agent must (a) activate the skill, (b) follow the workflow sections in order, and (c) produce output that conforms to the Repository Specification structure.

**Acceptance Scenarios**:

1. **Given** the canonical skill is placed in the agent's recognized location, **When** the user asks "help me understand this repo", **Then** the agent triages structure, identifies stack, inspects manifests/configs/entrypoints, and emits a Repository Specification with the required sections.
2. **Given** a repository with only a sparse README, **When** the user asks the agent to summarize architecture, **Then** the agent does not rely solely on the README and instead inspects manifests, configs, tests, and code to ground its claims.
3. **Given** the user asks an out-of-scope question (e.g., "write me a poem"), **When** the agent receives the message, **Then** the skill does not activate and ordinary agent behavior continues.

---

### User Story 2 — Produce an evidence-grounded repository specification (Priority: P1)

An engineer points the agent at a legacy repository and asks for an analysis. The agent inspects real repository artifacts (manifests, configs, entrypoints, tests, deployment files, source) and produces a structured Repository Specification in which every major claim is categorized (verified fact, inference, unknown, or human-provided context) and cited to concrete repository evidence (file paths, symbols, command outputs, config keys).

**Why this priority**: Evidence-grounded output is the load-bearing quality of the product. Without it, the skill is just another summarizer.

**Independent Test**: Run the skill against a sample repository. The produced Repository Specification must contain all required sections, every major claim must carry a citation, and the Evidence Index must list each citation. Spot-check at least 10 citations: each cited path must exist; each cited symbol must be locatable.

**Acceptance Scenarios**:

1. **Given** a repository in a supported common ecosystem, **When** the agent produces a Repository Specification, **Then** the specification contains every section listed in FR-005 and each non-trivial claim is labeled (fact / inference / unknown / human-provided) and cited.
2. **Given** the agent cannot determine a piece of information from inspection, **When** writing the specification, **Then** it places the claim under "Unknowns and unresolved questions" rather than fabricating an answer.
3. **Given** the user asks the agent to trace a specific behavior, **When** the agent traces it, **Then** the trace lists entrypoint → intermediate modules → core logic → side effects/persistence, with file and symbol citations at each hop.

---

### User Story 3 — Provide human feedback that improves the current specification (Priority: P1)

An engineer reviews the agent's Repository Specification and provides feedback — a correction, a confirmation, a missing file the agent should have inspected, preferred terminology, a quality rating, or an instruction to avoid a misleading path. The agent records the feedback using the Human Feedback Template, revises the current specification, and re-cites evidence where claims changed.

**Why this priority**: Recurrent human feedback is the mechanism by which the skill earns trust on a specific repository and accumulates signal for the longer-term convergence loop. P1 because feedback-handling is part of the MVP loop, even before any cross-session convergence.

**Independent Test**: After producing a Repository Specification, supply at least three pieces of feedback covering different types (correction, missing-context, terminology). The agent must (a) record each item with a traceable identifier, (b) update the specification accordingly, (c) mark which claims were revised and why, and (d) not silently merge repository-specific facts into the generic skill.

**Acceptance Scenarios**:

1. **Given** the specification claims module X is the entrypoint, **When** the user corrects this to module Y, **Then** the specification is updated, the old claim is marked superseded, the new claim cites evidence, and the correction is logged.
2. **Given** the user says "you missed `services/billing/` entirely", **When** the agent receives the feedback, **Then** it inspects the indicated location and either updates the relevant sections with new cited claims or records why it could not.
3. **Given** the user gives feedback that is repository-specific (e.g., "in our codebase, 'job' always means a Kafka consumer"), **When** the agent processes it, **Then** the fact is recorded as a repository-scoped note and is **not** promoted into the generic canonical skill without an explicit scope decision.

---

### User Story 4 — Export the canonical skill to multiple agent harnesses (Priority: P2)

A user — possibly an AI engineer — takes the canonical skill and uses or generates an agent-specific adapter for at least Claude Code, Codex, OpenCode, and a generic local agent. Each adapter preserves the canonical skill's intent while conforming to the target environment's packaging conventions.

**Why this priority**: Cross-agent portability is a defining feature of the project, but P1 stories deliver value even if only one adapter is in place. P2 captures the cross-vendor breadth required for the MVP to be considered complete.

**Independent Test**: For each of Claude Code, Codex, OpenCode, and generic, an example adapter exists in the repository, is documented in the README, and — when placed in the target environment — produces behavior consistent with the canonical skill on the same sample repository (same workflow steps, same required output sections).

**Acceptance Scenarios**:

1. **Given** the canonical skill, **When** the Claude Code adapter is installed, **Then** the agent activates on the documented trigger conditions and emits Repository Specifications with the required sections.
2. **Given** the canonical skill, **When** the Codex `AGENTS.md` export is placed in a target repo, **Then** a Codex-style agent follows the same workflow and output discipline.
3. **Given** the OpenCode export, **When** an OpenCode session runs, **Then** the rules/`AGENTS.md` produce the same workflow behavior.
4. **Given** the generic Markdown export, **When** it is pasted as a system or developer prompt into a custom harness, **Then** the agent follows the workflow.
5. **Given** any adapter, **When** compared against the canonical skill, **Then** no required section, principle, or workflow step is silently dropped.

---

### User Story 5 — Distinguish verified facts from hypotheses (Priority: P2)

A technical lead reads a Repository Specification and can immediately tell which claims are grounded in inspected evidence, which are inferences from partial signal, which are unknowns, and which originate from human-provided context. The specification never presents a hypothesis as a fact.

**Why this priority**: Trust and risk control depend on this distinction. P2 rather than P1 only because it is enforced *through* the output produced by Stories 2 and 3.

**Independent Test**: Sample at least 20 claims across a produced specification. Each must carry an explicit category label and (for facts) at least one citation that can be verified by a reader without rerunning the agent.

**Acceptance Scenarios**:

1. **Given** a specification, **When** a reader inspects any major claim, **Then** the claim is labeled fact / inference / unknown / human-provided and (for fact) carries at least one citation.
2. **Given** the agent has weak evidence for a claim, **When** it writes the claim, **Then** it is labeled as an inference with the basis explained, not as a fact.

---

### User Story 6 — Refine the repository specification across iterations (Priority: P2)

A documentation owner runs multiple analysis sessions against the same repository over time. Each session begins from the prior specification, incorporates new feedback, and produces a revised specification with a clear change log.

**Why this priority**: The artifact has long-term value only if it is maintainable across sessions. Single-shot quality is covered by P1; multi-session continuity is P2.

**Independent Test**: Run two consecutive sessions against the same sample repository, providing different feedback in each. The second session must build on the first (not regenerate from scratch), the change log must record what was added/changed/removed, and prior human-provided context must not be lost without explicit replacement.

**Acceptance Scenarios**:

1. **Given** a prior Repository Specification, **When** a new session starts, **Then** the agent treats the prior specification as input, not noise.
2. **Given** prior human feedback exists in the feedback log, **When** the new session produces a specification, **Then** it addresses or explicitly defers each open feedback item.

---

### User Story 7 — Convert recurrent feedback into bounded, reviewable skill edits (Priority: P3)

A skill maintainer accumulates feedback across multiple sessions (and potentially multiple repositories) and asks the agent to summarize patterns and propose edits to the **canonical skill**. Each proposed edit is bounded (small, scoped), categorized (ADD / REPLACE / DELETE / REORDER / SPECIALIZE / GENERALIZE), justified by referenced feedback items, and individually accept/reject-able. Rejected edits are preserved for future review.

**Why this priority**: This is the SkillOpt-inspired convergence behavior. It is the most distinctive capability of the project but the least urgent for first usefulness — the prior stories already deliver value.

**Independent Test**: With a feedback log containing at least three related items pointing to the same skill weakness, request a skill-edit proposal. The agent must produce one or more proposals using the Skill Edit Proposal Template, each citing the supporting feedback. The maintainer accepts some and rejects others; accepted edits are applied to the canonical skill, rejected edits are preserved in a rejected-proposals log with rationale.

**Acceptance Scenarios**:

1. **Given** N recurring feedback items pointing to the same gap, **When** the maintainer requests proposals, **Then** at least one Skill Edit Proposal is produced citing those items.
2. **Given** a proposal is accepted, **When** it is applied, **Then** only the bounded section indicated is changed and the change is reviewable as a small diff.
3. **Given** a proposal is rejected, **When** the decision is recorded, **Then** the proposal and rationale are preserved.
4. **Given** an edit would mix repository-specific facts into the canonical skill, **When** the proposal is generated, **Then** it is either rewritten to generalize or flagged as out-of-scope for the generic skill.

---

### User Story 8 — Compare skill versions for evaluation (Priority: P3)

A researcher wants to compare two versions of the canonical skill on the same set of repository-analysis tasks and decide whether the newer version improves repository-understanding quality. The project's Evaluation Rubric and Rollout Log Template make this comparison tractable.

**Why this priority**: Important for the research thesis and for justifying skill edits, but not required for first useful use.

**Independent Test**: Two skill versions are run against the same task set in the same agent. The Rollout Logs and Evaluation Rubric scores are produced for each. A reader can identify per-dimension improvements/regressions.

**Acceptance Scenarios**:

1. **Given** two skill versions and a fixed task set, **When** rollouts are completed, **Then** Rollout Logs exist for each rollout and Evaluation Rubric scores can be produced per dimension.
2. **Given** rubric scores, **When** compared, **Then** per-dimension deltas (improvements, regressions, unchanged) are identifiable.

---

### Edge Cases

- **Repository in an unsupported or unfamiliar ecosystem**: The skill must still apply its workflow (triage, identify, inspect manifests/configs/tests, trace) and explicitly mark unknowns rather than pattern-matching from training data.
- **Empty or near-empty repository**: The skill produces a minimal specification, flags lack of evidence, and does not invent structure.
- **Monorepo with multiple stacks**: The skill must scope analysis (per-package / per-subrepo) and not blend stacks into a single misleading summary.
- **Repository whose README is materially wrong**: The skill must surface the conflict between README and code evidence and prefer code evidence.
- **Conflicting human feedback across users**: The most recent feedback is applied to the current specification; both items are preserved in the feedback log with attribution and timestamps so the conflict is visible.
- **Human feedback that is itself incorrect**: Feedback is recorded as a human-provided claim, not silently promoted to fact; the agent may push back with cited contradicting evidence.
- **Cited file or symbol that does not exist** (hallucination): A deterministic check flags any citation whose path/symbol cannot be resolved; the claim must be revised or removed.
- **Adapter drift**: An adapter that drops required workflow steps, required sections, or principles must be flagged by the adapter-equivalence check.
- **Private repository contents**: The skill must operate entirely within the user's local environment and must not exfiltrate repository contents to external services unless the user has explicitly configured that.
- **Very large repository exceeding the agent's context budget**: The workflow degrades gracefully — the agent prioritizes triage, entrypoints, manifests, and the user-requested trace; the specification marks under-inspected areas as such.
- **Skill edit proposal that is too broad to review**: The proposal is rejected by the bounded-edit check and must be split into smaller proposals.

## Requirements *(mandatory)*

### Functional Requirements

**Canonical skill artifact**

- **FR-001**: The project MUST provide a single canonical skill, stored as Markdown at `skills/repo-skillopt/SKILL.md`, that is the source of truth for all adapters.
- **FR-002**: The canonical skill MUST be vendor-neutral — it MUST NOT depend on Claude Code, Codex, OpenCode, GitHub Copilot, or any single coding-agent runtime.
- **FR-003**: The canonical skill MUST contain at least the following named sections: Purpose; Trigger Conditions; Operating Principles; Repository Understanding Workflow; Repository Specification Format; Human Feedback Loop; Skill Convergence Loop; Output Discipline.
- **FR-004**: The Trigger Conditions section MUST cause the skill to activate when the user asks to understand, map, document, onboard to, refactor, modify, or assess a repository, and MUST NOT cause activation outside those conditions.

**Repository specification structure**

- **FR-005**: The Repository Specification Format MUST require these sections: Repository overview; Technology stack; Build and runtime commands; Major entrypoints; Architectural layers; Core modules; Domain model; Data model; External integrations; Control-flow traces; Data-flow traces; Dependency map; Configuration map; Testing strategy; Deployment assumptions; Change-impact map; Known risks; Unknowns and unresolved questions; Evidence index.
- **FR-006**: A Repository Specification Template MUST exist in the repository as a reusable Markdown template matching FR-005.

**Operating principles and output discipline**

- **FR-007**: The skill MUST instruct the agent not to rely only on README files and to ground claims in repository evidence (paths, symbols, configs, tests, command outputs).
- **FR-008**: Every **major claim** in a Repository Specification MUST carry an explicit category label: verified fact, inference, unknown, or human-provided context. A **major claim** is defined as any assertion that fills a non-trivial slot in a required Repository Specification section (e.g., entrypoint identity, technology choice, dependency relationship, control- or data-flow step, integration target, risk statement) OR any standalone assertion that a maintenance reader of the repository would act on. Trivial recitations (literal file contents, raw config dumps, syntactic restatements) are not major claims and do not require labels.
- **FR-009**: Every claim labeled "verified fact" MUST carry at least one citation that points to a concrete repository artifact (file path, optionally line range, symbol name, config key, or command output).
- **FR-010**: The skill MUST instruct the agent to record uncertainty explicitly under "Unknowns and unresolved questions" rather than fabricate.
- **FR-011**: The skill MUST instruct the agent to prefer concrete repository evidence over training-data pattern matching.

**Repository-understanding workflow**

- **FR-012**: The workflow MUST prescribe these stages in order: (a) triage repository structure; (b) identify language, framework, package manager, runtime; (c) inspect manifests, configs, tests, deployment files, entrypoints; (d) map modules, layers, dependencies, domain concepts, data flow; (e) trace specific behavior from entrypoint to core logic to persistence or side effects; (f) produce a Repository Specification; (g) identify risks, unknowns, and safe next steps.

**Human feedback loop**

- **FR-013**: A Human Feedback Template MUST exist that captures, per feedback item: identifier, timestamp, author (optional), type (correction, confirmation, missing-context, terminology, quality rating, avoid-path, deeper-analysis, criticism-of-claim, format, detail-level, cross-agent-difference), referenced spec claim(s), feedback text, suggested action.
- **FR-014**: The skill MUST instruct the agent to record each piece of human feedback in the Human Feedback Template before applying it.
- **FR-015**: Human feedback MUST be used in two ways: (a) immediate revision of the current Repository Specification; (b) input to the longer-term Skill Convergence Loop.
- **FR-016**: The skill MUST NOT silently promote repository-specific facts from human feedback into the canonical skill. Such promotion requires an explicit scope decision and a Skill Edit Proposal (see FR-022).

**Rollout log**

- **FR-017**: A Rollout Log Template MUST exist that records, per session: agent identity, skill version, task description, files/paths inspected, claims produced (with categories and citations), human feedback received, revisions applied.

**Skill convergence loop**

- **FR-018**: The skill MUST define a Skill Convergence Loop that summarizes recurring feedback and produces Skill Edit Proposals.
- **FR-019**: A Skill Edit Proposal Template MUST exist and MUST require: target section, edit kind (one of ADD, REPLACE, DELETE, REORDER, SPECIALIZE, GENERALIZE), proposed text, supporting feedback item identifiers, expected effect, scope (generic vs repository-scoped), risk notes.
- **FR-020**: Each Skill Edit Proposal MUST be bounded — small enough to be reviewed and accepted or rejected as a single unit.
- **FR-021**: Accepted proposals MUST be applied as small, reviewable edits to the canonical skill. Rejected proposals MUST be preserved with rationale.
- **FR-022**: The Skill Convergence Loop MUST prefer edits that generalize across tasks and repositories; edits that would over-specialize the generic skill to a single repository MUST be flagged or rewritten.

**Adapter / export strategy**

- **FR-023**: The project MUST provide example adapters or export examples for at least: Claude Code, Codex (`AGENTS.md`), OpenCode (`AGENTS.md` or rules), and a generic Markdown skill / prompt fragment.
- **FR-024**: Each adapter MUST be a thin wrapper around the canonical skill — preserving all required sections, principles, workflow stages, and output discipline.
- **FR-025**: An adapter-equivalence check MUST be defined: a reviewer (or a deterministic check) can verify that no required section, workflow stage, principle, or output-discipline rule was dropped or weakened by the adapter.
- **FR-026**: The project SHOULD prepare for, but does not require in the MVP, a GitHub Copilot-style prompt/instruction adapter and a CLAUDE.md project-instruction export.
- **FR-027**: The project MUST clearly separate canonical-skill content from adapter packaging, and MUST clearly separate general skill instructions from repository-specific facts and notes.
- **FR-027a**: The canonical skill file MUST carry a semantic version (`version: MAJOR.MINOR.PATCH`) in YAML front matter, along with a brief changelog (in-file or in an adjacent `CHANGELOG.md`). Each adapter MUST carry a `canonical_version` field in its own front matter (or, where the target environment forbids YAML front matter, in an explicitly labeled metadata block at the top of the adapter file) identifying the canonical version it wraps. The adapter-equivalence check (FR-025) MUST verify that the adapter's `canonical_version` matches an existing canonical version.

**Evaluation rubric**

- **FR-028**: An Evaluation Rubric MUST exist covering at least these dimensions: architectural correctness; evidence quality; citation validity; file and symbol grounding; hallucination avoidance; change-localization accuracy; usefulness to an engineer; risk awareness; distinction between verified facts and hypotheses; test strategy quality; responsiveness to human feedback; repository specification completeness; repository specification maintainability; cross-agent portability; resistance to agent-specific failure modes.
- **FR-029**: The rubric MUST define a scoring scheme for each dimension that a human reviewer can apply without rerunning the agent. The MVP ships a single default scheme: every qualitative dimension (FR-028) is scored on an integer **0–3 scale** with anchor descriptions — 0 = absent, 1 = poor, 2 = adequate, 3 = strong. Per-dimension scores are recorded individually; an aggregate score MAY be reported but MUST NOT replace per-dimension scores when comparing skill versions.
- **FR-030**: The rubric MUST include deterministic checks where feasible: cited file paths exist; cited symbols exist where feasible; required output sections are present; unsupported claims are marked or removed; hallucinated files/modules/APIs are penalized; prior human feedback is addressed; exported skill preserves canonical skill intent. Each deterministic check is reported as **pass / fail** (binary), separately from the 0–3 qualitative scores defined in FR-029.

**Examples and onboarding**

- **FR-031**: The project MUST include usage examples for at least Claude Code, Codex, OpenCode, and a generic local agent, each demonstrating activation and a sample Repository Specification. All four adapter examples MUST be demonstrated against the **same** small open-source legacy reference repository (selected at planning time) so that the produced Repository Specifications are directly comparable across adapters. The reference repository's identifier (name, source URL, and pinned commit/tag) MUST be recorded alongside each example.
- **FR-032**: A top-level README MUST explain how to use the skill across supported agents, how to install/copy adapters, how to provide feedback, and how to propose skill edits.

**Portability, privacy, and local-first operation**

- **FR-033**: The MVP MUST be usable without any hosted service, database, frontend, or model fine-tuning.
- **FR-034**: The MVP MUST not require deep static analysis tooling. Inspection MUST rely on standard file reads, manifest parsing, and ordinary agent tool use.
- **FR-035**: The skill MUST instruct the agent not to send repository contents to external services unless the user has explicitly configured such behavior.
- **FR-036**: All working artifacts produced during use (Repository Specifications, Feedback Logs, Rollout Logs, Skill Edit Proposals) MUST be plain Markdown (or simple structured Markdown with YAML front matter) so that they remain human-readable and locally editable.
- **FR-036a**: Working artifacts MUST be written under a `.reposkillopt/` directory at the target repository root, using fixed subdirectories: `.reposkillopt/specs/` (Repository Specifications), `.reposkillopt/feedback/` (Feedback Log entries), `.reposkillopt/rollouts/` (Rollout Logs), `.reposkillopt/proposals/` (Skill Edit Proposals, including accepted and rejected). The canonical skill MUST instruct the agent to use this layout, and every adapter example MUST reference it.

**Scope discipline**

- **FR-037**: The project documentation MUST state explicit non-goals, including: not a SaaS product; does not claim universal repository understanding; does not support all programming languages initially; does not fine-tune the underlying model; does not replace human code review; does not auto-modify production code; does not optimize only for pretty summaries; does not treat human feedback as always correct without traceability; does not mix repository-specific knowledge into the generic skill without an explicit scope decision; does not bind the canonical skill to any single agent runtime.

### Key Entities

- **Canonical Skill**: Single source-of-truth Markdown file at `skills/repo-skillopt/SKILL.md`. Vendor-neutral. Versioned. Contains the named sections of FR-003.
- **Agent Adapter**: A thin per-environment wrapper around the canonical skill (Claude Code skill, Codex `AGENTS.md`, OpenCode rules, generic Markdown). Carries identification of which canonical version it adapts.
- **Repository Specification**: A structured Markdown document produced by the agent for a target repository, matching the Repository Specification Template (FR-005, FR-006). Lives in or alongside the target repository.
- **Human Feedback Item**: A single entry recorded via the Human Feedback Template (FR-013). Carries identifier, type, scope (repository-scoped vs candidate-for-generic), referenced claim(s), and suggested action.
- **Rollout Log**: A per-session record of what the agent inspected, claimed, cited, and was corrected on (FR-017).
- **Skill Edit Proposal**: A bounded, categorized proposed change to the canonical skill (FR-019), with supporting feedback item references and a generic-vs-repository-scoped marker.
- **Evaluation Rubric**: A scoring document (FR-028, FR-029) used to evaluate Repository Specifications and to compare skill versions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can install or copy the canonical skill (or an adapter) into at least one supported coding-agent environment and produce a Repository Specification for a sample legacy repository in a single working session of under 30 minutes of human time.
- **SC-002**: For a sample legacy repository, at least 90% of major claims in a produced Repository Specification carry an explicit category label (verified fact / inference / unknown / human-provided context).
- **SC-003**: For claims labeled "verified fact", at least 95% carry a citation whose cited path resolves to an existing file and (where applicable) whose cited symbol can be located in that file.
- **SC-004**: A produced Repository Specification contains every required section listed in FR-005, with no section silently omitted.
- **SC-005**: The project ships working adapter examples for at least four targets — Claude Code, Codex, OpenCode, and a generic local agent — and each adapter passes the adapter-equivalence check against the canonical skill.
- **SC-006**: A reviewer using only the canonical skill and an adapter can identify, without running the agent, every required canonical section, principle, workflow stage, and output-discipline rule present in the adapter — i.e., 100% canonical-section coverage in each adapter.
- **SC-007**: After three pieces of human feedback are provided against a Repository Specification, all three are reflected in the next revision of that specification, recorded in the Feedback Log with traceable identifiers, and addressed or explicitly deferred.
- **SC-008**: When the Skill Convergence Loop is run against a Feedback Log containing at least three related items, at least one bounded Skill Edit Proposal is produced that cites those items.
- **SC-009**: Every Skill Edit Proposal is small enough that a reviewer can decide accept/reject in under 5 minutes of reading.
- **SC-010**: The MVP runs end-to-end on a local developer workstation with no hosted service, no database, no frontend, no model fine-tuning, and no required network calls beyond those the user's chosen coding agent already makes.
- **SC-011**: The project's documentation explicitly states limitations (no universal repository understanding; limited initial language coverage; no replacement for human code review) in a single discoverable place.
- **SC-012**: A researcher can score two skill versions on the same task set using the Evaluation Rubric and produce per-dimension deltas without modifying either skill or running additional tooling beyond the supported agent.

## Assumptions

- **Skill-first scope**: The MVP is the canonical skill, its templates, adapter examples, rubric, and README. Helper scripts are explicitly optional and not part of acceptance.
- **Common ecosystems first**: The canonical skill is language-agnostic. For the MVP, a single small open-source legacy reference repository is used across all four adapter examples (see FR-031); additional ecosystems and reference repositories are out of scope for v1 and can be added later.
- **Working-artifact location**: Working artifacts are stored under `.reposkillopt/` at the target repository root with the fixed subdirectories defined in FR-036a. This is a project convention shared across all adapters so the canonical skill and examples can reference paths concretely.
- **Skill versioning**: Defined by FR-027a — semantic version in canonical YAML front matter, mirrored by `canonical_version` in adapter front matter (or an equivalent metadata block where YAML front matter is not permitted by the target environment).
- **Agent capabilities**: The supported coding agents can read files, list directories, and execute shell commands within the user's local environment. The skill does not assume specialized static-analysis tooling.
- **Local-first privacy**: The user controls whether repository contents leave their machine. The skill does not introduce any external network dependency of its own.
- **Human reviewers exist**: Skill Edit Proposals are accepted or rejected by a human maintainer; the project does not attempt fully autonomous acceptance.
- **Single-feature delivery**: This specification covers the RepoSkillOpt MVP as a single feature; later features (additional adapters, automated convergence tooling, hosted evaluation) are out of scope here.

## Risks and Limitations

- **Hallucinated citations**: Even with the citation requirement, agents can fabricate paths/symbols. The deterministic checks in FR-030 mitigate but cannot eliminate this; the rubric must reward citation-validity verification.
- **Overfitting the canonical skill to one repository**: Repeated feedback from a single project may push edits that hurt generality. The SPECIALIZE/GENERALIZE markers and the scope discipline in FR-022 are the primary controls; vigilance during proposal review is required.
- **Adapter drift over time**: Adapters can fall behind the canonical skill. The adapter-equivalence check (FR-025) is the primary control.
- **Cross-agent behavioral variance**: The same skill text can produce different behavior across agents. The rubric explicitly scores cross-agent portability and resistance to agent-specific failure modes, but variance cannot be fully eliminated without per-adapter tuning.
- **Context-window limits**: Very large repositories may exceed an agent's context budget; the workflow degrades gracefully but completeness suffers.
- **Incorrect human feedback**: Feedback may itself be wrong. Traceability (FR-013, FR-014) preserves the audit trail; agents may push back with cited evidence, but the human still has authority.
- **Sparse evidence**: Some legacy repositories lack tests, docs, or coherent structure. The skill will produce sparser specifications and more "unknown" items — this is correct behavior, not failure.

## Open Questions

- **OQ-3**: What is the minimum set of deterministic checks (FR-030) that should be shipped as documentation only vs. as optional helper scripts in the MVP?
- **OQ-5**: How should the project track and surface cross-agent behavioral differences observed in the wild (per-adapter notes vs. a single shared notes file)?

## Acceptance Criteria (project-level)

- **AC-01**: A canonical RepoSkillOpt skill exists at `skills/repo-skillopt/SKILL.md`.
- **AC-02**: The canonical skill is human-readable Markdown and is the single source of truth.
- **AC-03**: Following the skill, an agent can carry out evidence-grounded understanding of a legacy repository and produce a Repository Specification matching FR-005.
- **AC-04**: The skill supports a human feedback loop that records feedback (FR-013), revises the current specification, and feeds the convergence loop.
- **AC-05**: The skill supports proposing bounded skill edits from recurrent feedback, with categorization (ADD / REPLACE / DELETE / REORDER / SPECIALIZE / GENERALIZE), supporting-feedback references, and accept/reject tracking.
- **AC-06**: Adapter examples are provided for at least Claude Code, Codex, OpenCode, and a generic local agent, and each preserves canonical-skill intent.
- **AC-07**: The project clearly distinguishes (a) canonical skill content from agent-specific wrappers and (b) general skill instructions from repository-specific facts.
- **AC-08**: An Evaluation Rubric covering at least the dimensions in FR-028 is included.
- **AC-09**: The MVP runs without a hosted service, database, frontend, or model fine-tuning.
- **AC-10**: The project documentation explicitly states its limitations and does not claim universal repository understanding.
