# Data Model — 005 Real-Analysis-Driven Optimization

## EvidencePack
The cached body of real repository evidence handed to spec generation and used as the basis for citation resolution.

| Field | Type | Notes |
|---|---|---|
| `repo_path` | str | absolute path to the target repo (resolution root) |
| `repo_name` | str | display name |
| `text` | str | the assembled, bounded evidence (README, manifests, trees, line-numbered key files, grep hits) |
| `included_files` | list[str] | repo-relative paths whose contents were embedded (with line numbers) |
| `omitted` | list[str] | what was dropped to fit the budget (recorded, not silent — FR-003) |
| `char_budget` | int | configured bound (default 60000) |

- Built once per run (FR-002). `text` is what `generate_spec` receives in place of the old digest.
- Invariant: `len(text) ≤ char_budget`; if truncation occurred, `omitted` is non-empty.

## Citation (parsed from a spec)
| Field | Type | Notes |
|---|---|---|
| `raw` | str | the citation as written |
| `path` | str | repo-relative file path |
| `kind` | enum | `line` \| `range` \| `symbol` \| `symbol_line` \| `cmd` \| `malformed` |
| `line` / `start` / `end` | int? | as applicable |
| `symbol` | str? | as applicable |

## GroundingResult
Output of resolving a spec against a repo (deterministic, no LLM).

| Field | Type | Notes |
|---|---|---|
| `citations` | list[Citation] | all parsed |
| `resolved` | int | count that resolve against the repo |
| `resolvable_total` | int | citations excluding `cmd`/`output` |
| `rate` | float | `resolved / resolvable_total` (1.0 if none resolvable) |
| `checks` | dict[str,bool] | the 7 rubric checks, citation-bearing ones computed deterministically |
| `failures` | list[str] | concrete, human-readable grounding defects (drive reflect — FR-009) |

## Reward (combined)
| Field | Type | Notes |
|---|---|---|
| `rubric_norm` | float | `Σ dim.aggregate / (15×3)` ∈ [0,1] |
| `det_rate` | float | `mean(checks.values())` ∈ [0,1] |
| `value` | float | `0.5×rubric_norm + 0.5×det_rate` ∈ [0,1] |

- SC-001/SC-008: for identical specs differing only in fabricated vs resolving citations, `det_rate` (hence `value`) is strictly higher for the resolving one.

## RunOutputs
| Field | Type | Notes |
|---|---|---|
| `specialized_skill_path` | path | `<repo>/.reposkillopt/best_skill.md` |
| `best_spec_path` | path | `<repo>/.reposkillopt/specs/optimized-repository-specification.md` |
| `accepted` | int | edits accepted by the gate (may be 0 — FR-013) |
| `best_reward` | float | combined reward of the emitted skill's spec |

## Changed existing types
- **RepoTask**: add `pack: EvidencePack | None`. `digest` retained for the fake path/back-compat.
- **NativeResult**: add `best_spec: str` and `best_reward: float` so the CLI can write the spec output and report grounding.
