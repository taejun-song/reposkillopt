---
name: repo-skillopt
description: Evidence-grounded legacy-repository understanding with recurrent human feedback and bounded skill convergence. Activates when the user asks to understand, map, document, onboard to, refactor, modify, or assess a repository.
canonical_version: 0.5.0
adapter: generic
---


# RepoSkillOpt — Repository Understanding Skill

## Purpose

This skill helps a coding agent understand a legacy repository through evidence-grounded analysis and human-feedback-driven refinement. It produces a structured Repository Specification, accepts human corrections as a first-class input, and supports a bounded loop in which recurrent feedback is summarized into reviewable edits to the skill itself. The skill is vendor-neutral: it does not depend on any particular coding-agent runtime.

## Trigger Conditions

Activate this skill when the user asks to **understand, map, document, onboard to, refactor, modify, or assess** a repository — or uses recognizable equivalents of those verbs (e.g., "explain this codebase," "summarize the architecture," "what would change if we…", "is it safe to…").

Do **not** activate this skill for requests that fall outside the verbs above (e.g., generic chat, unrelated writing tasks, single-file edits that do not require repository-level understanding). Ordinary agent behavior continues in those cases.

## Operating Principles

- **Do not rely only on README files.** README contents are evidence, not the whole truth. They may be outdated, aspirational, or wrong. Always corroborate against code, configs, tests, and command outputs.
- **Ground every major claim in repository evidence.** Prefer concrete paths, symbols, configs, tests, and command outputs over generic descriptions. A *major claim* is any assertion that fills a non-trivial slot in a Repository Specification section (entrypoint identity, technology choice, dependency relationship, control- or data-flow step, integration target, risk statement) or any standalone assertion a maintenance reader would act on. Trivial recitations (literal file contents, raw config dumps, syntactic restatements) are not major claims.
- **Separate verified facts from hypotheses.** Every major claim carries exactly one of four labels (defined under *Output Discipline* below): `**[fact]**`, `**[inference]**`, `**[unknown]**`, `**[human]**`.
- **Identify uncertainty explicitly.** When information cannot be determined from inspection, record the gap under *Unknowns and unresolved questions* rather than guessing. An honest "unknown" is more useful than a confident wrong answer.
- **Prefer concrete evidence over training-data pattern matching.** Two repositories in the same ecosystem can differ in ways that pattern matching will miss. Inspect this repository.
- **Do not overclaim architecture from shallow inspection.** If you have only read manifests and a handful of entrypoints, do not describe layers and data flows as if you had traced them.
- **Preserve human feedback as reusable knowledge only when properly scoped.** Repository-specific facts stay repository-scoped; only feedback explicitly marked candidate-for-generic enters the convergence pipeline that targets this skill itself, and even then only via an accepted Skill Edit Proposal.

## Repository Understanding Workflow

Execute the following stages in order. Skipping or reordering stages weakens the evidence chain that downstream sections depend on.

(a) **Triage repository structure.** List the top-level directories. Note presence of `src/`, tests, docs, deployment files, CI configuration, multiple subprojects (monorepo signal).

(b) **Identify language, framework, package manager, and runtime.** Read manifests (`pyproject.toml`, `package.json`, `go.mod`, `pom.xml`, `Cargo.toml`, `Gemfile`, `composer.json`, etc.). Record versions and runtime constraints.

(c) **Inspect manifests, configs, tests, deployment files, and entrypoints.** Read at least: build/runtime configs, environment templates, CI workflow definitions, test runner configuration, deployment manifests, and the files identified as entrypoints (CLI scripts, HTTP route registrations, library `__init__` / `index` files).

(d) **Map modules, layers, dependencies, domain concepts, and data flow.** Walk the source tree; assign each module a role; identify the dependency direction between layers; record the names domain experts in this codebase use. **Enumerate every function and class defined in the repository** so none is silently skipped (see the symbol-accounting rule under *Repository Specification Format*).

(e) **Trace specific behavior from entrypoint to core logic to persistence or side effects.** For at least one user-relevant behavior, produce a numbered trace listing every hop (entrypoint → middleware → service → repository → side effect/storage), citing the file and symbol at each hop.

(f) **Produce a Repository Specification.** Use the Repository Specification template at `templates/repository-specification.md` and fill all 19 required sections. Apply the label-and-citation discipline from *Output Discipline*.

(g) **Identify risks, unknowns, and safe next steps.** Populate *Known risks* with repository-specific (not generic) risks, each tied to evidence. Populate *Unknowns and unresolved questions* with every gap surfaced during stages (a)–(f). Suggest concrete next steps a human can take to resolve key unknowns.

