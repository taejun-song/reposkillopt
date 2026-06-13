<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
  <img src="assets/logo.svg" alt="RepoSkillOpt" width="460">
</picture>

### Teach any coding agent to understand a legacy repo — and produce an evidence-grounded spec it can't fake.

[![license](https://img.shields.io/badge/license-Apache%202.0-4F46E5)](LICENSE)
[![canonical skill](https://img.shields.io/badge/canonical%20skill-v0.7.0-4F46E5)](skills/repo-skillopt/SKILL.md)
![engine tests](https://img.shields.io/badge/engine%20tests-116%20passing-10B981)
![runs](https://img.shields.io/badge/runs-keyless%20%7C%20offline-10B981)
![scoring](https://img.shields.io/badge/scoring-deterministic-64748B)

</div>

RepoSkillOpt is a portable, vendor-neutral **Markdown skill** (plus optional tooling) that gives Claude Code, Codex, OpenCode, or any custom agent a disciplined way to read an unfamiliar codebase: every major claim is **labeled and cited to a real `file:line`**, uncertainty is called out, and your feedback is folded back into the skill itself.

- 🧭 **Evidence-grounded** — facts carry citations; hypotheses are marked `[inference]`; an honest `[unknown]` beats a confident guess.
- 🔌 **Works anywhere** — one skill, thin adapters per agent; installs online **or fully offline**; runs against API, OSS, or a local LLM.
- 🎯 **Self-tuning per repo** — an optional engine specializes the skill for *your* codebase, scored by how well its citations actually resolve against real files (historic grounding lift **74% → 98%** on `pallets/click`, **69% → 100%** on `itsdangerous`).
- ✅ **Guarantees, not just lift** — a v0.5.0 spec is **100% citation-grounded, 100% section-complete, and accounts for 100% of functions/classes** (measured deterministically), with malformed citations driven toward zero — before any tuning.

Not a service, not a database, not a fine-tune — just a skill, templates, adapters, and a rubric.

## ⚡ Quick start

From inside the repository you want to understand:

```sh
# install the skill for your agent  (claude-code shown; also: codex | opencode | generic)
curl -fsSL https://raw.githubusercontent.com/taejun-song/reposkillopt/main/install.sh | sh -s -- --agent claude-code
```

Then open your agent and ask:

> *“Help me understand this repository.”*

The skill runs a seven-stage workflow and writes a Repository Specification to `.reposkillopt/specs/`. Correct it in plain prose — each correction is recorded and the spec is revised. No API key, no service; offline from a clone works too: `installer/reposkillopt-install --agent claude-code --dest .`.

## 📄 What it produces

A 19-section spec where **every major claim is labeled and cited**. Real excerpt — analysing [`pallets/click@8.1.7`](https://github.com/pallets/click):

```markdown
## Repository overview
**[fact]** Click is "a simple Python module … to make writing command line scripts fun"
— distributed as the `click` package (`src/click/__init__.py:1-5`).
**[inference]** The codebase is library-shaped (no application entrypoint of its own).
Basis: the public API is exposed only via `__init__.py` re-exports; no `__main__.py`.

## Known risks
- **[fact]** `filterwarnings = error` makes any new warning a test failure
  (`setup.cfg:41-42`) — an upstream deprecation can break the suite even if Click is unchanged.
- **[fact]** Windows-only code paths are platform-sensitive: `src/click/_winconsole.py:30`
  asserts `sys.platform == "win32"`; Linux CI gives no signal.
```

Full samples for every adapter live in [`examples/reference-output/`](examples/reference-output/).

**Optional — specialize the skill for your repo.** The engine tunes a per-repo skill and reports how grounded it is:

```console
$ reposkillopt-engine optimize-repo ./my-service --skill skills/repo-skillopt/SKILL.md --rounds 2
  building evidence pack … 7 files embedded
  round 1: accept_new_best     round 2: reject
  final version 0.3.0; 1 accepted of 2 rounds
  reward 0.78; citation resolution 95%
  wrote skill -> ./my-service/.reposkillopt/best_skill.md
  wrote spec  -> ./my-service/.reposkillopt/specs/optimized-repository-specification.md
```

**Measured, not hand-waved.** A grounding benchmark scores a spec by how many of its
`file:line` citations actually resolve against the real repo. Optimizing the skill *for a repo*
closes grounding gaps where they exist — and holds steady where the baseline is already clean.

*Grounding lift — measured at canonical **v0.2.0**, when these repos still had headroom:*

| Repo (generate-mode grounding) | Canonical v0.2.0 | Per-repo optimized |
|---|---|---|
| `pallets/click` | 74% | **98%** |
| `pallets/itsdangerous` | 69% | **100%** |
| `pallets/markupsafe` | 100% | 98% |
| `chalk/chalk` (JS) | 100% | 100% |

The two repos with real gaps were fixed (the optimizer *learned, from each repo's own grounding
failures, to cite real filesystem paths* — `src/click/core.py:57`, not `core.py:57`); the two
already-grounded repos held (chalk's gate accepted **0** edits — nothing to fix).

As the canonical skill matured (now **v0.5.0**), those baselines rose toward ceiling — so the
headline shifted from *lift* to **guarantees that always hold**, measured deterministically
(model-free) on every spec:

*Deterministic guarantees — clean A/B on `pallets/click` at canonical **v0.5.0**:*

| Deterministic axis | Canonical v0.5.0 | Per-repo optimized |
|---|---|---|
| Citation grounding (cited `file:line` resolve) | 99.5% (184/185) | **100%** (195/195) |
| Symbol coverage (every function/class accounted) | **100%** | **100%** |
| Section completeness (all 19 sections) | **100%** | **100%** |
| Quality score (evidence discipline) | 97% | **98%** |
| Malformed-citation rate (lower is better) | 2.2% | **0.5%** |

A v0.5.0 spec is **fully grounded, fully sectioned, and accounts for every symbol** before any
per-repo tuning; the optimizer then closes the last grounding gap and trims malformed citations.
`analyzed_fraction` (how much got real prose analysis) is reported honestly and separately —
*accounting* is guaranteed 100%, *analysis depth* is best-effort.

click is a small, near-ceiling library — so the *lift* shows on a **larger real-world repo**.
On `eco-standard-wiki` (1,617 functions/classes, **79 DB tables**), per-repo optimization at
v0.5.0 closes a real grounding gap *and* perfects the ER diagram:

*Lift on a large real repo — clean A/B on `eco-standard-wiki` at canonical **v0.5.0**:*

| Deterministic axis | Canonical v0.5.0 | Per-repo optimized |
|---|---|---|
| Citation grounding (cited `file:line` resolve) | 87.4% (173/198) | **99.0%** (204/206) |
| **ER-diagram grounding** (entities vs real tables) | 92.3% | **100%** |
| Analyzed fraction (symbols given real prose analysis) | 10.7% | **27.8%** |
| Malformed-citation rate (lower is better) | 5.1% | **3.4%** |
| Symbol coverage / Section completeness | 100% / 100% | 100% / 100% |

The optimizer accepted **2 of 2** rounds (it learned, from eco-wiki's own grounding failures, to
cite real paths and to ground every ER entity to a schema file). The generated spec carries **two
Mermaid `flowchart` traces and a 100%-grounded `erDiagram`** of the real tables — concrete proof
the v0.5.0 presentation format (tables + flowcharts + ER diagram) holds up on a production codebase.

Method, exact numbers, and reproduce steps in [`rubric/benchmarks/`](rubric/benchmarks/).

## 🧩 Architecture at a glance

```text
  CANONICAL   skills/repo-skillopt/SKILL.md      — vendor/repo-neutral, source of truth
      │  mirrored 1:1 (adapter-equivalence)
      ▼
  ADAPTERS    claude-code · codex · opencode · generic   (thin wrappers, same content)


  ── Layer 1 · run the generic skill on any repo ──────────────────────────────
      installer/            ─►  drops the right adapter into  <target-repo>
      agent runs the skill  ─►  <target-repo>/.reposkillopt/{specs,feedback,rollouts,proposals}/


  ── Layer 2 · specialize the skill for one repo  (optional engine) ───────────
      engine/ optimize-repo ─►  reads <target-repo> + the canonical skill
          reward   = rubric (15 dims + 7 checks)  +  citation-grounding vs real files
          edits    = microsoft/SkillOpt  (generate → apply → gate)
          LLM      = API · OSS · local server (air-gapped)
          writes   = <target-repo>/.reposkillopt/best_skill.md  +  optimized spec
          (the canonical skill is never modified)


  ── Quality bar  (shared by both layers) ─────────────────────────────────────
      rubric/           evaluation-rubric (15 dimensions, 0–3)  +  deterministic-checks (7)
      validation-gate   single-scorer (003)  ·  majority / HELD (004)
```

Full version — relation map, function reference, schemas — in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

### Two layers: a generic base, then per-repo specialization

RepoSkillOpt is deliberately **layered** — this is the key mental model:

1. **Generic layer (the base you install everywhere).** The canonical
   [`skills/repo-skillopt/SKILL.md`](skills/repo-skillopt/SKILL.md) is vendor- and
   repo-neutral. Its self-improvement path (the *Skill Convergence Loop*) is intentionally
   conservative: it accepts only edits that **generalize** across repositories, gated against a
   held-out reference set — so the shared base never absorbs any single repo's quirks.

2. **Specialization layer (one tuned skill per repository).** The optional engine's
   [`optimize-repo`](engine/README.md) takes that base and tunes a **per-repo** skill for one
   target repository, scoring candidate skills by how well the spec they produce is **grounded
   in that repo** — every `file:line` / `file:Symbol` citation must resolve against the real
   files. It writes two artifacts under the *target* repo and **never modifies the canonical
   skill**:
   - `<repo>/.reposkillopt/best_skill.md` — the specialized skill for this repo
   - `<repo>/.reposkillopt/specs/optimized-repository-specification.md` — the spec it earned

So *"each repository can have a different, tuned skill"* is achieved **without** polluting the
shared base: the canonical stays generic; specialization is an opt-in layer on top.

## 📦 What you get

```text
skills/repo-skillopt/SKILL.md      # The canonical skill — single source of truth
skills/repo-skillopt/CHANGELOG.md  # Semantic version history

templates/                         # Authoring templates the skill references
├── repository-specification.md
├── human-feedback.md
├── rollout-log.md
└── skill-edit-proposal.md

rubric/                            # Evaluation rubric (qualitative + deterministic)
├── evaluation-rubric.md
└── deterministic-checks.md

install.sh                         # One-line bootstrap for the CLI installer
installer/                         # Optional POSIX-sh installer (install/list/uninstall)
├── reposkillopt-install
├── lib/{util,targets,detect,manifest}.sh
└── tests/

adapters/                          # Thin per-environment wrappers around the canonical skill
├── claude-code/SKILL.md
├── codex/AGENTS.md
├── opencode/AGENTS.md
└── generic/{skill.md, system-prompt-fragment.md}

examples/reference-output/         # Sample outputs against pallets/click@8.1.7 for each adapter
└── {claude-code,codex,opencode,generic}/.reposkillopt/
    ├── specs/                     # Sample Repository Specifications
    ├── feedback/                  # Sample Feedback Items
    ├── rollouts/                  # Sample Rollout Logs
    └── proposals/                 # Sample Skill Edit Proposals

.gitignore                         # Excludes local working artifacts and build-time tooling (.claude/, .specify/, CLAUDE.md)
```

## 🚀 Install & use across agents

### Working-artifact layout

When you (or an agent) use this skill on a *target* repository, the skill writes its working artifacts under a fixed layout at that repository's root:

```text
<target-repo>/.reposkillopt/
├── specs/         # The Repository Specifications the agent produces
├── feedback/      # Your feedback items (one Markdown file per item)
├── rollouts/      # One log per agent session
└── proposals/     # Bounded edits proposed for the canonical skill
```

Every adapter writes to and reads from this same layout, so artifacts produced under one adapter remain readable by another.

### Install with the CLI (one command)

The optional installer drops the right adapter into a target repo for you. From inside your target repository:

```sh
curl -fsSL https://raw.githubusercontent.com/taejun-song/reposkillopt/main/install.sh | sh -s -- --agent claude-code
```

Or, after cloning this repo, run it directly (audit-friendly, fully offline):

```sh
/path/to/reposkillopt/installer/reposkillopt-install --agent claude-code --dest /path/to/target-repo
```

RepoSkillOpt installs as a **namespaced Agent Skill** (a `repo-skillopt/SKILL.md` folder) into each harness's native skills directory — collision-free, and it **never touches a repo's `AGENTS.md`**:

| Target | `--agent` | Installs to | Read by |
|---|---|---|---|
| Claude Code | `claude-code` | `<dest>/.claude/skills/repo-skillopt/SKILL.md` | Claude Code |
| Codex | `codex` | `<dest>/.agents/skills/repo-skillopt/SKILL.md` | Codex |
| OpenCode | `opencode` | `<dest>/.opencode/skills/repo-skillopt/SKILL.md` | OpenCode |
| Cursor | `cursor` | `<dest>/.cursor/skills/repo-skillopt/SKILL.md` | Cursor |
| **Cross-tool** | `agents` | `<dest>/.agents/skills/repo-skillopt/SKILL.md` | **Codex + OpenCode + Cursor** |
| Generic | `generic` | `<dest>/skill.md` + `system-prompt-fragment.md` (requires `--dest`) | prompt-fragment harnesses |

Since the SKILL.md *Agent Skills* format is now a cross-tool open standard, the `codex`/`opencode`/`cursor`/`agents` targets install the **canonical skill** directly. One `--agent agents` install is read by Codex, OpenCode, and Cursor at once.

**Legacy single-file `AGENTS.md`** is still available via `--agent codex-agentsmd` / `opencode-agentsmd`, but it **never silently overwrites** an existing `AGENTS.md` it didn't create: it refuses unless `--force`, and `--force` first backs the file up to `AGENTS.md.bak`.

Useful flags: `--scaffold` (create the `.reposkillopt/` dirs), `--dry-run`, `--list`, `--uninstall <agent>`. With no `--agent` the installer auto-detects the harness and, if that's ambiguous, exits with the valid targets rather than guessing. See `installer/README.md` for full details.

### Manual install (Claude Code)

1. Copy the Claude Code adapter into the target environment:
   ```sh
   mkdir -p <target-repo>/.claude/skills/repo-skillopt
   cp adapters/claude-code/SKILL.md <target-repo>/.claude/skills/repo-skillopt/SKILL.md
   ```
2. Verify the adapter's `canonical_version` matches the canonical skill:
   ```sh
   grep '^version:' skills/repo-skillopt/SKILL.md
   grep '^canonical_version:' <target-repo>/.claude/skills/repo-skillopt/SKILL.md
   # Both should print the same semver.
   ```
3. Open Claude Code in `<target-repo>` and prompt:
   > "Help me understand this repository."

   The skill activates, executes the seven-stage workflow, and writes a Repository Specification to `<target-repo>/.reposkillopt/specs/repository-specification.md`.

4. Provide corrections as prose; the agent records each one to `.reposkillopt/feedback/` and revises the spec. See `adapters/claude-code/README.md` for the full flow.

### Other agent harnesses

| Harness | Source | Install location |
|---|---|---|
| Claude Code | `adapters/claude-code/SKILL.md` | `<target-repo>/.claude/skills/repo-skillopt/SKILL.md` |
| Codex | canonical `skills/repo-skillopt/SKILL.md` | `<target-repo>/.agents/skills/repo-skillopt/SKILL.md` |
| OpenCode | canonical `skills/repo-skillopt/SKILL.md` | `<target-repo>/.opencode/skills/repo-skillopt/SKILL.md` |
| Cursor | canonical `skills/repo-skillopt/SKILL.md` | `<target-repo>/.cursor/skills/repo-skillopt/SKILL.md` |
| Cross-tool | canonical `skills/repo-skillopt/SKILL.md` | `<target-repo>/.agents/skills/repo-skillopt/SKILL.md` |
| Generic / custom | `adapters/generic/skill.md` + `system-prompt-fragment.md` | per harness convention |
| Codex/OpenCode (legacy `AGENTS.md`) | `adapters/{codex,opencode}/AGENTS.md` | `<target-repo>/AGENTS.md` (opt-in; non-destructive) |

See each adapter's own guide for installation specifics and "Known cross-agent differences":

- `adapters/claude-code/README.md`
- `adapters/codex/README.md`
- `adapters/opencode/README.md`
- `adapters/generic/README.md`

For a full end-to-end walkthrough against `pallets/click@8.1.7`, see `specs/001-reposkillopt-skill/quickstart.md`.

## 🗣️ Provide feedback

Feedback is a first-class input. After the agent produces a Repository Specification:

1. Tell the agent what is wrong, missing, mis-named, or under-supported.
2. The agent writes a Feedback Item to `<target-repo>/.reposkillopt/feedback/FB-YYYY-MM-DD-NNN-<slug>.md` using `templates/human-feedback.md` and assigns it a `type` (correction / missing-context / terminology / quality-rating / …) and a `scope`:
   - `repository-scoped` — stays in this target repository only; never enters the canonical skill.
   - `candidate-for-generic` — may be cited by a future Skill Edit Proposal targeting the canonical skill.
3. The agent revises the Repository Specification and updates the rollout log.

## 🔁 Propose canonical skill edits

When several Feedback Items point at the same gap in the canonical skill, ask the agent to summarize the pattern and propose edits:

1. The agent writes one or more Skill Edit Proposals to `<target-repo>/.reposkillopt/proposals/SP-YYYY-MM-DD-NNN-<slug>.md` using `templates/skill-edit-proposal.md`.
2. Each proposal is bounded (≤5 minutes of human review), categorized as `ADD` / `REPLACE` / `DELETE` / `REORDER` / `SPECIALIZE` / `GENERALIZE`, and references the supporting Feedback Item ids.
3. A maintainer accepts or rejects each proposal. Accepted edits are applied to `skills/repo-skillopt/SKILL.md` (in this repository) and bump the canonical `version:`. Rejected proposals are preserved with rationale.

## 🧪 Evaluation

See `rubric/evaluation-rubric.md` (15 qualitative dimensions, scored 0–3) and `rubric/deterministic-checks.md` (7 pass/fail checks). The rubric is technology-agnostic and is the same instrument used to compare canonical skill versions over time.

**Validation gate.** Accepting a `scope: generic` skill edit into the canonical skill now requires a passing **validation gate**: the candidate edit must regenerate specifications for a commit-pinned **held-out reference set** (disjoint from the repositories that motivated it) without regressing any per-dimension rubric score and without any deterministic-check regression. See `rubric/validation-gate.md` (procedure + criterion), `rubric/held-out-set.md` (the held-out repos), and `rubric/gates/` (the reports). This is canonical from skill version `0.2.0`. For high-stakes edits the gate can be scored in **majority mode** — N independent scorers (odd, ≥3) with per-dimension majority aggregation and a `HELD` outcome for contested potential regressions; see `rubric/validation-gate.md` → *Majority mode*. (Majority mode is scoring methodology only — it requires no canonical or adapter change.)

## ⚙️ Executable engine (optional, opt-in)

An optional Python **convergence engine** under [`engine/`](engine/README.md) makes both
layers *runnable*, over a provider-agnostic LLM layer (Anthropic, OpenAI, or any
OpenAI-compatible / open-source endpoint — including a **local LLM server**, fully air-gapped
at runtime):

- **Generic convergence** — propose a bounded edit → run the validation gate → accept and bump
  the canonical version only on PASS → repeat. The executable counterpart to
  `rubric/validation-gate.md`.
- **Per-repo specialization (`optimize-repo`)** — tune a specialized skill for one target
  repository. The reward combines the rubric with **deterministic citation-grounding**: a
  cached evidence pack is built once from the real repo, each candidate's spec is scored partly
  by how many of its `file:line` / `file:Symbol` citations **resolve against the actual files**,
  and the concrete grounding failures steer the next edit. Emits `best_skill.md` + the spec it
  earned; the canonical skill is never touched.

It can optionally **use the real [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)
package** (`pip install skillopt`): `--backend skillopt` applies edits with SkillOpt's
`apply_edit` and gates with `evaluate_gate`, and `optimize-repo` hands the **whole** ReflACT
loop (edit generation + apply + gate) to SkillOpt. So beyond being *inspired by* SkillOpt, the
engine genuinely runs on it.

> **Scope note.** The RepoSkillOpt core is deliberately skill-first (Markdown + optional
> shell, no service/network). The engine **intentionally crosses that line** (it calls an
> LLM) and is therefore isolated in `engine/` and **strictly optional** — the skill,
> adapters, templates, rubric, and installer all work without it, and it never edits the
> canonical skill at run time. See `engine/README.md`.

## 🏷️ Versioning

The canonical skill follows [Semantic Versioning](https://semver.org/). The `version:` field in `skills/repo-skillopt/SKILL.md` is the source of truth; every adapter mirrors it via its `canonical_version:` field (in YAML front matter or, for environments that forbid YAML front matter, in an HTML-comment metadata block at the top of the adapter file). Changes are recorded in `skills/repo-skillopt/CHANGELOG.md` using [Keep a Changelog](https://keepachangelog.com/) conventions.

## ⚠️ Limitations

RepoSkillOpt does **not** claim universal repository understanding. In particular:

- The skill ships with adapters and reference outputs for one open-source legacy repository (`pallets/click@8.1.7`). Other ecosystems work — the skill is language-agnostic — but examples will grow over time.
- The skill is **not** a replacement for human code review. It produces a structured, evidence-grounded artifact that an engineer can trust and act on; it does not approve changes on anyone's behalf.
- Initial language coverage is limited by example, not by design. Languages, frameworks, and project types beyond those exercised in `examples/` may surface gaps that subsequent feedback rounds can address.
- The skill performs no deep static analysis; it relies on what an ordinary agent harness can read with file and shell access.
- The skill runs entirely locally and does not exfiltrate repository contents to external services unless your chosen agent harness is independently configured to do so.

## 📜 License

Apache-2.0. See `LICENSE`.

## Understanding the whole repo

- **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — one document covering the entire repo:
  the relation map, layer architecture, the full function/symbol reference (Python engine +
  shell), the artifact-schema catalog (all contracts/templates), the gate-verdict spine, and
  data-flow walkthroughs.

## Design documents

- Specification: `specs/001-reposkillopt-skill/spec.md`
- Implementation plan: `specs/001-reposkillopt-skill/plan.md`
- Phase-0 research decisions: `specs/001-reposkillopt-skill/research.md`
- Artifact schemas: `specs/001-reposkillopt-skill/data-model.md`
- Contracts: `specs/001-reposkillopt-skill/contracts/`
- Quickstart walkthrough: `specs/001-reposkillopt-skill/quickstart.md`
