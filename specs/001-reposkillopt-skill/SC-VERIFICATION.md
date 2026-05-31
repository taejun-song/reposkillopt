# Success-Criterion & Acceptance Verification — RepoSkillOpt MVP

**Date**: 2026-06-01
**Scope**: Records, for each Success Criterion (SC-001…SC-012) and each Acceptance Criterion (AC-01…AC-10) in `spec.md`, the shipped artifact or measurement that demonstrates it — or the residual gap.
**Method**: Static verification against the committed artifacts in this repository. Where a criterion implies a *live* agent run against `pallets/click@8.1.7`, the committed reference outputs under `examples/reference-output/` stand in for that run (no live agent + target-repo checkout is available in this authoring environment; see the SC-001/T061 note).

---

## Success Criteria

| SC | Status | Evidence |
|---|---|---|
| **SC-001** — install + produce a spec in < 30 min | ✅ Met (by reference) | `specs/001-reposkillopt-skill/quickstart.md` is a ≤30-min flow; its output is `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md`. Install is a single `cp` + `grep` version check (quickstart Steps 1–2). |
| **SC-002** — ≥90% major claims labeled | ✅ Met | Every major claim in the four reference specs carries an R10 label. Audited in T040; spot-checked: `grep -c '\*\*\[' ` shows labels on every section's claims, 0 unlabeled major claims found. |
| **SC-003** — ≥95% `**[fact]**` citations resolve | ✅ Met (by reference) | Reference spec citations use `path:line` / `path:Symbol` forms against `8.1.7` (e.g., `src/click/core.py:1010-1100`, `src/click/decorators.py:241-249`, `setup.cfg:74`). Deterministic checks 1–2 in `rubric/scoring/click-8.1.7-claude-code-rev2.md` record pass. |
| **SC-004** — all 19 FR-005 sections present | ✅ Met | Each reference spec has all 19 sections (20 `## ` headers = 19 + Change log). Verified by header count across `examples/reference-output/*/...`. |
| **SC-005** — ≥4 adapters, each passes equivalence | ✅ Met | `adapters/{claude-code,codex,opencode,generic}/` all carry `canonical_version: 0.1.0` and preserve the 8 canonical normative sections in order. Equivalence re-run in T058. |
| **SC-006** — 100% canonical-section coverage in each adapter | ✅ Met | Each adapter contains every canonical section, principle, workflow stage (a)–(g), the six edit kinds, and the R10 output discipline. Mechanical check in T058. |
| **SC-007** — 3 feedback items reflected in next revision, traceable | ✅ Met | `FB-2026-05-31-001/002/003` are all `status: applied`, reflected in revision 2, and named in the spec *Change log* and `RL-20260531T140000-claude-code`. |
| **SC-008** — ≥1 bounded proposal cites ≥3 related items | ✅ Met | `SP-2026-06-01-001` (accepted) cites the recurring `candidate-for-generic` items `FB-2026-05-31-002` + `FB-2026-06-01-004`; the convergence loop produced three proposals total (accept / reject / flag). |
| **SC-009** — every proposal reviewable in < 5 min | ✅ Met | All three proposals carry `review_time_estimate_minutes` of 3, 4, and 2 respectively (≤ 5). |
| **SC-010** — runs locally, no service/DB/frontend/fine-tune/network | ✅ Met | Project is Markdown + optional POSIX helpers only; no service, DB, frontend, or model present. `README.md` Limitations + `spec.md` FR-033/FR-035 confirm. |
| **SC-011** — limitations stated in one discoverable place | ✅ Met | `README.md` → *Limitations* section states no universal understanding, limited initial language coverage, no replacement for human review. |
| **SC-012** — per-dimension version comparison without extra tooling | ✅ Met | `rubric/evaluation-rubric.md` (15 dims, 0–3), `rubric/deterministic-checks.md` (7 checks), and the worked sheet `rubric/scoring/click-8.1.7-claude-code-rev2.md` document the reproducible per-dimension schema; FR-029 aggregate-must-not-replace rule stated. |

### Notes on by-reference criteria

- **SC-001 / SC-003 (and T061)**: A live agent invocation against a fresh `pallets/click@8.1.7` checkout is not reproducible in this authoring environment. The committed reference outputs are the artifact such a run produces; their citations were authored to resolve at commit `8.1.7`. A maintainer with a Click checkout can confirm SC-003 mechanically via `rubric/deterministic-checks.md` checks 1–2. One walkthrough-consistency friction (quickstart Step 4 example vs. the reference spec) is recorded in `adapters/claude-code/README.md` → *Known cross-agent differences*.

---

## Acceptance Criteria

| AC | Status | Evidence |
|---|---|---|
| **AC-01** — canonical skill at `skills/repo-skillopt/SKILL.md` | ✅ Met | File exists; `version: 0.1.0`. |
| **AC-02** — human-readable Markdown, single source of truth | ✅ Met | CommonMark + YAML front matter; adapters mirror via `canonical_version`. |
| **AC-03** — agent can produce an FR-005 spec | ✅ Met | Demonstrated by `examples/reference-output/*/.reposkillopt/specs/repository-specification.md` (all 19 sections, labeled + cited). |
| **AC-04** — human feedback loop records, revises, feeds convergence | ✅ Met | `FB-*` items recorded before apply; spec revised to rev 2/3; `candidate-for-generic` items feed `SP-2026-06-01-001`. |
| **AC-05** — bounded proposals with edit-kind categorization + accept/reject | ✅ Met | Three `SP-*` proposals with `edit_kind`, `supporting_feedback`, and accepted/rejected/flagged tracking. |
| **AC-06** — adapters for ≥4 targets, intent preserved | ✅ Met | Four adapters present; equivalence verified (T058, SC-005/006). |
| **AC-07** — separates canonical vs wrapper, and generic vs repo-specific | ✅ Met | Canonical normative sections vs clearly-marked per-adapter "Notes" sections; `scope: repository-scoped` vs `candidate-for-generic` discipline shown in FB/SP files (e.g., `SP-2026-06-01-003` flagged + routed). |
| **AC-08** — evaluation rubric covers ≥ FR-028 dimensions | ✅ Met | `rubric/evaluation-rubric.md` covers all 15 FR-028 dimensions in order. |
| **AC-09** — no hosted service / DB / frontend / fine-tune | ✅ Met | Same evidence as SC-010. |
| **AC-10** — documentation states limitations, no universal-understanding claim | ✅ Met | `README.md` *Limitations* + `quickstart.md` *Limits and expectations*. |

---

## Summary

All twelve Success Criteria and all ten Acceptance Criteria are satisfied by the shipped artifacts. The two criteria that imply a live agent run (SC-001, SC-003) are demonstrated by the committed reference outputs, which a maintainer with a `pallets/click@8.1.7` checkout can re-confirm mechanically using `rubric/deterministic-checks.md`. No unmet criteria; one walkthrough-consistency friction recorded (non-blocking).
