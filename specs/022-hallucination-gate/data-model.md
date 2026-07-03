# Data Model: Deterministic Hallucination Catcher

In-memory engine entities + one additive report artifact. No new persisted schema; no change to any
existing metric/rubric/reward.

## CheckKind (enum-like string)

One of: `claim_code_mismatch`, `fabricated_symbol`, `unlabeled_claim`, `unsupported_quantity`.

## CheckableToken

A verifiable fragment extracted from a claim.
```
CheckableToken:
  text:  str            # the token, e.g. "create_app", "app/core.py", "3"
  ttype: str            # symbol | path | string | number
```
Code-like rule (D2): `ttype == "symbol"` requires snake_case / CamelCase / dotted / call-form / a known
repo symbol; plain dictionary words are excluded.

## Finding (the catcher's output unit)

```
Finding:
  kind:      CheckKind
  line:      int              # 1-based line in the artifact where the claim sits
  claim:     str              # the claim/sentence text (trimmed)
  token:     str              # the offending token/symbol/quantity ("" for unlabeled_claim)
  citation:  str              # the raw citation involved ("" if none)
  reason:    str              # human-readable explanation
```
**Ordering (D7)**: `detect_hallucinations` returns findings sorted by `(line, kind, token)` —
reproducible (SC-003).

## detect_hallucinations (signature)

```
detect_hallucinations(repo: str, artifact_path: str, text: str, *, window: int = 3) -> list[Finding]
```
- Classifies the artifact (`commit_gate.classify_artifact`) to scope the unlabeled-claim check.
- Runs the four checks; each is a pure function of (repo-on-disk, text). No model, no network.
- `window` is the D6 parameter (FR-015).

## Check semantics (normative)

| Kind | Flags when … | Never flags (precision guards) |
|---|---|---|
| `claim_code_mismatch` | a `[fact]`'s code tokens are absent from the cited file within ±`window` | prose-only claims (no code token); tokens present in window |
| `fabricated_symbol` | a code-like backtick is absent from `extract_symbols` names AND the file tree | non-code-like backticks (`TODO`, product names); real symbols/paths |
| `unlabeled_claim` | a prose line names a **resolvable** file/symbol but carries no R10 label | headings/tables/code-fences/accounting lines; labeled lines; non-claim-bearing artifacts |
| `unsupported_quantity` | a number in a `[fact]` is absent from the cited window | citation line/range digits; version tokens; numbers present in window |

## Mutation (benchmark input)

```
Mutation:
  cls:        MutationClass     # one of the four (+ the citation-flip variant)
  site:       int               # ground-truth artifact line of the injection
  before:     str               # original claim text
  after:      str               # mutated claim text
  expect:     CheckKind         # the finding kind the catcher should produce
```
`MutationClass` ∈ {`flip_citation_line`, `rename_cited_symbol`, `invent_api`, `strip_label`,
`alter_quantity`}. Each mutator is deterministic (given a fixed clean spec it produces a fixed mutant +
site).

## CalibrationReport (benchmark output — Markdown + YAML front matter under `rubric/benchmarks/`)

```
---
kind: hallucination-calibration
model: <id or "fixtures">
window: 3
generated_from: <clean spec path>
---
# Hallucination catcher — calibration

| class                 | injected | flagged | recall |
|-----------------------|----------|---------|--------|
| claim_code_mismatch   | N        | M       | M/N    |
| fabricated_symbol     | …        | …       | …      |
| unlabeled_claim       | …        | …       | …      |
| unsupported_quantity  | …        | …       | …      |

overall precision (clean spec not flagged): <0|1 -> 1.0/0.0>
```
- **recall(class)** = flagged / injected (computed by construction from the known injection set).
- **precision** = `1.0` iff `detect_hallucinations(clean) == []`, else `0.0` (a false positive on the
  known-clean input).
- `model` records whose output was measured (per-model failure mix, FR-013).
