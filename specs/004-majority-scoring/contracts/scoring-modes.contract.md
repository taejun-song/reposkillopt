# Contract — Scoring Modes (`rubric/validation-gate.md` → "## Scoring modes")

**Scope**: The two scoring modes for the validation gate and the rule for choosing between them (FR-010, FR-011).
**Consumers**: The maintainer deciding how to gate a proposal; report authors.

## The two modes

| Mode | Scorers | When |
|---|---|---|
| `single` | One scorer-of-record (feature 003) | Default for low-risk edits. |
| `majority` | N independent scorers, odd ≥3 (this feature) | Required for high-stakes edits (below). |

Every gate report MUST record its `mode`.

## Mode-selection rule (`majority` REQUIRED when any holds)

The methodology MUST state that majority mode is **required** when **at least one** of:

1. The proposal edits the **Operating Principles** section of the canonical skill.
2. The proposal **previously failed** a validation gate (any earlier `FAIL`/`HELD`).
3. The single-scorer-of-record records **low confidence** on any decisive dimension.

Otherwise (`single_eligible`): low-risk clarifying edits MAY use `single` mode.

Scaling: default `N = 3`; the rule MAY require `N = 5` or `7` for the highest-stakes edits (e.g., DELETE of a principle).

## Rules

- `majority` mode does **not** change *what* the gate requires (no-regression + checks + effect); it changes *how scoring is performed* (1 → N + aggregation). Therefore it needs **no canonical-skill or adapter edit** — it is documented under `rubric/` only.
- `single` mode (feature 003) remains valid and unchanged; this contract does not deprecate it.
- The required-when list is a **minimum**; a maintainer MAY always choose `majority` for extra assurance.

## Acceptance checklist

- [ ] `rubric/validation-gate.md` documents both modes and the required-when list (≥ the three triggers).
- [ ] The doc states `mode` MUST be recorded in every report.
- [ ] The doc states majority mode requires no canonical/adapter change (methodology-only).
- [ ] A worked example for each of: a high-stakes edit → majority required; a low-risk edit → single eligible.
