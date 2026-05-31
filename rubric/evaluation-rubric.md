# RepoSkillOpt Evaluation Rubric

**Scope**: Qualitative rubric reviewers use to score a Repository Specification produced by the skill, and to compare skill versions (FR-028, FR-029; supports SC-012).
**Companion**: `rubric/deterministic-checks.md` (the seven binary checks) and the scoring-sheet schema documented there.

## How to score

Each of the fifteen dimensions below is scored independently on a **0–3** scale:

- **0 = absent** — the dimension is not addressed at all.
- **1 = poor** — addressed but unreliable, thin, or partly wrong.
- **2 = adequate** — addressed correctly and usefully, with minor gaps.
- **3 = strong** — addressed thoroughly, reliably, and with concrete observable signals.

> **Per-dimension scores are the unit of comparison.** An aggregate (sum or mean) MAY be reported for convenience, but it **MUST NOT** replace the per-dimension scores when comparing skill versions (FR-029). A version that trades evidence quality for completeness can hold a constant aggregate while regressing on the dimension that matters — only the per-dimension vector reveals that.

## Dimensions (FR-028 order)

### 1. Architectural correctness

*Does the spec describe the real architecture — layers, modules, and their relationships — as they exist in the code?*

- **0**: No architecture described, or it contradicts the code.
- **1**: Layers/modules named but with errors or unverified structure.
- **2**: Architecture is correct with minor omissions; layers match the source tree.
- **3**: Architecture is correct and complete, each layer/module attributed to files and symbols, dependency direction stated.

### 2. Evidence quality

*Are claims backed by concrete repository evidence (paths, symbols, configs, command outputs) rather than generic description?*

- **0**: Claims are generic prose with no evidence.
- **1**: A few claims cite evidence; most are unsupported assertion.
- **2**: Most major claims cite concrete evidence; a few rest on generic description.
- **3**: Every major claim is grounded in specific, relevant, inspected evidence.

### 3. Citation validity

*Do the citations point at the right artifact and form (`path:line`, `path:Symbol`, `cmd:`/`output:`)?*

- **0**: Citations absent or malformed.
- **1**: Citations present but frequently point at the wrong location or use an invalid form.
- **2**: Citations are well-formed and mostly accurate; isolated drift.
- **3**: Citations are well-formed and resolve to exactly the cited content.

### 4. File and symbol grounding

*Do cited files and symbols actually exist in the repository at the recorded commit?*

- **0**: Multiple cited files/symbols do not exist.
- **1**: Most exist, but several hallucinated paths or symbols slip through.
- **2**: All cited files exist; a small number of symbols are imprecise (e.g., wrong line).
- **3**: Every cited file and symbol resolves at the recorded commit.

### 5. Hallucination avoidance

*Does the spec avoid asserting files, modules, APIs, or behaviors that do not exist?*

- **0**: Contains fabricated files/APIs/behaviors presented as real.
- **1**: One or more unverifiable claims presented without hedging.
- **2**: No fabrications; occasional overconfident phrasing on thin evidence.
- **3**: Zero fabrications; every uncertain claim is hedged or labeled.

### 6. Change-localization accuracy

*Does the Change-impact map correctly identify what a given change would and would not affect?*

- **0**: No change-impact analysis, or it is wrong.
- **1**: Impact stated but not traceable to the dependency structure.
- **2**: Impact mostly correct and tied to dependencies; some blast-radius gaps.
- **3**: Impact is accurate, derived from the dependency map, and distinguishes affected from unaffected paths.

### 7. Usefulness to an engineer

*Would a maintenance engineer act on this spec with confidence and save time?*

- **0**: Not actionable; an engineer would have to start over.
- **1**: Some orientation value but missing what's needed to act.
- **2**: Useful for onboarding and most maintenance tasks.
- **3**: Directly actionable — entrypoints, traces, risks, and next steps a real engineer can use immediately.

### 8. Risk awareness

*Are the repository-specific risks (not generic platitudes) identified and tied to evidence?*

- **0**: No risks, or only generic boilerplate.
- **1**: Risks listed but generic or unsupported.
- **2**: Repository-specific risks identified; most tied to evidence.
- **3**: Repository-specific risks, each tied to concrete evidence, with the conditions that trigger them.

### 9. Distinction between verified facts and hypotheses

*Does every major claim carry exactly one of `**[fact]**` / `**[inference]**` / `**[unknown]**` / `**[human]**`, with facts cited?*

- **0**: No labels; facts and guesses are indistinguishable.
- **1**: Labels used inconsistently; some hypotheses presented as facts.
- **2**: Labels applied to nearly all major claims; rare slips.
- **3**: Every major claim labeled; every `**[fact]**` cited; no hypothesis masquerades as fact.

### 10. Test strategy quality

*Does the spec correctly describe how the repository is tested, including non-obvious test surfaces?*

- **0**: Testing not described.
- **1**: Test framework named but layout/coverage wrong or shallow.
- **2**: Framework, layout, and fixtures correct; obvious surfaces covered.
- **3**: Correct framework/layout/fixtures plus secondary surfaces (typing, integration, property, matrix) enumerated with evidence.

### 11. Responsiveness to human feedback

*Are recorded Feedback Items applied to the spec, with traceable ids and correct scope handling?*

- **0**: Feedback ignored or not recorded.
- **1**: Feedback recorded but not reflected in the spec.
- **2**: Feedback applied and traceable; scope mostly respected.
- **3**: Every applicable item applied, traceable by id in the Change log, with `repository-scoped` vs `candidate-for-generic` handled correctly.

### 12. Repository specification completeness

*Are all 19 required sections present, with empty-by-design sections explicitly marked?*

- **0**: Many required sections missing.
- **1**: Several sections missing or silently omitted.
- **2**: All 19 sections present; one or two thin.
- **3**: All 19 sections present and substantive; empty-by-design sections explicitly state "None known"/"Not applicable".

### 13. Repository specification maintainability

*Is the spec structured so the next session can revise it incrementally (stable sections, Change log, de-duplicated Evidence index)?*

- **0**: Unstructured; would have to be regenerated to revise.
- **1**: Structured but no revision affordances (no Change log / revision metadata).
- **2**: Revisable with a Change log and revision metadata; minor friction.
- **3**: Cleanly revisable — stable section order, accumulating Change log, de-duplicated Evidence index, preserved prior `**[human]**` claims.

### 14. Cross-agent portability

*Would the same skill, exported through a different adapter, produce an equivalent spec?*

- **0**: Output depends on a specific runtime's behavior.
- **1**: Largely portable but leaks runtime-specific assumptions.
- **2**: Portable; adapter passes the Adapter Equivalence contract with minor notes.
- **3**: Fully portable — content is runtime-neutral and the producing adapter passes every Adapter Equivalence row.

### 15. Resistance to agent-specific failure modes

*Does the spec avoid known agent pitfalls (README-only trust, pattern-matching from training data, overclaiming from shallow inspection)?*

- **0**: Exhibits these failure modes plainly.
- **1**: Avoids some, exhibits others (e.g., trusts README, or overclaims).
- **2**: Avoids the major pitfalls; isolated pattern-matched claim.
- **3**: Demonstrably corroborates beyond README, inspects this repository over pattern-matching, and refuses to overclaim from shallow reads.
