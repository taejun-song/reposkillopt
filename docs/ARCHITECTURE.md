# RepoSkillOpt — Architecture, Function Reference & Relation Map

A single document to understand the entire repository: what it is, how the parts relate,
every public function/symbol, and the artifact schemas. Generated from the repo at the
state where the canonical skill is **v0.2.0** and the optional engine is **v0.1.0**.

> **Reading order:** §1 (the one idea) → §2 (relation map) → §3 (layers) → then use §6
> (function reference) and §7 (artifact schemas) as lookup tables.

---

## 1. The one idea

RepoSkillOpt is a **portable, vendor-neutral Markdown "skill"** that teaches a coding agent
to understand a legacy repository through **evidence-grounded analysis + human feedback +
bounded skill convergence**. Around that skill sits tooling that makes the workflow
*installable*, *measurable*, and *executable*:

- The **skill** (`skills/repo-skillopt/SKILL.md`) is the source of truth.
- **Adapters** mirror it into specific agent harnesses.
- A **rubric** scores the skill's output, and a **validation gate** decides whether a
  proposed change to the skill may be accepted (no-regression).
- An **installer** drops the skill into a target repo.
- An optional **Python engine** runs the gate + convergence loop automatically.

It is **self-referential**: a skill for understanding repositories that also documents its
own evolution as worked examples of that skill.

---

## 2. Relation map

```
                         ┌───────────────────────────────────────────────┐
                         │  skills/repo-skillopt/SKILL.md  (v0.2.0)        │  ← SOURCE OF TRUTH
                         │  8 normative sections; Convergence-Loop step 6  │
                         │  = "accept a proposal only with a passing gate" │
                         └───────────────┬───────────────────────────────┘
        mirrors (adapter-equivalence)    │ references templates/ by path
   ┌─────────────────────────────────────┼───────────────────────────────┐
   ▼                 ▼                    ▼                ▼               ▼
adapters/        adapters/           adapters/         adapters/      templates/
claude-code      codex               opencode          generic        repository-specification
SKILL.md         AGENTS.md           AGENTS.md         skill.md        human-feedback
(cv:0.2.0)       (cv:0.2.0)          (cv:0.2.0)        (cv:0.2.0)      rollout-log
   │                                                                   skill-edit-proposal
   │ installed by                                                          │ instantiated as
   ▼                                                                       ▼
installer/  install.sh ─► reposkillopt-install ─► lib/{targets,detect,manifest,util}.sh
   │  places an adapter into  <target-repo>/  +  writes .reposkillopt/.install-manifest
   │
   │                         the skill, when RUN, produces ▼
   │                 <target-repo>/.reposkillopt/{specs,feedback,rollouts,proposals}/
   │
   ▼ quality is measured by
rubric/  evaluation-rubric.md (15 dims) + deterministic-checks.md (7 checks)
   │        validation-gate.md  ── methodology ──►  single-scorer (003) + majority/HELD (004)
   │        gates/ (worked VG reports)   scoring/ (sheets)   scripts/ (verdict helpers)
   │
   ▼ executed by (OPTIONAL, crosses the no-network boundary)
engine/  reposkillopt_engine
        cli ─► optimizer.optimize() ─► judge.propose_edit ─► proposal.apply
                                   └─► gate.run_gate ─► judge.{generate_spec,score_spec}
                                                    └─► rubric.aggregate ─► rubric.verdict_for
        providers/ {fake | anthropic | openai_compatible}   version.bump
```

**The spine** — the gate verdict — is implemented **three times, deliberately equivalent**:
prose (`rubric/validation-gate.md`), shell (`rubric/scripts/majority-aggregate.sh`),
Python (`engine/reposkillopt_engine/rubric.py::verdict_for`). See §5.

---

## 3. Layers (directories)

| Dir | Role | Language | Tracked files |
|---|---|---|---|
| `skills/` | Canonical skill + changelog | Markdown | 2 |
| `adapters/` | Per-harness mirrors (4 targets) | Markdown | 9 |
| `templates/` | Authoring templates the skill references | Markdown | 4 |
| `rubric/` | Evaluation rubric, validation-gate methodology, worked reports, verdict helpers | Markdown + sh | 17 |
| `installer/` | One-command installer (drop an adapter into a target repo) | POSIX sh | 14 |
| `engine/` | Optional executable convergence optimizer | Python | 25 |
| `examples/` | Reference outputs against `pallets/click@8.1.7` (+ held-out demos) | Markdown | 26 |
| `specs/` | Spec-kit design record for features 001–005 | Markdown | 44 |
| `README.md`, `LICENSE`, `.gitignore`, `install.sh` | Root | — | 4 |