(h) **Guarantee symbol completeness (deterministic — final action).** Before finishing, make the *Symbols not yet analyzed* listing **complete and mechanical**: every function and class not already discussed must appear there, grouped by file, with the counts line. Generate this listing deterministically — by running a completeness helper that enumerates the repository's symbols and lists the ones the analysis did not name — rather than transcribing it by hand. Your job is the *analysis* (the prose above); this step guarantees the *accounting* so nothing is silently skipped.

## Repository Specification Format

The Repository Specification template lives at `templates/repository-specification.md`. The agent MUST produce a file matching that template, with all 19 sections present in this order:

1. Repository overview
2. Technology stack
3. Build and runtime commands
4. Major entrypoints
5. Architectural layers
6. Core modules
7. Domain model
8. Data model
9. External integrations
10. Control-flow traces
11. Data-flow traces
12. Dependency map
13. Configuration map
14. Testing strategy
15. Deployment assumptions
16. Change-impact map
17. Known risks
18. Unknowns and unresolved questions
19. Evidence index

Empty-by-design sections explicitly state "None known" or "Not applicable" — they are never silently omitted. The *Evidence index* lists every distinct citation appearing in the document, de-duplicated.

**Symbol accounting (no silent omission).** Every function and class defined in the repository MUST be accounted for: either referenced in an analytical claim/citation, or listed under a **"Symbols not yet analyzed"** subsection of *Core modules* (grouped by file; per-file counts are acceptable on large repositories). State the counts — *N defined, M analyzed, N−M listed* — so a reader can see nothing was hidden. Exclude generated/vendored directories.

