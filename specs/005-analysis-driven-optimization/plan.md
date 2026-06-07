# Implementation Plan: Real-Analysis-Driven Per-Repo Skill Optimization

**Branch**: `005-analysis-driven-optimization` | **Date**: 2026-06-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-analysis-driven-optimization/spec.md`

## Summary

Change the per-repo optimizer's fitness from a thin proxy (8 KB digest → one-shot spec → LLM rubric) to a signal grounded in the real repository: build a **cached evidence pack** once per run, generate each candidate's spec from it, and score with a **combined reward** = `0.5 × rubric + 0.5 × deterministic-pass-rate`, where the deterministic checks resolve the spec's citations against the actual files. Concrete grounding failures are fed into SkillOpt's reflect so edits target real gaps. A run emits the specialized SKILL.md and the best spec. SkillOpt still owns reflect/apply/gate.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine), POSIX shell (existing scripts). No new language.
**Primary Dependencies**: existing — `skillopt` (reflect/apply/gate), the in-repo rubric, the providers (`claude-cli` keyless / API-key). New work uses only the standard library (`re`, `pathlib`, `subprocess`/`grep`) — **no heavyweight deps** (FR-014).
**Storage**: filesystem only. Evidence pack held in memory per run; outputs written under the target repo's `.reposkillopt/`.
**Testing**: `python -m unittest` (existing `engine/tests/`), pyflakes. New deterministic unit tests for grounding + reward; a live end-to-end check on `eco-standard-wiki`.
**Target Platform**: local CLI (`reposkillopt-engine optimize-repo`).
**Project Type**: single (the `engine/` Python package).
**Performance Goals**: evidence pack built **once per run** (FR-002/SC-002); per-candidate cost = one generate + one score (LLM) + cheap deterministic checks (no LLM, FR-006/SC-006).
**Constraints**: canonical SKILL.md untouched (FR-011); deterministic component reproducible without a model (SC-006); evidence pack bounded ~60 KB, omissions recorded (FR-003).
**Scale/Scope**: single-repo runs; validation target is a ~10k-file repo (eco-standard-wiki).

## Constitution Check

The project constitution (`.specify/memory/constitution.md`) is an unfilled template — no ratified principles to gate against. The project's own non-negotiables (from `CLAUDE.md`) that apply here:

- **Canonical neutrality** — unaffected: this feature writes a *separate* per-repo skill artifact and never edits `skills/repo-skillopt/SKILL.md` (FR-011). ✅
- **Skill-first / helpers optional** — the engine is already the opt-in executable layer; this stays inside it. ✅
- **No new heavyweight dependency** — satisfied (stdlib + grep only). ✅

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/005-analysis-driven-optimization/
├── spec.md
├── plan.md                # this file
├── research.md            # Phase 0 decisions
├── data-model.md          # entities: EvidencePack, GroundingResult, Reward, RunOutputs
├── contracts/
│   └── engine-contracts.md  # function-level contracts for the new/changed engine surface
├── quickstart.md          # how to run + validate
└── checklists/requirements.md
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── evidence.py            # NEW: build_evidence_pack(repo) -> EvidencePack (cached, bounded)
├── grounding.py           # NEW: parse + resolve citations against the repo; deterministic checks + failures
├── skillopt_native.py     # CHANGED: RepoTask carries pack; _score_skill uses grounding + combined reward;
│                          #          reflect fail_reason from failures; NativeResult carries best_spec
├── rubric.py              # unchanged (reuse DIMENSIONS/CHECKS/aggregate)
├── judge.py               # unchanged (generate_spec/score_spec reused)
└── cli.py                 # CHANGED: build_evidence_pack wiring; write both outputs

engine/tests/
├── test_evidence.py       # NEW
├── test_grounding.py      # NEW: resolve real vs fabricated citations; failure messages
└── test_skillopt_native.py# CHANGED: combined-reward + grounded-beats-hallucinated
```

**Structure Decision**: single Python package (`engine/`); two new modules keep the change cohesive and unit-testable in isolation, with `skillopt_native.py`/`cli.py` as the integration seam.

## Complexity Tracking

None — no constitution deviations; no new dependencies; change is additive within the existing package.