---

## 4. Feature history (the spec record under `specs/`)

| # | Feature | Delivered | Touches canonical? |
|---|---|---|---|
| 001 | `reposkillopt-skill` — the package: canonical skill, 4 adapters, templates, rubric, click reference outputs | v0.1.0 | created it |
| 002 | `cli-installer` — POSIX-sh installer (`install`/`list`/`uninstall`, detection, manifest) | — | no |
| 003 | `validation-gating` — single-scorer no-regression gate; **added Convergence-Loop step 6**; bumped skill 0.1.0→0.2.0; mirrored to all 4 adapters | v0.2.0 | yes (+ adapters) |
| 004 | `majority-scoring` — N-scorer majority aggregation + `HELD` verdict + adjudication; mode selection | — | no (methodology only) |
| 005 | `convergence-engine` — optional Python optimizer (gate + loop) over a provider-agnostic LLM layer | engine v0.1.0 | no (isolated in `engine/`) |

Each feature has `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `tasks.md`,
`quickstart.md` under `specs/NNN-*/`.

---

## 5. The verdict logic (the spine), cross-referenced

The same rule, three encodings — they must agree:

```
FAIL  if any dimension aggregate < baseline on any held-out repo,
      OR any deterministic check aggregates to fail.
HELD  if not FAIL, AND some dimension is low-agreement (scorer range ≥ 2)
      AND at or below baseline AND not adjudicated.        (majority mode, feature 004)
