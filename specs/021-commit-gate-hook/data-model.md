# Data Model: Commit-Time Gate Hook

All entities are in-memory (engine) or lines in the existing manifest (installer). No new persisted
schema; the manifest format is unchanged.

## ArtifactKind (enum-like string)

One of: `repo_spec`, `architecture`, `impact`, `adr`, `ledger`, `other`.
Derived by `classify_artifact(path, text)` — a pure function of the file path and content
(deterministic; see research D1). Drives `select_gates`.

## Gate (identifier)

One of the four gate ids: `coverage`, `grounding`, `completeness`, `check_artifact`.
`select_gates(kind) -> list[Gate]` returns the applicable subset (D1 table). Each gate is evaluated by
reusing existing code:

| Gate | Backed by | Pass condition |
|---|---|---|
| `coverage` | `scripts/coverage-gate.sh --files` (or `compute_structure` file accounting) | every source file mentioned (exit 0) |
| `grounding` | `grounding.ground_spec` (frozen) | `rate == 1.0` (every `[fact]` resolves) |
| `completeness` | `quality/structure.compute_structure(...).symbol_coverage` | `== 1.0` |
| `check_artifact` | `artifact_checks.check_{architecture_view,impact_analysis,adr,task_ledger}` | `CheckResult.passed` |

## GateVerdict

```
GateVerdict:
  gate:    Gate
  passed:  bool
  reasons: list[str]   # human-readable failures (empty when passed); reused from each check's output
```

## GateReport

```
GateReport:
  artifact:  str                 # repo-relative path
  kind:      ArtifactKind
  verdicts:  list[GateVerdict]   # one per applicable gate
  passing:   frozenset[Gate]     # {v.gate for v in verdicts if v.passed} — the monotonicity key
  all_pass:  bool                # every applicable gate passed
```

**Invariant**: `passing ⊆ set(select_gates(kind))`. `all_pass == (passing == set(select_gates(kind)))`.

## RemediationRound

```
RemediationRound:
  round:        int
  before:       frozenset[Gate]  # passing set carried into this round
  after:        frozenset[Gate]  # passing set of the candidate
  gap_count:    int              # len(spec_gaps(repo, candidate))
  accepted:     bool             # after ⊇ before AND strictly-better (D2)
  regressed:    bool             # not (after ⊇ before) — candidate dropped, never committed
```

**Acceptance rule (D2)**: `accepted == (after ⊇ before) and ((after > before) or (after == before and gap_count < prev_gap_count))`.
A round with `after ⊉ before` is `regressed=True, accepted=False` and is discarded.

## RemediationResult

```
RemediationResult:
  artifact:   str
  final_text: str                 # the converged (or best-so-far) artifact
  converged:  bool                # all applicable gates pass
  rounds:     list[RemediationRound]
  changed:    bool                # final_text != original staged text (→ candidate for re-stage)
```

**Termination (FR-005)**: the loop stops at the first of — all gates pass; round budget reached; a
round yields no improvement (`accepted=False` for a non-regressing candidate, i.e. the model can't make
progress). Guarantees no unbounded loop.

## ProviderAvailability

```
ProviderAvailability:
  provider:   LLMProvider | None  # None ⇒ block-and-report
  id:         str | None          # claude-cli | opencode-cli | ollama
  probed:     list[str]           # candidates tried (for the report)
```

Resolved by `detect_keyless_provider(spec, timeout)` (D4). `None` ⇒ deterministic-only run.

## CommitGateOutcome (entrypoint return)

```
CommitGateOutcome:
  reports:     list[GateReport]        # final per-artifact gate state
  remediations:list[RemediationResult] # per artifact that needed work
  restaged:    list[str]               # paths git-add'd (re-stage accounting, D5)
  exit_code:   int                     # 0 = all applicable gates pass (commit proceeds);
                                        # 1 = non-convergence OR block-and-report; 2 = usage
  degraded:    bool                    # True when no provider/engine reachable (block-and-report)
```

## HookRecord (manifest row — existing format, new adapter id)

A single TAB-separated manifest line:

```
git-hook <TAB> <tool_version> <TAB> <installed_hook_path>[,<chained_backup_path>] <TAB> <timestamp>
```

- `installed_hook_path` — the `pre-commit` written under `git rev-parse --git-path hooks`.
- `chained_backup_path` — present only if a pre-existing hook was moved aside (D6); uninstall restores
  it. Absent when there was no prior hook.

**Lifecycle**: install ⇒ `manifest_upsert(target, "git-hook", version, paths_csv)`; list ⇒
`manifest_list`; uninstall ⇒ restore backup (if recorded) then `manifest_remove_row(target, "git-hook")`.
