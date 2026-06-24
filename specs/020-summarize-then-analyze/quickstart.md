# Quickstart — summarize → generate from summaries

```sh
# MAP: one grounded summary per source file (keyless; ollama:/opencode-cli/claude-cli all work)
reposkillopt-engine summarize <repo> --rollout-provider ollama:qwen3.5-coder
#  → <repo>/.reposkillopt/summaries/<path>.md  (every file; reports coverage + peak/total)

# verify nothing was skipped (portable, no Python):
scripts/coverage-gate.sh <repo> <repo>/.reposkillopt/summaries --files

# REDUCE: build the spec from the complete summary set (bounded peak context)
reposkillopt-engine generate-spec <repo> --skill skills/repo-skillopt/SKILL.md --from-summaries
#  → spec with 100% symbol coverage, resolving repo-relative citations; prints peak-vs-total

# then refine it continuously if you like:
reposkillopt-engine refine-spec <repo> --skill skills/repo-skillopt/SKILL.md --spec <the spec> --rounds 3
```
