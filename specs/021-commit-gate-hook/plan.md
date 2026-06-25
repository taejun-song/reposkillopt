# Implementation Plan: Commit-Time Gate Hook (Auto-Remediating Pre-Commit Enforcement)

**Branch**: `021-commit-gate-hook` | **Date**: 2026-06-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/021-commit-gate-hook/spec.md`

## Summary

Make the four deterministic gates and the bounded refine loop **mandatory at commit time** instead of opt-in. A portable POSIX-`sh` `pre-commit` hook — installed into target repos by the existing CLI installer — detects staged `.reposkillopt/` artifacts and calls one new engine entrypoint, `gate-commit`. That entrypoint gates each staged artifact (coverage / grounding / completeness / check-artifact), and on any failure runs a **bounded, gate-set-monotonic** remediation loop (reusing `refine`/`judge`) until every applicable gate passes, then re-stages the fixed artifact so the commit proceeds. If no keyless provider (or the engine itself) is reachable, it degrades to **block-and-report** — never hangs, never wedges. A pre-existing `pre-commit` hook is **chained**, not clobbered. Lifecycle (install/list/upgrade/uninstall, with chained-hook restore) is driven by the existing per-repo install manifest.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine entrypoint); POSIX `sh` (hook + installer, authored/tested under `bash` and `dash`).
**Primary Dependencies**: None new. Reuses `refine` (refine_loop/refine_once/spec_gaps/score_spec), `judge` (revise_spec), `grounding` (ground_spec — **frozen**), `completeness` (ensure_symbol_completeness), `quality`/`structure` (compute_structure), `artifact_checks` (the four checks), `providers` (make_provider, keyless ids), `scripts/coverage-gate.sh`, and `installer/lib/{manifest,util,targets}.sh` (manifest_upsert/remove_row/list, copy_atomic, read_field). Stdlib only otherwise (`subprocess`, `shutil`, `pathlib`, `socket`).
**Storage**: Filesystem only. The per-repo `.reposkillopt/.install-manifest` (unchanged TAB-separated line format) records the installed hook and any chained-hook backup. Artifacts gated/remediated live under the target repo's `.reposkillopt/`.
**Testing**: `unittest` for the engine entrypoint; POSIX-`sh` test scripts (run under `bash` **and** `dash`) for the hook + installer integration, matching `installer/tests/` and `scripts/tests/`.
**Target Platform**: Any POSIX shell + Python ≥ 3.10; a git work tree. Keyless providers: `claude-cli`, `opencode-cli`, `ollama`.
**Project Type**: CLI/tooling on top of the existing portable skill package + optional Python engine. No server, no daemon, no network required for the deterministic path.
**Performance Goals**: Source-only commits incur **zero** gate runs and zero model calls (fast path). The no-provider/no-engine path completes in deterministic-gate time with a tight bounded probe (no open-ended wait). Remediation is bounded by a small round budget (default 3).
**Constraints**: Keyless providers only in the hook path (never prompt for a secret mid-commit). Bounded + gate-set-monotonic remediation (no infinite loop; no gate regression). Chain (never overwrite) a pre-existing hook. Respect `core.hooksPath`. Honor `REPOSKILLOPT_HOOK=off` and git `--no-verify`. No change to any gate/metric/rubric/reward definition; `grounding` stays frozen.
**Scale/Scope**: One new engine module (`commit_gate.py`) + one CLI subcommand; one hook template + one installer lib (`hook.sh`) + installer wiring; tests; docs. Pre-commit only.

## Constitution Check

*GATE: must pass before Phase 0 and re-checked after Phase 1.*

| Principle | Assessment |
|-----------|------------|
| **I. Evidence-Grounded Output** | **Reinforces it.** The feature's whole purpose is to *enforce* grounding/coverage/completeness at commit time. Remediation reuses `judge.revise_spec` + `ensure_symbol_completeness`, which preserve R10 labels and resolvable `[fact]` citations. No artifact lands with unresolved `[fact]`s. ✅ |
| **II. Vendor Neutrality** | No canonical `SKILL.md` normative content is touched. The hook/engine are tooling; keyless provider ids live in the engine `providers/`, not in skill content. ✅ |
| **III. Adapter-Equivalence** | No skill is modified → no `canonical_version` bump and no adapter change required. ✅ (verified: feature adds engine + installer + hook only). |
| **IV. Deterministic & Reproducible, Stdlib-Only** | The **gates and all the parts under test** (gate selection, bound/termination, gate-set monotonicity, re-stage accounting, no-provider fallback, hook chaining/exit-status) are deterministic and reproducible; no new deps; POSIX `sh` + stdlib Python. The remediation *edit* is model-driven and therefore nondeterministic — this is the existing optional engine machinery and is documented plainly (FR-016). No SaaS/DB/required-network on the deterministic path. ✅ |
| **V. Bounded, Gated Self-Improvement** | Remediation is **bounded** (round budget) and **monotonic** on the passing-gate set (never regresses) — a strict reading of this principle. It fixes per-repo artifacts; it does not promote skill edits, so no version-gate is bypassed. ✅ |
| **VI. Test-First for Engine Code** | New module `commit_gate.py` and the hook/installer logic are built TDD (red→green) on their deterministic behaviors; the full `unittest` suite stays green. `grounding` is **not** modified (stays frozen). ✅ |

**Result: PASS, no violations.** Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/021-commit-gate-hook/
├── plan.md              # This file
├── research.md          # Phase 0 — decisions D1–D9
├── data-model.md        # Phase 1 — entities (GateVerdict, GateReport, RemediationRound, HookRecord, …)
├── quickstart.md        # Phase 1 — install → commit-fails-then-converges → uninstall walkthrough
├── contracts/
│   ├── gate-commit.contract.md     # the engine entrypoint (inputs, exit codes, gate selection, restage)
│   └── pre-commit-hook.contract.md # the hook + installer lifecycle (chaining, bypass, manifest)
├── checklists/requirements.md      # already written (all-pass)
└── tasks.md             # /speckit.tasks output (next phase)
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── commit_gate.py        # NEW — classify_artifact, select_gates, run_gates, remediate, gate_commit
└── cli.py                # EDIT — add `gate-commit` subcommand + detect_keyless_provider() helper

engine/tests/
└── test_commit_gate.py   # NEW (TDD) — gate selection, bound/termination, gate-set monotonicity,
                          #              re-stage accounting, no-provider fallback (deterministic core)

installer/
├── hooks/pre-commit      # NEW — portable POSIX-sh hook template (detect → bypass → invoke → chain)
├── lib/hook.sh           # NEW — install/list/uninstall the hook: chaining, core.hooksPath, manifest row
├── reposkillopt-install  # EDIT — wire `--hook` install/list/uninstall through hook.sh + manifest
└── tests/test_hook.sh    # NEW — chaining/exit-status, bypass, manifest record, uninstall-restore (sh+dash)

engine/README.md          # EDIT — document `gate-commit`
installer/README.md       # EDIT — document hook install/uninstall + bypass + chaining
```

