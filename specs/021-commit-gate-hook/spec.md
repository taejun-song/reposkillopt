# Feature Specification: Commit-Time Gate Hook (Auto-Remediating Pre-Commit Enforcement)

**Feature Branch**: `021-commit-gate-hook`
**Created**: 2026-06-26
**Status**: Draft
**Input**: User description: "A portable git pre-commit hook, installed into target repos by the CLI installer, that auto-remediates RepoSkillOpt artifacts until they pass the gates — making the loop forced systematically so ungated artifacts can never land."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A failing artifact is fixed automatically before the commit lands (Priority: P1)

A developer (or a coding agent) has regenerated a Repository Specification (or other `.reposkillopt/` artifact) and stages it for commit. The artifact is under-grounded (some claims don't resolve) or incomplete (a symbol is unaccounted for). When they run `git commit`, the hook detects the staged artifact, finds the failing gate, runs the bounded remediation loop to fix it, re-stages the corrected artifact, and the commit proceeds — now with every gate passing. The developer never has to remember to run the loop; the commit *is* the loop's convergence condition.

**Why this priority**: This is the entire reason for the feature. Without automatic remediation at commit time, the gates remain opt-in and ungated artifacts continue to land. It is the smallest slice that delivers the core promise ("the loop is forced systematically").

**Independent Test**: On a small repo with a deliberately under-grounded staged spec and a reachable keyless provider, run `git commit`; verify the committed artifact passes all four gates, the corrected content was the thing committed (re-staged), and the run reports how many remediation rounds it took.

**Acceptance Scenarios**:

1. **Given** a staged `.reposkillopt/` artifact failing one gate and a reachable provider, **When** `git commit` runs, **Then** the hook remediates within the round budget, re-stages the fixed artifact, exits 0, and the commit contains the passing artifact.
2. **Given** a staged artifact that already passes every gate, **When** `git commit` runs, **Then** the hook makes no model calls, changes nothing, and the commit proceeds unchanged.
3. **Given** a staged artifact failing a gate that cannot be made to pass within the round budget, **When** `git commit` runs, **Then** the commit is rejected with a precise per-gate failure report and bypass instructions, and nothing is silently re-staged.

---

### User Story 2 - The hook never traps the developer (Priority: P1)

A developer is offline, has no keyless provider configured, or simply wants to commit work-in-progress without remediation. The hook must degrade gracefully and always leave an escape path: it must not hang waiting on a model, and the developer can always bypass enforcement deliberately.

**Why this priority**: An enforcement hook that can wedge a commit (hang on an unreachable model, or block with no way out) is worse than no hook. Graceful degradation and a bypass are non-negotiable for adoption and are co-equal P1 with the core behavior.

**Independent Test**: Remove/disable every provider; stage a failing artifact; run `git commit`. Verify the hook does not hang, falls back to running the gates and reporting failures (block-and-report), and exits non-zero promptly. Separately verify that the documented env toggle and git's native bypass both let the same commit through.

**Acceptance Scenarios**:

1. **Given** no reachable keyless provider, **When** `git commit` runs on a failing artifact, **Then** the hook runs the deterministic gates, prints the failures, exits non-zero promptly (no hang), and prints how to bypass.
2. **Given** the documented disable toggle is set, **When** `git commit` runs, **Then** the hook is a no-op and the commit proceeds regardless of artifact state.
3. **Given** the developer uses git's native verify-bypass, **When** they commit, **Then** the hook does not run and the commit proceeds.

---

### User Story 3 - The hook coexists with the repo's existing pre-commit hook (Priority: P2)

A target repo already has its own `pre-commit` hook (linters, formatters, secret scanners). Installing RepoSkillOpt's enforcement must not silently disable or destroy that hook. The existing hook continues to run and its failure still blocks the commit; uninstalling RepoSkillOpt restores the repo to exactly its prior hook state.

**Why this priority**: Real repos already use pre-commit hooks. Clobbering them would be data loss and would block adoption, but it is a layer on top of the core enforcement (P1) rather than the core itself.

**Independent Test**: In a repo with a pre-existing pre-commit hook that exits non-zero, install the RepoSkillOpt hook, attempt a commit, and verify the pre-existing hook still runs and still blocks. Then uninstall and verify the original hook is restored byte-for-byte and is the active hook.

**Acceptance Scenarios**:

1. **Given** a pre-existing `pre-commit` hook, **When** the RepoSkillOpt hook is installed and a commit runs, **Then** both run and a non-zero exit from either blocks the commit.
2. **Given** the RepoSkillOpt hook was installed over a pre-existing hook, **When** it is uninstalled, **Then** the pre-existing hook is restored exactly and is the active `pre-commit` hook.

---

### User Story 4 - Install, list, and uninstall the hook through the existing installer (Priority: P2)

An operator uses the existing RepoSkillOpt CLI installer to add the enforcement hook to a target repo, to see that it is installed, and to remove it. The install is recorded in the per-repo install manifest so the lifecycle (list / upgrade / uninstall) is driven by the same mechanism as every other installed component.

**Why this priority**: Consistent lifecycle management is what makes the hook safe to adopt and remove; it reuses the established installer and manifest rather than introducing a separate mechanism.

**Independent Test**: Install into a fresh target repo; verify `list` shows the hook and the manifest records it; uninstall; verify the manifest entry and the installed hook are gone.

**Acceptance Scenarios**:

1. **Given** a target repo, **When** the operator installs the hook, **Then** the manifest records exactly the files/paths installed and `list` reports the hook as present.
2. **Given** an installed hook, **When** the operator uninstalls, **Then** every recorded path is removed (and any chained hook restored) and `list` no longer reports it.

---

### Edge Cases

- **A commit touches only source files, no `.reposkillopt/` artifact** → the hook is a no-op; the commit proceeds without running any gate or model call.
- **A commit stages multiple failing artifacts** → each affected artifact is gated/remediated; the commit proceeds only if all converge, otherwise it is rejected with a per-artifact, per-gate report.
- **A remediation round makes an already-passing gate fail (regression)** → the round is rejected; the loop keeps the last artifact whose passing-gate set was not reduced, and never commits a regression.
- **The remediation loop stops improving before all gates pass** → the loop halts at the no-improvement point (does not burn the full budget pointlessly) and the commit is rejected with the residual failures.
- **The provider is reachable but returns empty/garbled output for a round** → that round is treated as no-improvement (the prior artifact is carried forward); a persistent failure ends in block-and-report, never a hang or a corrupted artifact.
- **An artifact is staged but its target repo source has no extractable symbols** → coverage/completeness gates report trivially (nothing to cover) rather than erroring; the commit is not blocked by an empty-repo edge.
- **A staged artifact was partially staged (working-tree copy differs from index)** → gating and remediation operate on the staged (index) content, and only the staged content is what gets re-staged, so the commit reflects what was actually gated.
- **The hook is invoked outside a git work tree or during a merge/rebase with no `.reposkillopt/` changes** → no-op, commit proceeds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a pre-commit hook that, on each commit, determines whether any staged change lies under the repo's `.reposkillopt/` artifact tree and does nothing (no gates, no model calls) when none do.
- **FR-002**: For each staged artifact under `.reposkillopt/`, the system MUST run the four gates — file/symbol coverage (no silent omission), citation grounding (every claim-of-fact resolves to a real repo-relative location), specification completeness (full symbol coverage), and artifact validity (architecture/impact/decision-record/task-ledger structural checks including dependency-graph acyclicity).
- **FR-003**: When every applicable gate already passes, the system MUST allow the commit to proceed without making any model call or modifying any file.
- **FR-004**: When any gate fails, the system MUST run a bounded remediation loop that carries the prior artifact forward, attempts to fix the failing gate(s), and re-checks all gates after each round.
- **FR-005**: The remediation loop MUST terminate — it stops when all gates pass, OR when a fixed maximum number of rounds is reached, OR when a round yields no improvement; it MUST NOT loop unboundedly.
- **FR-006**: The remediation loop MUST be monotonic with respect to passing gates: a round whose result reduces the set of passing gates (a regression) MUST be rejected, and the artifact carried forward MUST never have fewer gates passing than a previously reached state.
- **FR-007**: On convergence (all gates pass), the system MUST re-stage the remediated artifact content so the commit contains exactly the gated, passing version, and MUST allow the commit to proceed.
- **FR-008**: On non-convergence, the system MUST reject the commit with a precise, per-artifact and per-gate failure report and MUST NOT silently alter or re-stage the artifact.
- **FR-009**: The system MUST use only keyless model providers for remediation, selected by the same mechanism the rest of the engine uses, and MUST NOT prompt for or require any secret/API key during a commit.
- **FR-010**: If no keyless provider is reachable, the system MUST degrade to block-and-report (run the deterministic gates, print failures, exit non-zero) without hanging, and MUST tell the developer how to bypass.
- **FR-011**: The system MUST provide a documented environment toggle that disables enforcement (making the hook a no-op), and MUST honor git's native per-commit verify-bypass; neither path may be silently overridden.
- **FR-012**: The hook MUST chain (invoke and preserve the exit status of) any pre-existing pre-commit hook it was installed alongside, so the pre-existing hook still runs and its failure still blocks the commit.
- **FR-013**: The existing CLI installer MUST be able to install, list, upgrade, and uninstall the hook, recording the install in the per-repo install manifest in its existing format so that uninstall removes exactly what was installed and restores any chained hook.
- **FR-014**: The system MUST gate and remediate on the staged (index) content of each artifact, and only the staged content is what is committed, so the committed artifact is exactly what was gated.
- **FR-015**: The system MUST NOT change any gate definition, metric definition, rubric, or reward; it composes the existing checks and the existing remediation loop without altering them.
- **FR-016**: The system MUST document plainly that remediation is model-driven and therefore nondeterministic in its edits, while the deterministic gates themselves are reproducible (same artifact + same repo → same verdict).
- **FR-017**: The remediation report MUST be honest about residual state on failure — it states which gates still fail, on which artifact, and how many rounds were spent — rather than implying success.

### Key Entities *(include if feature involves data)*

- **Staged artifact**: A `.reposkillopt/` file present in the commit's staged set (e.g., a Repository Specification, a feedback record, a proposal). The unit that is gated and, if needed, remediated.
- **Gate**: One of the four deterministic checks (coverage, grounding, completeness, artifact-validity). Each yields a pass/fail verdict plus a human-readable reason; reproducible for a given artifact+repo.
- **Remediation round**: One iteration of the bounded loop — input artifact in, model-revised artifact out, all gates re-evaluated. Characterized by its before/after passing-gate sets (for the monotonic guarantee) and an improvement/no-improvement outcome.
- **Hook record (manifest entry)**: The line(s) in the per-repo install manifest recording the installed hook and any chained-hook backup, enabling exact uninstall/restore.
- **Provider availability**: Whether a keyless provider is reachable at commit time; determines remediate-vs-block-and-report.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the hook installed and a provider reachable, committing a deliberately under-grounded artifact results in a committed artifact that passes all four gates in 100% of convergent runs (the committed content is the remediated, passing content).
- **SC-002**: A commit whose staged changes do not touch `.reposkillopt/` artifacts incurs zero gate executions and zero model calls (source-only commits are untouched).
- **SC-003**: When no provider is reachable, the hook returns a block-and-report result without hanging (it completes in deterministic-gate time, with no open-ended wait on a model).
- **SC-004**: The remediation loop always terminates within the configured round budget; no input produces an unbounded loop, and a round that does not improve the passing-gate set ends the loop.
- **SC-005**: No accepted remediation ever reduces the set of passing gates relative to the artifact carried into that round (zero regressions across the test suite).
- **SC-006**: Installing the hook over a pre-existing pre-commit hook preserves that hook's behavior (it still runs and still blocks on failure), and uninstalling restores the pre-existing hook exactly; verified in 100% of install/uninstall cycles in the test suite.
- **SC-007**: After uninstall, the manifest contains no entry for the hook and no hook file installed by the feature remains (exact-removal verified against the manifest record).
- **SC-008**: All deterministic behaviors (gate selection, bound/termination, monotonic non-regression, re-stage accounting, no-provider fallback, hook-chaining/exit-status) are covered by tests that pass under both `bash` and `dash` for the hook and under the engine's standard test runner for the entrypoint.

## Assumptions

- **Reuse, don't re-implement**: The four gates already exist (file/symbol coverage verifier, citation grounding, specification completeness, artifact-validity checks) and the bounded monotonic remediation loop already exists; this feature composes them and does not redefine any of them.
- **Artifact location**: Gated artifacts live under the target repo's `.reposkillopt/` tree (specs/feedback/proposals); the hook scope is exactly that tree.
- **Keyless-only at commit time**: Only keyless providers are used during a commit, to avoid prompting for secrets mid-commit; API-key providers are intentionally out of the hook path.
- **Round budget default**: A small fixed default round budget applies when not otherwise configured, chosen so a normal commit remediates quickly; the exact default is a planning decision.
- **Installer & manifest reuse**: The existing CLI installer and the existing per-repo manifest format are reused unchanged for the hook's lifecycle; no new manifest schema is introduced.
- **Scope boundary**: This is pre-commit only. Pre-push hooks, CI gating, a server/daemon, and changes to gate/metric/rubric/reward definitions are explicitly out of scope. The opt-in manual loop commands remain; this enforces them at commit time, it does not replace them.
- **Determinism honesty**: Gate verdicts are reproducible; model-driven remediation edits are not, and this is documented rather than hidden.
