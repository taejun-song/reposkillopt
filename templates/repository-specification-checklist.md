# Specification Quality Checklist: <target_repository>

**Purpose**: Validate a Repository Specification's grounding, completeness, and readiness before it is shared or used to drive work — the RepoSkillOpt analogue of speckit's `checklists/requirements.md`.
**Created**: <YYYY-MM-DD>
**Specification**: [repository-specification.md](repository-specification.md)

**Note**: Tick each item only when the spec demonstrably satisfies it. Grounding and completeness
items (CHK006–CHK013) are also measured deterministically by the engine's metrics — this checklist
is the human-facing gate over the same guarantees.

## Evidence & Grounding

- [ ] CHK001 Every major claim carries exactly one label — `**[fact]**`, `**[inference]**`, `**[unknown]**`, or `**[human]**`.
- [ ] CHK002 Every `**[fact]**` is followed by at least one citation; no uncited facts remain.
- [ ] CHK003 Citations use a valid form (`file:line`, `file:start-end`, `file:Symbol[:line]`, or `cmd:`/`output:`) and resolve to real paths/lines in the repository.
- [ ] CHK004 `**[inference]**` claims state their basis; no architecture is asserted from shallow inspection.
- [ ] CHK005 No `[NEEDS CLARIFICATION]` / TODO / placeholder markers remain.

## Completeness

- [ ] CHK006 All 19 sections are present, in order; empty-by-design sections say "None known" / "Not applicable" (never deleted).
- [ ] CHK007 Every function and class is accounted for — referenced in the analysis or listed under *Symbols not yet analyzed*, with the counts line (*N defined, M analyzed, N−M listed*); symbol coverage is 100%.
- [ ] CHK008 The *Evidence index* lists every distinct citation in the document, de-duplicated.
- [ ] CHK009 Inherently tabular sections (*Technology stack*, *Dependency map*, *Configuration map*, *Data model* fields, *Evidence index*) use tables with an Evidence + Label column.

## Diagrams

- [ ] CHK010 *Data model* includes a Mermaid `erDiagram` of the real tables (key columns + foreign keys), each entity traceable to its schema file — or states "Not applicable" when there is no persistent schema (never a fabricated one).
- [ ] CHK011 Every entity shown in the `erDiagram` corresponds to a real table (diagram grounding); no invented entities.
- [ ] CHK012 *Control-flow traces* and *Data-flow traces* each lead with a Mermaid `flowchart`; every step the diagram shows also appears as a labeled, cited line.

## Readiness

- [ ] CHK013 *Known risks* are repository-specific (not generic platitudes) and each is tied to evidence.
- [ ] CHK014 *Unknowns and unresolved questions* lists every `**[unknown]**` plus open questions, with concrete next steps to resolve key ones.
- [ ] CHK015 Front matter is complete (`spec_id`, `target_repository`, `target_repository_commit`, `skill_version`, `adapter`, `status`) and the *Change log* records this revision.

## Notes

- Items left unticked block sharing the spec as "ready"; record why under each.
- CHK002/003/006/007/008/011 map onto the deterministic metrics (citation grounding, section
  completeness, symbol coverage, diagram grounding) — a green checklist should coincide with the
  engine reporting 100% on those axes.
