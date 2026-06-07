# Quickstart — 005 Real-Analysis-Driven Optimization

## Run a per-repo optimization (keyless)

```sh
cd engine
python -m reposkillopt_engine optimize-repo /home/deploy/workspace/eco-standard-wiki \
  --skill ../skills/repo-skillopt/SKILL.md \
  --opt-backend claude-code \
  --rollout-provider claude-cli \
  --rounds 2 --timeout 900
```

Outputs (written under the target repo, never the canonical skill):
- `…/eco-standard-wiki/.reposkillopt/best_skill.md` — the specialized skill
- `…/eco-standard-wiki/.reposkillopt/specs/optimized-repository-specification.md` — the best spec

Console reports: accepted edits / rounds, best combined reward, and the citation-resolution rate.

## Deterministic checks (no LLM, fast)

```python
from reposkillopt_engine.grounding import ground_spec
g = ground_spec("/path/to/repo", open("spec.md").read())
print(g.rate, g.checks, g.failures[:5])
```

## Validate the feature

```sh
cd engine
python -m unittest discover -s tests -t .        # unit: evidence, grounding, combined reward
python -m pyflakes reposkillopt_engine/*.py
```

Acceptance signals:
- `test_grounding`: a grounded spec out-scores a fabricated-citation spec (SC-001/FR-008).
- `test_evidence`: pack built once, bounded, omissions recorded (SC-002/FR-003).
- Live on eco-standard-wiki: ≥1 accepted repo-specialized edit; accepted skill's spec reward ≥ starting (SC-004); citation rate reported (SC-005).
