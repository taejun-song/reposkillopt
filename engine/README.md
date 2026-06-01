# RepoSkillOpt Convergence Engine

An **opt-in, executable** optimizer that runs the RepoSkillOpt validation gate and the
convergence loop in code — the functional counterpart to the Markdown methodology in
`rubric/validation-gate.md` (features 003/004). It is the closest analogue in this project
to microsoft/SkillOpt's `train.py`: **propose a bounded skill edit → run the validation
gate → accept (and bump the version) only if it PASSes → repeat**, gated by the rubric
instead of a benchmark reward, and **without touching model weights**.

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

Open-source / local models are reached through `openai:<model>` by pointing `OPENAI_BASE_URL`
at the local server. Adding a new backend = one small `LLMProvider.complete()` subclass.

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

## Tests

```sh
cd engine && python3 -m unittest discover -s tests -t .
```

26 stdlib `unittest` tests cover aggregation, the PASS/FAIL/HELD verdict, proposal
application, version bumping, the gate (single + majority + outlier + odd-N), and the
optimizer loop (accept+bump, reject-on-regression, skip-repository-scoped) — all with the
deterministic fake provider, so they run with no network and no API key.

## Honest limitations

- Real-provider runs are **not exercised in CI here** (no keys, and the held-out repos
  aren't bundled). The deterministic core and loop logic are fully tested via the fake
  provider; the Anthropic/OpenAI adapters are structurally complete but unverified against
  a live endpoint in this repo.
- Scoring quality is only as good as the judge model + the rubric prompt; majority mode
  and the held-out-set disjointness rule (feature 004) mitigate single-scorer bias but do
  not eliminate model error.
- This engine automates the *gate*; promoting an accepted candidate into the canonical
  skill (and mirroring to adapters) remains a human/PR step by design.
