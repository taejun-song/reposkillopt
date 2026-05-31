# Contract — Adapter Equivalence (FR-024, FR-025)

**Scope**: The relationship between any adapter (`adapters/<target>/...`) and the canonical skill (`skills/repo-skillopt/SKILL.md`).
**Consumers**: Adapter authors; reviewers; the optional future automated check.

## Required metadata on every adapter

- A `canonical_version` value (in YAML front matter or in an HTML-comment metadata block) that exactly matches an existing `version:` in canonical `SKILL.md` (FR-027a).
- An `adapter` value identifying the target (`claude-code`, `codex`, `opencode`, `generic`).

## Equivalence checklist

Run against the adapter file with the canonical `SKILL.md` open side-by-side. The adapter passes if every item is true:

| # | Check | Source |
|---|---|---|
| 1 | `canonical_version` resolves to an existing canonical `version` | FR-027a |
| 2 | All nine canonical required sections are present, in order | Canonical-Skill contract, sections 2–9 |
| 3 | *Purpose* communicates the same goal | FR-001, FR-003 |
| 4 | *Trigger Conditions* enumerates the FR-004 verbs and excludes activation outside them | FR-004 |
| 5 | *Operating Principles* preserves every rule from FR-007, FR-008, FR-009, FR-010, FR-011 — wording may differ, rule strength may not weaken | FR-024 |
| 6 | *Repository Understanding Workflow* lists FR-012 stages (a)–(g) in order | FR-012 |
| 7 | *Repository Specification Format* lists the 19 FR-005 sections (verbatim or as a recognizable list) | FR-005 |
| 8 | *Human Feedback Loop* preserves FR-013 (template fields), FR-014 (record-before-apply), FR-015 (dual use), FR-016 (no silent promotion) | FR-013–FR-016 |
| 9 | *Skill Convergence Loop* preserves FR-018, names the six edit kinds, preserves FR-020 boundedness, FR-021 preservation of rejected proposals, FR-022 generalize-over-specialize preference | FR-018–FR-022 |
| 10 | *Output Discipline* requires the R10 label notation and citations for `**[fact]**` claims | FR-008, FR-009 |
| 11 | No required canonical instruction is dropped, weakened, or contradicted | FR-024, FR-025 |
| 12 | Adapter additions (per-environment notes) are clearly marked as such and do not modify canonical normative content | FR-027 |
| 13 | Adapter does not introduce dependency on any other vendor runtime | FR-002 |
| 14 | Adapter uses the on-disk layout from FR-036a in any examples it gives — `.reposkillopt/{specs,feedback,rollouts,proposals}/` | FR-036a |

## Reviewer procedure (manual; documented per Phase 0 R6)

1. Open canonical `SKILL.md` and the adapter side-by-side.
2. Verify metadata (checks 1–2).
3. Walk the canonical sections in order; for each, locate the corresponding adapter section and confirm checks 3–10.
4. Scan the adapter for any normative content not derived from the canonical skill; if found, confirm it is in a clearly marked per-adapter notes section (check 12).
5. Grep the adapter for the names of other vendors (check 13); permitted only in illustrative non-normative content.

## Failure modes (recorded for the rubric)

- **Dropped section** — the adapter is missing a required canonical section. Fail.
- **Weakened rule** — an Operating Principle is rephrased to be optional or conditional. Fail.
- **Stale `canonical_version`** — the value does not resolve to a current canonical version. Fail (stale wrapper).
- **Cross-vendor leakage** — adapter mentions another vendor in a normative section. Fail.
- **Layout drift** — adapter examples use a path other than `.reposkillopt/`. Fail.