PASS  otherwise (no regression; contested-at/below all adjudicated; expected effect realized or waived).
```

| Encoding | Location | Notes |
|---|---|---|
| Prose (normative) | `rubric/validation-gate.md` → *Majority verdict rule* | the source of record |
| Shell | `rubric/scripts/gate-verdict.sh` (single), `majority-aggregate.sh` (majority) | parse a VG report's tables → PASS/FAIL/HELD |
| Python | `engine/.../rubric.py::verdict_for` + `aggregate` | runs inside the engine's gate |

Aggregation per dimension: **majority (mode)**; if no strict majority, the **median**, flagged
low-agreement when scorer range ≥ 2.

---

## 6. Function & symbol reference

### 6.1 Engine — Python (`engine/reposkillopt_engine/`)

**`rubric.py`** — dimensions, checks, aggregation, verdict
- `DIMENSIONS: tuple[str,...]` — 15 dimension keys (mirror `rubric/evaluation-rubric.md`)
- `CHECKS: tuple[str,...]` — 7 deterministic-check keys
- `class Verdict(str, Enum)` — `PASS | FAIL | HELD`
- `class ScoreCard` — one scorer's `{scores, checks}`; `.validate()`
- `class DimAggregate` — per-dimension result: `aggregate, method, range, low_agreement, vs_baseline`
- `_aggregate_dimension(values) -> (aggregate, method, range, low_agreement)`
- `aggregate(cards, baseline) -> (list[DimAggregate], checks)`
- `class RepoResult` — per-repo `dims + checks + adjudicated`
- `verdict_for(results, effect_realized=True) -> Verdict` — **the spine**

**`proposal.py`** — bounded edits
- `EDIT_KINDS` — `{ADD, REPLACE, DELETE, REORDER, SPECIALIZE, GENERALIZE, NONE}`
- `class ProposalError(ValueError)`
- `class Proposal` — `.from_dict()`, `.is_terminal`, `.eligible()`, `.apply(text) -> str`

**`gate.py`** — the runnable gate
- `class HeldOutRepo` — `name, commit, content, baseline`
- `class GateConfig` — `mode, n, effect_realized`; `.scorers()` (enforces odd N≥3 for majority)
- `class GateResult` — `verdict`, `.passed`
- `run_gate(provider, skill_text, repos, config) -> GateResult`

**`optimizer.py`** — the convergence loop
- `class Round` / `class OptimizerConfig` (`max_rounds, patience, guidance, gate`) / `class OptimizerResult` (`.accepted_count`)
- `optimize(provider, skill_text, version, repos, config) -> OptimizerResult`

**`judge.py`** — LLM-facing operations
- `_extract_json(text) -> dict` (lenient first-balanced-object parser)
- `generate_spec(provider, skill_text, repo_name, repo_content) -> str`
- `score_spec(provider, spec_text, repo_name) -> ScoreCard`
- `propose_edit(provider, skill_text, guidance) -> Proposal`

**`version.py`** — `parse(v) -> (a,b,c)`, `bump(v, level) -> str`

**`skillopt_backend.py`** — **real** microsoft/SkillOpt integration (optional dependency)
- `HAS_SKILLOPT: bool`, `SKILLOPT_VERSION`, `require()`
- `to_skillopt_edit(proposal) -> skillopt.types.Edit` (our 6 kinds → SkillOpt's append/insert_after/replace/delete)
- `apply_proposal(skill, proposal) -> str` — via **`skillopt.optimizer.apply_edit`**
- `rubric_score(results) -> float` — per-dimension aggregates → a [0,1] scalar for SkillOpt's gate
- `gate_decision(...) -> skillopt.types.GateResult` — via **`skillopt.evaluation.evaluate_gate`** (accept_new_best/accept/reject)

`optimizer.optimize(..., config.backend="skillopt")` routes edit application + the accept
decision through SkillOpt; `backend="native"` (default) uses the rubric no-regression path.

**`providers/`** — provider-agnostic LLM layer
- `base.py`: `class LLMProvider(ABC)` with `complete(prompt, *, system=None) -> str`; `class ProviderError`
- `fake.py`: `class FakeProvider` — deterministic, routes on `REGENERATE_SPEC|SCORE_SPEC|PROPOSE_EDIT`
- `anthropic.py`: `class AnthropicProvider` (Messages API via urllib)
- `openai_compatible.py`: `class OpenAICompatibleProvider` (OpenAI / local OSS endpoints)
- `__init__.py`: `make_provider(spec, **kwargs) -> LLMProvider` (factory: `fake|anthropic:<m>|openai:<m>`)

**`cli.py`** — `main(argv)`, `cmd_gate`, `cmd_optimize`, `_load_repos`, `_provider`
(`python -m reposkillopt_engine gate|optimize <config.json>`)

### 6.2 Installer — POSIX shell (`installer/`)

**`reposkillopt-install`** (entrypoint dispatch)
- `usage`, `canonical_version`, `list_valid_targets`, `resolve_root`, `do_scaffold`,
  `cmd_install`, `cmd_list`, `cmd_uninstall`

**`lib/targets.sh`** (the registry — one place to add a harness)
- `target_valid`, `target_source_files`, `target_install_rel`, `target_detect`, `target_requires_dest`

**`lib/detect.sh`** — `detect_targets <dest>` (codex+opencode both match `AGENTS.md` → ambiguous)

**`lib/manifest.sh`** — `manifest_path`, `manifest_get`, `manifest_version`, `manifest_upsert`,
`manifest_remove_row`, `manifest_list`

**`lib/util.sh`** — `say/info/warn/err`, `timestamp`, `read_field`, `semver_cmp`, `_mktemp_in`, `copy_atomic`

**`install.sh`** (root) — bootstrap: exec local installer, else fetch tarball (curl|sh path)

### 6.3 Rubric helpers — POSIX shell (`rubric/scripts/`)

- `gate-verdict.sh <report>` — single-scorer verdict from a VG report
- `majority-aggregate.sh <report>` — majority verdict (PASS/FAIL/HELD) from aggregated tables

---

## 7. Artifact schema catalog (the `contracts/`)

Each contract defines a Markdown artifact's schema + acceptance checklist.

| Contract (under `specs/NNN-*/contracts/`) | Defines |
|---|---|
| `001 canonical-skill` | the 8-section skill structure + vendor-neutrality |
| `001 adapter-equivalence` | the 14-row equivalence checklist adapters must pass |
| `001 repository-specification` | the 19-section spec the skill produces + R10 labels/citations |
| `001 feedback-item` | `FB-…` schema (11 types, scope) |
| `001 rollout-log` | `RL-…` schema (per-session log) |
| `001 skill-edit-proposal` | `SP-…` schema (6 edit kinds, ≤5-min review) |
| `001 evaluation-rubric` | the 15 dimensions + 7 deterministic checks + scoring-sheet format |
| `002 cli-interface` | installer flags, exit codes 0–5 |
| `002 target-registry` | harness → files/location/detection mapping |
| `002 install-manifest` | `<target>/.reposkillopt/.install-manifest` line format |
| `003 gate-procedure` | the 8-step gate + acceptance criterion + binding edit |
| `003 held-out-set` | commit-pinned repos + disjointness rule |
| `003 validation-gate-report` | `VG-…` schema + PASS/FAIL/HELD rule |
| `004 majority-gate-report` | `VG-…` extended: roster, per-scorer matrix, agreement, adjudication |
| `004 scoring-modes` | `single` vs `majority`, required-when rule |

**Templates** (`templates/`) instantiate four of these: `repository-specification.md`,
`human-feedback.md`, `rollout-log.md`, `skill-edit-proposal.md`.

**Working artifacts** the skill produces live under a target repo's
`.reposkillopt/{specs,feedback,rollouts,proposals}/` (never inside this project).

---

## 8. Data flow — two worked paths

### 8.1 A gate run (engine)

```
run_gate(provider, candidate_skill, [HeldOutRepo...], GateConfig)
  for each repo:
    spec  = judge.generate_spec(provider, skill, repo)      # provider call #1 (REGENERATE_SPEC)
    cards = [judge.score_spec(provider, spec, repo)          # provider calls #2..N (SCORE_SPEC)
             for _ in range(config.scorers())]               #   N=1 single, odd≥3 majority
    dims, checks = rubric.aggregate(cards, repo.baseline)    # majority/median + low-agreement
  verdict = rubric.verdict_for(results, effect_realized)     # PASS | FAIL | HELD
