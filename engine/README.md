# RepoSkillOpt Convergence Engine

An **opt-in, executable** optimizer that runs the RepoSkillOpt validation gate and the
convergence loop in code — the functional counterpart to the Markdown methodology in
`rubric/validation-gate.md` (features 003/004). It is the closest analogue in this project
to microsoft/SkillOpt's `train.py`: **propose a bounded skill edit → run the validation
gate → accept (and bump the version) only if it PASSes → repeat**, gated by the rubric
instead of a benchmark reward, and **without touching model weights**.

It can also **actually use microsoft/SkillOpt** (the real `skillopt` PyPI package) as an
optional optimizer backend — not just be inspired by it. See *SkillOpt backend* below.

## ⚠️ Scope boundary (read this)

The RepoSkillOpt **core is deliberately skill-first** — Markdown + optional shell helpers,
no service, no required network, no model calls. **This engine intentionally crosses that
line** (it calls an LLM to regenerate and score specs). It therefore lives in its own
top-level `engine/` directory and is **strictly optional**:

- The canonical skill, adapters, templates, rubric, and installer work exactly as before
  **without** this engine.
- Nothing here edits the canonical skill or adapters at import/run time; the optimizer
  returns new skill *text* and a proposed version — applying it to `skills/repo-skillopt/`
  remains a deliberate, reviewable human step.
- Using a real provider requires **your own API key** in the environment. The default
  provider is an offline, deterministic fake.

## Install / run

No third-party dependencies (standard library only). From `engine/`:

```sh
python3 -m reposkillopt_engine --provider fake gate examples/gate-fake.json -v
python3 -m reposkillopt_engine --provider fake optimize examples/optimize-fake.json --out final_skill.md
```

Or install the console script: `pip install -e engine` → `reposkillopt-engine gate <config>`.

## Providers (provider-agnostic, incl. open-source models)

| `--provider` | Backend | Env |
|---|---|---|
| `fake` (default) | Deterministic offline provider for tests/dry-runs | — |
| `anthropic:<model>` | Anthropic Messages API | `ANTHROPIC_API_KEY` |
| `openai:<model>` | OpenAI **or any OpenAI-compatible endpoint** — vLLM, Ollama's OpenAI shim, llama.cpp server, LM Studio, etc. | `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| `ollama:<model>` | **Open-source models via Ollama**, no key — defaults `base_url` to `http://localhost:11434/v1` (override `OLLAMA_BASE_URL`) | — |
| `claude-cli` | Local **Claude Code CLI** (`claude -p`) — real LLM calls with **no API key** when run where `claude` is installed | — |
| `opencode-cli` / `opencode-cli:<provider/model>` | Local **OpenCode CLI** (`opencode run`) — real LLM calls with **no API key**, using OpenCode's configured model (incl. local/OSS) when `opencode` is installed and authed | — |

Open-source / local models are reached through `ollama:<model>` (e.g. `ollama:qwen2.5-coder`) or
`openai:<model>` with `OPENAI_BASE_URL` at the local server. **Chat-model output is sanitized**
(`sanitize.py`): an outer ```` ```markdown ```` wrapper or conversational pre/postamble that open-source
models add is stripped before grounding/completeness (inner ```` ```mermaid ```` fences preserved), so a
weaker model's spec still parses. And because scoring is deterministic, the guarantees hold regardless
of model quality: completeness forces 100% symbol coverage and grounding flags fabricated citations
even when the model is small. Adding a new backend = one small `LLMProvider.complete()` subclass.

The `claude-cli` provider is what makes a **real, no-API-key** end-to-end run possible inside
a Claude Code environment — and it is verified: a live `tests/test_claude_cli_live.py`
(opt-in via `RSO_LIVE_CLAUDE=1`) regenerates a spec for a tiny repo and scores it into a full
15-dimension / 7-check card.

## What it does

