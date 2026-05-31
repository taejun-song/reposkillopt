# Quickstart — RepoSkillOpt

**Audience**: An engineer who wants to install the RepoSkillOpt skill into their coding-agent environment and produce an evidence-grounded Repository Specification for a sample legacy repository.

**Estimated time**: ≤ 30 minutes of human time (SC-001).

**Default adapter for this quickstart**: Claude Code (per Phase 0 R2). The same flow works with Codex, OpenCode, or the generic adapter — only the install step differs; the run/feedback/convergence steps are identical because adapters preserve canonical behavior.

---

## Prerequisites

- A Claude Code installation (or any other supported coding-agent harness).
- `git` installed locally.
- Clone of the reference repository at the pinned commit (per Phase 0 R1):
  ```sh
  git clone https://github.com/pallets/click.git ~/work/click
  git -C ~/work/click checkout 8.1.7
  ```
- A clone of this project (RepoSkillOpt) somewhere alongside.

## Step 1 — Install the adapter

Copy the Claude Code adapter into the target environment's skills directory. The target environment is the directory **you will run the agent from** (i.e., `~/work/click` for this walkthrough).

```sh
mkdir -p ~/work/click/.claude/skills/repo-skillopt
cp <reposkillopt-checkout>/adapters/claude-code/SKILL.md \
   ~/work/click/.claude/skills/repo-skillopt/SKILL.md
```

Verify the adapter's `canonical_version` matches the canonical skill:

```sh
grep '^version:' <reposkillopt-checkout>/skills/repo-skillopt/SKILL.md
grep '^canonical_version:' ~/work/click/.claude/skills/repo-skillopt/SKILL.md
# both should print the same semver
```

## Step 2 — Trigger the skill

Open the agent in `~/work/click` and issue any prompt that matches the FR-004 triggers, for example:

> "Help me understand this repository."

The skill activates, executes the FR-012 workflow (triage → identify → inspect → map → trace → produce spec → identify risks), and writes a Repository Specification to:

```
~/work/click/.reposkillopt/specs/repository-specification.md
```

Verify:

```sh
ls ~/work/click/.reposkillopt/specs/
cat ~/work/click/.reposkillopt/specs/repository-specification.md | head -40
```

The file's front matter should carry `spec_id: click-8.1.7`, `target_repository_commit: 8.1.7`, `skill_version:` matching the canonical, and `adapter: claude-code`. All 19 FR-005 sections should be present.

## Step 3 — Read the specification critically

Open the Repository Specification. For every major claim:
- Verify the R10 label is present (`**[fact]**`, `**[inference]**`, `**[unknown]**`, `**[human]**`).
- For `**[fact]**` claims, click through (or `grep`) the cited path and confirm it exists at commit `8.1.7`.
- Note any claim you disagree with — that becomes a Feedback Item in the next step.

## Step 4 — Provide feedback

Suppose the spec calls `click.core.Group` the "primary entrypoint" but you know `click.decorators.group` is the more common user-facing entrypoint. Ask the agent:

> "Correction: `click.decorators.group` is the most common user entrypoint, not `click.core.Group`. Update the Major entrypoints section and re-cite."

The agent will:
1. Create `.reposkillopt/feedback/FB-<date>-001-entrypoint-correction.md` with `type: correction`, `scope: repository-scoped`, `status: open`.
2. Apply the correction to *Major entrypoints* in the spec, marking the new claim `**[fact]**` with a citation to `src/click/decorators.py`.
3. Mark the feedback `status: applied` and increment the spec's `revision` and `revised` fields.
4. Append a row to the spec's *Change log* appendix.

Verify:

```sh
ls ~/work/click/.reposkillopt/feedback/
grep '^status:' ~/work/click/.reposkillopt/feedback/FB-*-entrypoint-correction.md
grep '^revision:' ~/work/click/.reposkillopt/specs/repository-specification.md
```

## Step 5 — (Optional) Propose skill edits from recurring feedback

After several feedback items accumulate (e.g., three different sessions where the agent missed decorator-based entrypoints), run the convergence loop:

> "Summarize recurring feedback in `.reposkillopt/feedback/` and propose any bounded edits to the canonical skill."

The agent will:
1. Identify the recurring pattern across the supporting Feedback Items.
2. Write one or more `SP-<date>-NNN-*.md` files to `.reposkillopt/proposals/`, each with `status: proposed`, `scope: candidate-for-generic`, `edit_kind`, and `review_time_estimate_minutes ≤ 5`.
3. List the supporting feedback ids in each proposal's front matter.

You (the maintainer) then review each proposal and set `status: accepted` or `status: rejected` with a one-paragraph rationale. Accepted proposals are applied to the canonical `skills/repo-skillopt/SKILL.md` (in the RepoSkillOpt project itself), the canonical `version:` is bumped per R8, and a `CHANGELOG.md` row is added. Rejected proposals are preserved on disk for future reference.

## Step 6 — (Optional) Compare adapters

To exercise User Story 4 / SC-005, repeat steps 1–3 against the same `~/work/click` commit with each of the other three adapters (Codex, OpenCode, generic), copying the appropriate file to the appropriate location. Compare the four resulting Repository Specifications. Differences should be near-zero in *what* claims were made and *what* sections were filled; differences in wording and emphasis are expected.

## What you have now

| Path | Content |
|---|---|
| `~/work/click/.reposkillopt/specs/repository-specification.md` | A revision-tracked Repository Specification of Click 8.1.7 with labeled, cited claims. |
| `~/work/click/.reposkillopt/feedback/FB-*.md` | One or more Feedback Items capturing your corrections. |
| `~/work/click/.reposkillopt/rollouts/RL-*.md` | One Rollout Log per session. |
| `~/work/click/.reposkillopt/proposals/SP-*.md` | (Optional) Bounded Skill Edit Proposals for the canonical skill. |

## Next reading

- `skills/repo-skillopt/SKILL.md` — the canonical skill that drove the run.
- `rubric/evaluation-rubric.md` and `rubric/deterministic-checks.md` — how to score what you got.
- `contracts/` (in this spec's directory) — the contracts the spec, adapters, and templates satisfy.
- `adapters/<target>/README.md` — installation notes for each agent harness.

## Limits and expectations

- This skill does **not** claim universal repository understanding (FR-037; AC-10). Sparse, undocumented, or pathologically large repositories will produce sparser specs and more `**[unknown]**` items — by design.
- This skill does **not** replace human code review.
- The skill runs entirely locally; it does not exfiltrate repository contents to external services unless the user has explicitly configured that (FR-035).