```

### 8.2 The convergence loop (engine)

```
optimize(provider, skill, version, repos, OptimizerConfig)
  repeat up to max_rounds:
    proposal = judge.propose_edit(provider, skill, guidance)  # PROPOSE_EDIT; NONE => converged
    if not proposal.eligible(): skip (count toward patience)
    candidate = proposal.apply(skill)                         # bounded edit
    gate = run_gate(provider, candidate, repos, gate_cfg)
    if gate.verdict == PASS:  skill = candidate; version = bump(version, level); reset patience
    else:                     keep skill; count toward patience
  stop on NONE / max_rounds / patience consecutive non-accepts
```

---

## 9. Tests & verification

| Suite | Run | Count |
|---|---|---|
| Installer | `sh installer/tests/run.sh` | 7 |
| Single-scorer verdict | `sh rubric/scripts/test_gate_verdict.sh` | (PASS/FAIL/usage) |
| Majority verdict | `sh rubric/scripts/test_majority_aggregate.sh` | (PASS/HELD/usage) |
| Engine | `cd engine && python3 -m unittest discover -s tests -t .` | 26 |

Engine tests use the deterministic **FakeProvider** — no network, no API key — and cover
aggregation, the PASS/FAIL/HELD verdict, proposal application, version bump, the gate
(single/majority/outlier/odd-N), and the optimizer loop.

---

## 10. Honest notes (what is real vs. illustrative)

- **Executable & tested**: the installer, the two shell verdict helpers, and the entire
  Python engine core + loop (via the fake provider). These genuinely run and are covered by tests.
- **Illustrative by design**: the scoring sheets and VG reports under `rubric/` and the
  reference specs under `examples/` are *worked examples* of the methodology — they are **not**
  verified analyses of the named repositories at their pinned commits. Every such file says so.
- **Structurally complete but unexercised here**: the real `AnthropicProvider` /
  `OpenAICompatibleProvider` network paths (no API keys / held-out repos checked out in this repo).
- **Real & exercised — the SkillOpt backend**: `engine/.../skillopt_backend.py` genuinely uses
  the `skillopt` PyPI package (microsoft/SkillOpt) — `optimize(..., backend="skillopt")` applies
  edits with `skillopt.optimizer.apply_edit` and decides accept/reject with
  `skillopt.evaluation.evaluate_gate`. Covered by passing tests (skipped only if `skillopt` is absent).
- **Scope boundary**: the core is skill-first (Markdown + optional shell, no required network).
  The `engine/` deliberately crosses that line (it calls an LLM) and is therefore isolated and
  opt-in; it never edits the canonical skill at run time.
- **Version state**: canonical skill `v0.2.0` (all four adapters mirror `canonical_version: 0.2.0`);
  engine package `v0.1.0`.