**Structure Decision**: Single new engine module + one CLI subcommand (mirrors how 018/019/020 added `refine`, `artifact_checks`, `summarize`), plus a self-contained installer hook subsystem (`hooks/pre-commit` + `lib/hook.sh`) wired into the existing installer dispatch. The hook is intentionally thin — it only detects, honors bypass, chains, and delegates to `gate-commit`; all gate/remediation logic lives in the engine where it is unit-testable.

## Phase 0 — Research (see research.md)

Resolved decisions: **D1** gate selection by artifact kind; **D2** monotonic on the *passing-gate set* (wrap refine); **D3** completeness fixed deterministically (never the model's job); **D4** provider/engine availability probe + block-and-report degradation (tight timeouts, no hang); **D5** gate/re-stage the staged (index) content, `git add` exactly the changed artifacts; **D6** install to `git rev-parse --git-path hooks` (respects `core.hooksPath`) and chain a pre-existing hook via a recorded backup; **D7** installer lifecycle via a `git-hook` manifest adapter row; **D8** bypass surface (`REPOSKILLOPT_HOOK=off` + `--no-verify`) and round-budget default 3; **D9** honesty: gates reproducible, remediation nondeterministic.

No `NEEDS CLARIFICATION` remain (the three product forks were resolved before `/speckit.specify`).

## Phase 1 — Design & Contracts

- **data-model.md** — `GateVerdict`, `GateReport`, `ArtifactKind`, `RemediationRound`, `RemediationResult`, `HookRecord`, `ProviderAvailability`; the gate-set-monotonic acceptance rule and termination conditions stated normatively.
- **contracts/gate-commit.contract.md** — the `gate-commit` CLI: arguments (`--staged <files…>`, `--repo`, `--skill`, `--rollout-provider auto|<id>`, `--rounds`, `--timeout`, `--no-restage` for tests), exit codes (0 = all applicable gates pass / committed; 1 = non-convergence or block-and-report; 2 = usage), gate-selection table, re-stage behavior, and the no-provider/no-engine fallback.
- **contracts/pre-commit-hook.contract.md** — the hook's detect→bypass→invoke→chain contract and the installer lifecycle (install/list/uninstall, manifest row schema reuse, chained-hook backup/restore, `core.hooksPath`).
- **quickstart.md** — end-to-end: install the hook → stage an under-grounded spec → commit auto-remediates and succeeds → stage an unfixable artifact → commit blocked with per-gate report + bypass → uninstall restores prior hook.
- Update agent context via `.specify/scripts/bash/update-agent-context.sh claude`.
