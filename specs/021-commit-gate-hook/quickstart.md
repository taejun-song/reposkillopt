# Quickstart: Commit-Time Gate Hook

Forces the gate/refine loop at commit time. Opt-in per repo via the installer; bypassable; reuses the
existing engine and manifest. Keyless.

## 1. Install the hook into a target repo

```sh
# from the RepoSkillOpt checkout
installer/reposkillopt-install --hook --dest /path/to/your/repo
# -> installs <repo>/.git/hooks/pre-commit (chaining any existing one), records a git-hook manifest row

installer/reposkillopt-install --list --dest /path/to/your/repo
# git-hook  0.1.0  .git/hooks/pre-commit  2026-06-26T...Z
```

## 2. A failing artifact is fixed automatically (provider reachable)

```sh
cd /path/to/your/repo
# stage an under-grounded Repository Specification (a [fact] cites a line that doesn't exist)
git add .reposkillopt/specs/repository-specification.md
git commit -m "add repo spec"
# [reposkillopt] gating .reposkillopt/specs/repository-specification.md (coverage, grounding, completeness)
# [reposkillopt] grounding 0.94 < 1.0 — remediating (provider: claude-cli)...
# [reposkillopt]   round 1: passing {completeness} -> {completeness,coverage}  accept
# [reposkillopt]   round 2: passing {...} -> {coverage,grounding,completeness}  accept  CONVERGED
# [reposkillopt] re-staged .reposkillopt/specs/repository-specification.md
# -> commit proceeds; the committed spec passes all three gates
```

## 3. A source-only commit is untouched (fast path)

```sh
git add src/foo.py
git commit -m "tweak foo"
# (no .reposkillopt/ artifact staged -> hook is a no-op: zero gates, zero model calls) — SC-002
```

## 4. Non-convergence or no provider → blocked with a report + bypass

```sh
# no keyless provider reachable, or the artifact can't be made to pass within --rounds:
git commit -m "add spec"
# [reposkillopt] BLOCKED — .reposkillopt/specs/repository-specification.md
# [reposkillopt]   grounding: FAIL (2 citations unresolved)
# [reposkillopt]     - cited "src/x.py:999" — line out of range
# [reposkillopt] no keyless provider reachable (probed: claude-cli, opencode-cli, ollama)
# [reposkillopt] bypass: REPOSKILLOPT_HOOK=off git commit ...   or   git commit --no-verify
# -> commit rejected (exit 1); nothing silently re-staged — SC-003/FR-008/FR-017
```

## 5. Bypass deliberately

```sh
REPOSKILLOPT_HOOK=off git commit -m "wip"   # hook no-op
git commit --no-verify -m "wip"             # git skips the hook entirely
```

## 6. A pre-existing pre-commit hook still runs

```sh
# if the repo already had a linting pre-commit hook, it was chained:
git commit -m "x"
# (the original hook runs first; if it exits non-zero the commit is blocked before gating) — FR-012
```

## 7. Uninstall restores the prior state

```sh
installer/reposkillopt-install --uninstall git-hook --dest /path/to/your/repo
# -> removes our pre-commit hook, restores the chained original exactly, drops the manifest row
installer/reposkillopt-install --list --dest /path/to/your/repo
# (git-hook no longer listed) — SC-006/SC-007
```

## Honesty note

Gate **verdicts** are reproducible (same artifact + repo ⇒ same verdict). The remediation **edits**
are model-driven and therefore nondeterministic — the loop is bounded (default 3 rounds) and never
regresses an already-passing gate, but the exact wording it produces will vary run to run.