1. **Gate** (`gate.py`) — for each commit-pinned held-out repo: regenerate a Repository
   Specification with the candidate skill, score it against the 15-dimension rubric + 7
   deterministic checks (N scorers in `majority` mode), aggregate (majority/median +
   low-agreement), and decide **PASS / FAIL / HELD** per features 003/004.
2. **Optimize** (`optimizer.py`) — propose a bounded edit (`judge.propose_edit`), apply it
   (`proposal.py`), run the gate, accept + bump the version only on PASS, and loop until
   convergence (`NONE`), a round budget, or `patience` consecutive rejects.

## Config file

```json
{
  "skill_path": "../skills/repo-skillopt/SKILL.md",
  "version": "0.2.0",
  "held_out": [
    {"name": "benjaminp/six", "commit": "1.16.0", "content": "<repo material>",
     "baseline": {"architectural_correctness": 3, "...": 3}}
  ],
  "gate": {"mode": "majority", "n": 3},
  "max_rounds": 10, "patience": 2
}
```

`content` is the repository material handed to the provider (file excerpts, tree, key
sources). `baseline` is the per-dimension floor (the released version's scores).

## SkillOpt backend (real microsoft/SkillOpt)

Install the optional dependency and switch the optimizer to SkillOpt's own machinery:

```sh
pip install "reposkillopt-engine[skillopt]"     # or: pip install skillopt
reposkillopt-engine optimize examples/optimize-fake.json --backend skillopt
```

With `--backend skillopt` (or `"backend": "skillopt"` in the config), each round:

- applies the proposed edit with **`skillopt.optimizer.apply_edit`** (our six edit kinds map
  onto SkillOpt's `append` / `insert_after` / `replace` / `delete` ops), and
- makes the **accept/reject decision with `skillopt.evaluation.evaluate_gate`**, which returns
  a real `GateAction` of `accept_new_best` / `accept` / `reject` over a rubric-derived score
  (SkillOpt's `hard` metric = accept only on strict improvement).

The native rubric backend (no-regression PASS/FAIL/HELD, features 003/004) remains the
default and needs no SkillOpt. Integration lives in `reposkillopt_engine/skillopt_backend.py`
(`HAS_SKILLOPT`, `apply_proposal`, `gate_decision`, `rubric_score`).

## Optimize a skill *for one repo* — fully SkillOpt-driven (`optimize-repo`)

Where the `skillopt` backend above uses SkillOpt for two steps (apply + gate),
`reposkillopt_engine/skillopt_native.py` hands the **whole optimization** to SkillOpt's
own ReflACT machinery — **edit generation** (`gradient.run_minibatch_reflect`), **ranking**
(`rank_and_select`), **patch apply** (`apply_patch`), and the **gate** (`evaluate_gate`).

RepoSkillOpt supplies the **reward**, grounded in the real repository (feature 005):

1. a **cached evidence pack** (`evidence.build_evidence_pack`) is built once per run — repo
   structure, manifests, entrypoints, and **line-numbered** key-file contents — and reused for
   every candidate (no per-candidate re-exploration);
2. each candidate skill generates a spec from that pack, scored as
   `reward = 0.5 × rubric + 0.5 × deterministic`, where the **deterministic** half is model-free
   and folds together citation-grounding, quality, and structural coverage —
   `0.4·grounding-checks + 0.3·quality-score + 0.2·analyzed-coverage + 0.1·ER-grounding`
   (ER term dropped + renormalized when the repo has no schema). Because every term but the
   rubric is computed against the real repo, **a spec cannot win by fabricating citations or
   skimping on coverage** — half the reward is non-gameable;
3. the concrete grounding failures (unresolved citations, missing sections, uncited claims) are
   fed into SkillOpt's reflect, so edits target the repo's real gaps.

A run emits **two outputs**: the per-repo `best_skill.md` and the best
`specs/optimized-repository-specification.md`. The **canonical, repo-neutral skill is never touched**.

```sh
# keyless — SkillOpt's edit generator runs on the local Claude CLI (no API key):
python3 -m reposkillopt_engine optimize-repo /path/to/target-repo \
    --skill ../skills/repo-skillopt/SKILL.md --opt-backend claude-code --rollout-provider claude-cli

# with an API key, if you want — pick any SkillOpt API-key backend + provider:
OPENAI_API_KEY=… python3 -m reposkillopt_engine optimize-repo /path/to/target-repo \
    --skill ../skills/repo-skillopt/SKILL.md --opt-backend openai --rollout-provider openai:gpt-4o-mini
```

**Backends are selectable** — keyless or API key:

| Role | flag | keyless | API key |
|---|---|---|---|
| SkillOpt edit generator | `--opt-backend` | `claude-code` (→ SkillOpt `claude_chat`, local CLI) | `openai` / `qwen` / `minimax` |
| Spec generate + score | `--rollout-provider` | `claude-cli` | `anthropic:<model>` / `openai:<model>` |

If SkillOpt's reflect yields no usable patch, the loop falls back to RepoSkillOpt's own
`judge.propose_edit` so a run always makes progress. Outputs (repository-scoped — never the
canonical skill): `<repo>/.reposkillopt/best_skill.md` and
`<repo>/.reposkillopt/specs/optimized-repository-specification.md`.

> The full `optimize-repo` loop makes real model calls; the deterministic parts (backend
> selection, the SkillOpt apply/gate chain, rollout shaping, the evidence pack, and citation
> grounding) are unit-tested, and the live loop is validated by running it.

## Low-context mode — shrink the per-generation evidence pack

Each spec generation sends the cached **evidence pack** to the model. On a big repo that pack is
the dominant context cost (e.g. `eco-standard-wiki`: ~55.6 KB ≈ 14k tokens). For a small context
window, shrink it — the high-signal **structure inventory** (symbols + schema) is kept; the
expendable **file excerpts** are trimmed:

```sh
# preset: ~24k-char pack (≈ 6k tokens) AND default rounds to 1
reposkillopt-engine optimize-repo <repo> --skill … --low-context

# or set an explicit budget
reposkillopt-engine optimize-repo <repo> --skill … --pack-budget 30000
reposkillopt-engine benchmark   --manifest … --mode generate --skill … --low-context
```

Measured on `eco-standard-wiki`: `--low-context` cuts the pack **55.6 KB → 21.1 KB (62% smaller)**
while keeping the deterministic symbol inventory. Scoring stays model-free (zero tokens), and the
completeness step still appends the full symbol listing *after* generation (the model never
transcribes it). Combine with `render --view agent` to keep the *consumed* spec lean too.

## Two improvement loops (both first-class) — `optimize-repo` + `refine-spec`

There are two complementary automatic loops, and they **chain**:

1. **`optimize-repo`** improves the **skill** — each round tries a bounded skill edit and
   regenerates the spec from scratch to measure that skill (the reward). Output: a repo-tuned
   `best_skill.md` + an initial spec.
2. **`refine-spec`** improves the **spec document** — it carries the *prior* spec forward and, each
   round, computes its concrete deterministic gaps (unresolved citations, missing sections,
   malformed citations, ER-grounding) and has the model **revise that same document** to fix exactly
   those. A candidate is kept **only if its score strictly improves** (monotonic — the document
   never regresses); it stops early when there are no gaps left. Scoring + gap-extraction are
   model-free; the only model call is the revise step.

```sh
# chain them: tune the skill, then continuously refine the spec it produced
reposkillopt-engine optimize-repo  ./repo --skill skills/repo-skillopt/SKILL.md --rollout-provider ollama:qwen3.5-coder
reposkillopt-engine refine-spec    ./repo \
    --skill ./repo/.reposkillopt/best_skill.md \
    --spec  ./repo/.reposkillopt/specs/optimized-repository-specification.md \
    --rollout-provider ollama:qwen3.5-coder --rounds 3
#  → writes ./repo/.reposkillopt/specs/refined-repository-specification.md, score climbing each accepted round
```

`refine-spec` reuses the frozen `grounding`/`quality`/`structure`/`completeness` — no metric
definitions change; the completeness step still guarantees 100% symbol coverage every round, so
coverage is never something the model is asked to "fix".

## Section-scoped retrieval — lower *peak* context (opt-in)

`--low-context` shrinks the one pack; **section-scoped** mode goes further by feeding each spec
section only the evidence *that section* needs, retrieved deterministically from the structural
ontology the project already computes (symbols, schema/FKs, manifests, entrypoints) — **no
embeddings, no vector DB**.

```sh
# generate the spec section-by-section; each model call sees only its slice
reposkillopt-engine benchmark --manifest <m.tsv> --mode generate \
    --skill skills/repo-skillopt/SKILL.md --rollout-provider claude-cli --section-scoped --date demo
```

```python
# inspect a slice / the peak-vs-total tradeoff, model-free
from reposkillopt_engine.retrieval import retrieve_section_evidence, build_retrieval_report
build_retrieval_report("/path/to/repo", char_budget=8000)   # baseline / peak / total / fallbacks
```

Measured on `eco-standard-wiki`: peak per-section evidence **7.9 KB (~2.0k tokens)** vs the full
pack **55.6 KB (~13.9k tokens)** — an **86% peak reduction**, deterministic and byte-identical on
re-run. **Honest tradeoff:** total evidence across the 19 sections (~85.7 KB) *exceeds* the single
pack — section-scoped lowers the **peak** context to fit a tight window but can raise **total**
tokens. It is opt-in; the single-pack path stays the default. Spec guarantees are unchanged (the
completeness step still runs once at the end → 100% symbol coverage).

## Audience-specific views (`render`) — one source of truth, derived projections

The Repository Specification is **one** evidence-grounded Markdown document. Rather than
authoring separate human and agent copies (which drift, and would each need grounding), the
engine derives audience-specific views **deterministically** from that single spec:

```sh
# Lean Markdown for feeding a coding agent: drops mermaid diagrams + authoring comments,
# keeps every labeled, cited claim and table (~70% smaller on a diagram-rich spec).
reposkillopt-engine render --spec <repo>/.reposkillopt/specs/repository-specification.md --view agent

# Structured JSON for programmatic upgrade tooling: {meta, sections:[{section, claims:[{label,
# text, citations}]}], evidence_index, counts}.
reposkillopt-engine render --spec … --view structured --out spec.json
```

Both are pure functions of the spec text (no model, no repo access, no drift). The human reads
the full Markdown (tables + flowcharts + ER diagram); the agent gets the lean view or the JSON.
`render.py` is model-free and unit-tested.

## Tests

```sh
cd engine && python3 -m unittest discover -s tests -t .
```

32 stdlib `unittest` tests cover aggregation, the PASS/FAIL/HELD verdict, proposal
application, version bumping, the gate (single + majority + outlier + odd-N), the optimizer
loop (accept+bump, reject-on-regression, skip-repository-scoped), and the **real SkillOpt
backend** (edit-op mapping, `apply_edit`, `evaluate_gate`, and a full `--backend skillopt`
optimize round). The SkillOpt tests skip cleanly when the package is absent; the rest run
with no network and no API key.

## Honest limitations

- Real-provider (LLM) runs are **not exercised in CI here** (no keys, and the held-out repos
  aren't bundled). The deterministic core and loop logic are fully tested via the fake
  provider; the Anthropic/OpenAI adapters are structurally complete but unverified against
  a live endpoint in this repo. **The SkillOpt backend, by contrast, IS exercised** — the
  `skillopt` package is real, installed, and its `apply_edit`/`evaluate_gate` are called by
  passing tests.
- Scoring quality is only as good as the judge model + the rubric prompt; majority mode
  and the held-out-set disjointness rule (feature 004) mitigate single-scorer bias but do
  not eliminate model error.
- This engine automates the *gate*; promoting an accepted candidate into the canonical
  skill (and mirroring to adapters) remains a human/PR step by design.
