# Quickstart: Deterministic Hallucination Catcher

Model-free lexical claim-support verification. Catches what citation-resolution misses on weak/small-
context models. Reads the repo from disk — no model, no repo-in-context.

## 1. Catch hallucinations in an artifact

```sh
reposkillopt-engine check-hallucination --repo . --file .reposkillopt/specs/repository-specification.md
# .reposkillopt/specs/repository-specification.md:42 fabricated_symbol: `create_sess` not found in repo
# .reposkillopt/specs/repository-specification.md:55 claim_code_mismatch: tokens {RedisCache} absent near db.py:42
# .reposkillopt/specs/repository-specification.md:60 unsupported_quantity: "5" not found near models.py:10
# .reposkillopt/specs/repository-specification.md:71 unlabeled_claim: names `create_app` but carries no [fact]/[inference]/… label
# exit 1
```

A genuinely grounded, fully-labeled spec prints `clean` and exits 0.

## 2. Zero-install gate (CI / pre-commit / reviewer)

```sh
scripts/hallucination-gate.sh . .reposkillopt/specs/repository-specification.md
# same four checks, POSIX sh + grep/awk, no engine needed; exit 0 clean / 1 findings / 2 usage
```

Agrees with the engine on the shared fixtures; passes under `bash` and `dash`.

## 3. The loop and the commit gate now target hallucinations

```sh
# refine drives a hallucinated spec toward clean (findings become gaps it must fix):
reposkillopt-engine refine-spec --repo . --skill skills/repo-skillopt/SKILL.md \
    --spec .reposkillopt/specs/repository-specification.md --rollout-provider claude-cli

# and the feature-021 commit gate blocks/remediates unsupported claims on commit:
git add .reposkillopt/specs/repository-specification.md && git commit -m "spec"
# [reposkillopt] hallucination: FAIL (2 unsupported claims) -> remediating... / or blocked with bypass
```

## 4. Measure and tune the catcher (mutation benchmark)

```sh
reposkillopt-engine halluc-bench --repo . --spec rubric/benchmarks/clean-reference-spec.md --model qwen2.5
# class                 injected  flagged  recall
# claim_code_mismatch   8         8        1.00
# fabricated_symbol     8         8        1.00
# unlabeled_claim       6         6        1.00
# unsupported_quantity  6         6        1.00
# overall precision (clean spec not flagged): 1.0
# wrote rubric/benchmarks/hallucination-calibration-qwen2.5.md
```

The meta-loop: run it, see which class has the lowest recall, tighten that check, re-run. Compare
`--model qwen2.5` vs `--model claude` to see each model's failure mix.

## Honest blind spot

The catcher is **lexical**. A fluent claim that is subtly wrong but shares **no code token** with the
cited code (pure-prose paraphrase) is **not** caught — and the catcher does not pretend it verified it.
That semantic tier is an explicitly deferred, optional model-judge follow-up.
