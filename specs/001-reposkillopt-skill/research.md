# Phase 0 Research — RepoSkillOpt MVP

**Feature**: 001-reposkillopt-skill
**Date**: 2026-05-31
**Status**: Complete — no `NEEDS CLARIFICATION` remains.

Each section below resolves one of the ten Phase 0 research tasks in `plan.md`. Every entry follows **Decision / Rationale / Alternatives considered**.

---

## R1 — Reference repository for adapter examples (FR-031)

**Decision**: `pallets/click` at tag `8.1.7` (https://github.com/pallets/click, BSD-3-Clause). Python 3, ~10k LOC, mature multi-module library with documented entrypoints, tests, plugin surface, and a real (not toy) architecture. Used as the **single shared reference repository** by all four adapter examples in `examples/reference-output/`.

**Rationale**:
- License is permissive (BSD-3-Clause); sample outputs may be redistributed without friction.
- Small enough that the canonical workflow can complete in one agent session within SC-001's 30-minute target.
- Large enough that evidence-grounded discovery is meaningful (multiple modules, decorators, parameter parsing, terminal rendering, testing utilities).
- Pinned to a specific tag so sample outputs remain reproducible.
- Python is a mainstream language; the skill is language-agnostic by design but a Python sample minimizes incidental friction for first-time readers.

**Alternatives considered**:
- `tj/commander.js` (JS) — similar size, similar architecture, but Click has cleaner module boundaries that better exercise the architectural-layer section.
- `psf/requests` — too large; would not finish in one session.
- A synthetic toy repo — rejected at clarification (Q3) on the grounds that toy repos do not convincingly demonstrate "legacy" understanding.
- `pgcli/pgcli` — interesting but couples a TUI, a parser, and a database client; topology is too tangled for an MVP demonstration.

---

## R2 — Claude Code skill packaging conventions

**Decision**: Adapter file lives at `adapters/claude-code/SKILL.md`. YAML front matter at minimum carries `name`, `description`, plus the RepoSkillOpt-required `canonical_version` (FR-027a) and `model` if applicable. Activation is description-based (Claude Code routes by `description`); the description text incorporates the trigger conditions from canonical FR-004 ("understand, map, document, onboard to, refactor, modify, or assess a repository").

```yaml
---
name: repo-skillopt
description: Evidence-grounded legacy-repository understanding with recurrent human feedback. Activates when the user asks to understand, map, document, onboard to, refactor, modify, or assess a repository.
canonical_version: 0.1.0
---
```

**Rationale**: Claude Code skills are routed by description text and packaged as `<name>/SKILL.md` under `.claude/skills/` of the target environment. YAML front matter is the standard place for metadata, and `canonical_version` coexists with Claude's keys without conflict.

**Alternatives considered**: a CLAUDE.md project-instruction export (FR-026) — out of MVP scope; can be added later as a second Claude Code adapter target without disturbing the skill format.

---

## R3 — Codex AGENTS.md conventions

**Decision**: Adapter file lives at `adapters/codex/AGENTS.md`. AGENTS.md is a plain-Markdown convention without a standardized YAML front-matter slot, so the `canonical_version` metadata required by FR-027a is carried in an **HTML-comment metadata block** placed as the very first lines of the file (before the H1):

```markdown
<!-- repo-skillopt-meta
canonical_version: 0.1.0
adapter: codex
-->

# RepoSkillOpt — Repository Understanding Agent Instructions
...
```

**Rationale**: HTML comments are ignored by Markdown renderers and by Codex's prose parsing, but remain machine-greppable by simple scripts (and by the adapter-equivalence check). This satisfies FR-027a's "or, where the target environment forbids YAML front matter, in an explicitly labeled metadata block" fallback without inventing a Codex-specific convention.

**Alternatives considered**:
- YAML front matter unconditionally — rejected because AGENTS.md tooling in the wild does not uniformly tolerate front matter.
- A sibling `AGENTS.meta.yaml` file — rejected because it splits the source of truth across two files.

---

## R4 — OpenCode adapter format

**Decision**: Adapter file lives at `adapters/opencode/AGENTS.md`. OpenCode consumes the same `AGENTS.md` convention as Codex (a shared community convention). The HTML-comment metadata block from R3 is reused verbatim, with `adapter: opencode`. A future OpenCode "rules" variant can be added as a sibling without breaking the main adapter.

**Rationale**: Reusing the AGENTS.md format minimizes per-adapter divergence and makes the adapter-equivalence check (FR-025) easier — the Codex and OpenCode adapters can be diffed against each other to confirm only metadata differs.

**Alternatives considered**: OpenCode-specific rules format — rejected as primary because the rules layer is meant for narrower per-rule guidance, not full skill packaging.

---

## R5 — Generic adapter shape

**Decision**: A **single Markdown skill file** at `adapters/generic/skill.md`, plus a short **system-prompt fragment** at `adapters/generic/system-prompt-fragment.md`. The skill file is the full canonical content; the system-prompt fragment is a ~10-line snippet that a custom harness can paste into its system message to ensure the skill is loaded and activated.

```text
adapters/generic/
├── README.md                       # How to install in a custom harness
├── skill.md                        # Full Markdown adapter (with metadata block)
└── system-prompt-fragment.md       # 10-line activation fragment
```

**Rationale**: Custom harnesses vary in how they load instructions. Some accept a single Markdown file; others want a system-message addition. Shipping both satisfies the broadest set of consumers without overengineering. The fragment references the skill file by relative path, keeping the skill itself as the source.

**Alternatives considered**: only the skill file (rejected — leaves harness authors to figure out activation); only the prompt fragment (rejected — loses the workflow detail).

---

## R6 — Optional helper scripts (OQ-3)

**Decision**: **Documentation only for v1 MVP.** No helper scripts ship with the MVP. The deterministic checks (FR-030) are documented as procedures in `rubric/deterministic-checks.md` that a reviewer (or a future script) can apply mechanically. The Markdown notations chosen in R10 are explicitly grep-able, so any team that wants automation can add it later without changing the artifacts.

**Rationale**: The spec is explicit (Assumptions, FR-033) that the MVP is skill-first and helper scripts are optional and outside acceptance. Shipping no scripts in v1 keeps the package portable across operating systems and avoids creating a maintenance surface that the MVP does not need.

**Alternatives considered**: shipping minimal `sh` checks (e.g., citation-path resolution) — deferred to post-MVP because it would tie the package to a POSIX environment for what is otherwise a pure-Markdown product.

---

## R7 — Cross-agent behavior notes location (OQ-5)

**Decision**: **Per-adapter** for v1. Each adapter directory's `README.md` contains a "Known cross-agent differences" section noting any behavior that diverges from the canonical intent on that specific harness (e.g., "Codex sometimes truncates citations exceeding 80 chars — wrap or split"). A shared `adapters/NOTES.md` is not introduced in v1.

**Rationale**: Differences observed in the wild are inherently per-adapter; co-locating them with the adapter they describe makes them discoverable by anyone reading that adapter. A shared notes file becomes useful only once cross-cutting patterns appear, which is unlikely in v1.

**Alternatives considered**: single `adapters/NOTES.md` — rejected for v1 (low value, risk of becoming a dumping ground); per-adapter `KNOWN_ISSUES.md` files — rejected as additional surface for the same content.

---

## R8 — Canonical skill changelog format

**Decision**: A single `skills/repo-skillopt/CHANGELOG.md` adjacent to `SKILL.md`, following the [Keep a Changelog](https://keepachangelog.com/) conventions (sections: Added / Changed / Deprecated / Removed / Fixed / Security). Versions are semver (FR-027a). Each entry's headline is the version + ISO date. The MVP releases as `0.1.0` (pre-1.0 because the canonical content is expected to evolve through the convergence loop before any "stable" claim).

**Rationale**: Keep a Changelog is well-known, human-readable, and machine-parseable. Co-locating with SKILL.md makes the change history visible to anyone reading the source of truth.

**Alternatives considered**: per-version directories (rejected — overkill for a Markdown artifact); GitHub Releases only (rejected — couples the artifact to a hosting provider, violating vendor neutrality in spirit).

---

## R9 — Rubric anchor descriptions (FR-029)

**Decision**: Each of the 15 qualitative dimensions in FR-028 receives a one-line anchor at each score level (0 / 1 / 2 / 3). The full table lives in `rubric/evaluation-rubric.md`; the abbreviated anchors below are reproduced here as the source for that file.

| Dimension | 0 (absent) | 1 (poor) | 2 (adequate) | 3 (strong) |
|---|---|---|---|---|
| Architectural correctness | Wrong or absent | Mostly wrong | Mostly right; minor gaps | Right at every layer named |
| Evidence quality | No evidence | Vague evidence | Concrete but partial | Concrete and proportionate |
| Citation validity | No citations | Some broken citations | All citations resolve to paths | All paths + symbols resolve |
| File and symbol grounding | None | Files only | Files + most symbols | Files + symbols + line ranges |
| Hallucination avoidance | Multiple hallucinations | One hallucination | Zero detected; some unverifiable | Zero, with explicit "unknown" labels |
| Change-localization accuracy | Misses target areas | Identifies wrong area | Identifies right area broadly | Pinpoints exact files/symbols |
| Usefulness to an engineer | Unhelpful | Surface-level | Lets an engineer start work | Lets an engineer change code safely |
| Risk awareness | No risks listed | Generic risks only | Repo-specific risks listed | Risks ranked with mitigations |
| Fact-vs-hypothesis distinction | None | Inconsistent labeling | Mostly labeled | Every major claim labeled per FR-008 |
| Test strategy quality | Absent | Generic advice | Repo-specific suggestions | Repo-specific + actionable + cited |
| Responsiveness to human feedback | Ignored | Applied superficially | Applied and recorded | Applied, recorded, generalized when appropriate |
| Spec completeness | Many sections missing | Some sections missing | All sections present | All sections present and substantive |
| Spec maintainability | Single-shot only | Survives one revision | Survives multiple revisions | Survives multiple revisions with change log |
| Cross-agent portability | One agent only | Works on two | Works on three | Works on all four MVP adapters |
| Resistance to agent-specific failures | Brittle | One agent-specific workaround required | A few workarounds documented | None required |

**Rationale**: Single-line anchors are scoreable in seconds, keep inter-rater variance low, and fit the 0–3 scheme decided at clarification. The text deliberately uses concrete observable signals so reviewers do not need to invent their own definitions.

**Alternatives considered**: paragraph-length anchors (rejected — too slow to read); leaving anchors to teams (rejected at clarification Q4).

---

## R10 — Major-claim label notation (FR-008)

**Decision**: Inline label prefix, four allowed forms, before the claim:
- `**[fact]**` — verified fact (requires citation per FR-009)
- `**[inference]**` — inference from partial signal (basis stated)
- `**[unknown]**` — explicitly unknown; lives under the Unknowns section per FR-010
- `**[human]**` — human-provided context (cite the feedback item id)

Example:
```markdown
- **[fact]** The HTTP entrypoint is `app.cli:main` (`src/cli.py:42`, defined by `@click.group` at L41).
- **[inference]** Auth is likely session-based; basis: `flask_login` import in `src/auth.py:7` plus no JWT-related libraries in `pyproject.toml`.
- **[unknown]** Whether the deployment uses gunicorn or uWSGI in production.
- **[human]** Internal terminology: "tenant" always means a billing account, not a workspace. (Source: feedback `FB-2026-05-31-003`.)
```

**Rationale**: Bold-bracket prefixes are visible to human readers, easy to grep with `\*\*\[(fact|inference|unknown|human)\]\*\*`, and survive being copied between Markdown environments. The fixed enum maps directly to the four FR-008 categories and to the rubric's "Fact-vs-hypothesis distinction" dimension.

**Alternatives considered**:
- HTML-comment markers (`<!-- fact -->`) — invisible to readers; the discipline is meant to be visible.
- Inline emoji — rejected; CLAUDE.md guidance forbids emoji unless requested, and they break grep on terminals without color.
- A separate "categories" column in a table — heavyweight for what should be a one-token decoration.

---

## Open Questions resolved by this phase

- **OQ-3** (deterministic checks: docs vs scripts) — resolved by R6: documentation only for MVP.
- **OQ-5** (cross-agent notes location) — resolved by R7: per-adapter `README.md` section.

No `NEEDS CLARIFICATION` remain. Ready for Phase 1.