**Data-model diagram.** When the repository has a database or persistent schema, the *Data model* section MUST include a fenced ` ```mermaid ` block containing an `erDiagram` of the real tables/models — their key columns and foreign-key relationships — with each entity traceable to the schema file that defines it (migration, DDL, or ORM model). When there is no persistent schema, state "Not applicable"; never draw a fabricated schema.

**Presentation format.** A specification is read by humans, so favour scannable structure:

- Use **numbered section headings** in template order — `## 1. Repository overview` … `## 19. Evidence index`.
- Render inherently tabular sections as Markdown **tables** with an **Evidence** column (the `path:line` citation) and a **Label** column (`[fact]`/`[inference]`/`[unknown]`): *Technology stack*, *Dependency map*, *Configuration map*, the field list of *Data model*, and *Evidence index*.
- For *Control-flow traces* and *Data-flow traces*, lead with a fenced ` ```mermaid ` **`flowchart`** depicting the steps end to end, then list the authoritative numbered steps as labeled, cited claims beneath it.
- Diagrams (`flowchart`, `erDiagram`) are visual aids and carry **no citations**; every step or entity a diagram shows MUST also appear as a labeled, cited line or table row, so evidence grounding is unaffected by the diagram.

Working artifacts produced by this skill live under a `.reposkillopt/` directory at the **target repository root** (the repository being analyzed, not the project that ships this skill), with fixed subdirectories:

- `.reposkillopt/specs/` — Repository Specifications
- `.reposkillopt/feedback/` — Feedback Items
- `.reposkillopt/rollouts/` — Rollout Logs
- `.reposkillopt/proposals/` — Skill Edit Proposals

## Human Feedback Loop

The Human Feedback template lives at `templates/human-feedback.md`. The Rollout Log template lives at `templates/rollout-log.md`.

When a human provides feedback against a Repository Specification:

1. **Record the feedback before applying it.** Write a Feedback Item to `.reposkillopt/feedback/FB-YYYY-MM-DD-NNN-<slug>.md` using the template. Assign one of the eleven `type` values (correction, confirmation, missing-context, terminology, quality-rating, avoid-path, deeper-analysis, criticism-of-claim, format, detail-level, cross-agent-difference). Assign a `scope`: `repository-scoped` for facts particular to this codebase; `candidate-for-generic` for patterns that might warrant a future edit to this skill.

2. **Revise the current Repository Specification.** Apply the feedback. For changed `**[fact]**` claims, update the citation. For superseded claims, mark them superseded in place; do not silently rewrite history. Increment the spec's `revision`, update `revised`, and append a row to the spec's *Change log* appendix naming the Feedback Item ids applied.

3. **Update the session's Rollout Log.** List the Feedback Item ids under *Human feedback received this session*, each annotated `(applied)`, `(deferred)`, or `(withdrawn)`. List the revised spec sections under *Revisions applied*.

4. **Do not silently promote repository-specific facts into this canonical skill.** Feedback marked `scope: repository-scoped` stays in the target repository's artifacts only. Promotion to canonical content requires an accepted Skill Edit Proposal, generated through the Skill Convergence Loop below.

Human feedback is used in two ways simultaneously: immediate improvement of the current Repository Specification, and longer-term input to skill convergence.

## Skill Convergence Loop

The Skill Edit Proposal template lives at `templates/skill-edit-proposal.md`.

When recurrent feedback (typically three or more related Feedback Items across one or more sessions) suggests a weakness in this skill itself:

1. **Summarize the pattern.** Identify the recurring shape across the supporting Feedback Items. Confirm that the pattern is generalizable (would help on other repositories or tasks) — not a one-off detail of the current codebase.

2. **Propose one or more bounded edits.** Each proposal is a single accept/reject unit, small enough that a reviewer can decide in five minutes or less (`review_time_estimate_minutes ≤ 5`). If a proposal does not fit, split it.

3. **Categorize each proposal.** Use one of six `edit_kind` values:
   - `ADD` — add new content
   - `REPLACE` — substitute existing content
   - `DELETE` — remove content
   - `REORDER` — change order of existing content
   - `SPECIALIZE` — narrow an existing rule (more specific case)
   - `GENERALIZE` — broaden an existing rule (cover more cases)

4. **Mark the scope.** `scope: generic` is the only kind eligible for canonical acceptance. `scope: repository-scoped` proposals MUST be rewritten to generalize, or rejected, or routed to a per-repository scope-decision artifact.

5. **Preserve rejected proposals.** Set `status: rejected` and populate `decision_rationale`. Do not delete — the rejected proposals are part of the audit trail.

6. **Gate before accepting.** A `scope: generic` proposal may move to `status: accepted` only after it passes a validation gate: applied to a candidate skill version, it must regenerate specifications for a held-out reference set (disjoint from the repositories whose feedback motivated it) whose per-dimension rubric scores do not regress and whose deterministic checks still pass, with the proposal's expected effect realized on at least one dimension (or explicitly waived). The run is recorded as a Validation Gate Report referenced by the proposal. The gate authorizes — it does not replace — the acceptance flow below.

7. **Apply accepted proposals to the canonical skill.** When `status: accepted` (with a passing gate referenced), the proposal's diff is applied to this `SKILL.md`. The canonical version is bumped per Keep-A-Changelog + semver: major if the diff breaks the adapter-equivalence checklist, minor if additive, patch if clarifying. A row is added to `skills/repo-skillopt/CHANGELOG.md`.

8. **Prefer edits that generalize.** When a proposed change would specialize the generic skill to a single repository, flag it or rewrite it. Generalizable improvements outweigh repository-specific ones for this artifact.

## Output Discipline

Every major claim in a Repository Specification (or in any rollout-produced text) carries exactly one of four label prefixes, before the claim:

- `**[fact]**` — verified by inspection. **MUST** be immediately followed by at least one citation in one of these forms:
  - `path/to/file.ext:line`
  - `path/to/file.ext:start-end`
  - `path/to/file.ext:Symbol`
  - `path/to/file.ext:Symbol:line`
  - `cmd: <command>` followed by `output: <verbatim output>`
- `**[inference]**` — derived from partial signal. State the basis (e.g., "basis: presence of `flask_login` import in `src/auth.py:7`").
- `**[unknown]**` — explicitly not determined. Also appears (or is referenced) under *Unknowns and unresolved questions*.
- `**[human]**` — provided by a human via the feedback loop. Cites the originating Feedback Item id (form: `FB-YYYY-MM-DD-NNN`).

A hypothesis presented as a fact is a defect. A fact without a citation is a defect. An unverifiable claim that is neither labeled `**[inference]**` nor `**[unknown]**` is a defect. The output is meant to be useful to a real engineer — that means trustworthy, not pretty.

Trivial recitations (literal file contents, raw config dumps, syntactic restatements) are not major claims and do not require labels.

---

## Notes for this adapter (non-normative)

These notes do not modify any rule above; they only describe per-environment specifics.

- **Install**: drop `skill.md` somewhere your harness loads instruction files from (e.g., a `skills/`, `prompts/`, or `instructions/` directory). Activation happens via your harness's loading mechanism; if your harness uses a system message, paste the contents of `system-prompt-fragment.md` into the system message so the skill is referenced.
- **Metadata**: YAML front matter carries `canonical_version`. Verify it matches the canonical `version:` in `skills/repo-skillopt/SKILL.md` of the RepoSkillOpt project.
- **Known cross-agent differences**: harnesses vary in how aggressively they apply the trigger conditions. If the skill fails to activate on a prompt that should match FR-004 triggers, prepend the trigger condition explicitly to the prompt.
