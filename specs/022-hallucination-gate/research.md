# Phase 0 Research: Deterministic Hallucination Catcher

All decisions reuse existing machinery; no new dependency. Decision / Rationale / Alternatives.

## D1 — Claim unit and "checkable tokens" (and the honest boundary of what's catchable)

**Decision**: A *claim* is the text span of a `**[fact]**` marker up to end-of-line (its sentence),
together with the citation(s) inside it (via `grounding.parse_citations`). The **checkable tokens** of
a claim are its *code* tokens: backticked spans, code-like identifiers (D2), string literals, and file
paths. The claim↔cited-code check requires those code tokens to appear in the cited file within the
window (D6). A claim's non-code prose (e.g. the bare word "Redis") is **not** a checkable token.

**Rationale**: The lexically decidable question is "does the cited code contain the code entities the
claim names?" A claim that asserts `` `RedisCache` `` cited at `db.py:42` where line 42 defines
`PostgresStore` is caught (the token is absent from the window). A pure-prose claim "uses Redis" with
no code token is **not** lexically decidable — that is the semantic blind spot (FR-014). Being explicit
here keeps the motivating example honest: the catchable form carries a code token; the prose-only form
is out of scope and neither flagged nor "verified".

**Alternatives considered**: NL entailment / embeddings over the claim — rejected (nondeterministic,
heavyweight dep, violates Principle IV; and would itself hallucinate on weak models).

## D2 — "Code-like identifier" rule (avoids false positives on prose in backticks)

**Decision**: A backticked token is **code-like** if any of: it is a known repo symbol
(`extract_symbols` name); it is snake_case (contains `_`) or CamelCase (internal capital); it is
dotted/attribute (`a.b`) or call-form (`foo()` / `foo(...)`); or it is path-like (`a/b.ext`). A plain
single lowercase/Capitalized dictionary word in backticks (`` `TODO` ``, `` `note` ``, `` `Redis` ``)
is **not** code-like and is exempt from the fabricated-symbol check. The rule is documented and lives
in one place (FR-015).

**Rationale**: Backticks are used for both code and emphasis. Flagging every backticked word would
wreck precision (SC-002). The heuristic captures real identifiers while sparing prose. A product name
like `Redis` is intentionally *not* treated as a repo symbol (it isn't one), so it isn't flagged as
fabricated — correct.

**Alternatives considered**: flag every backtick — rejected (false positives). Maintain a stcopword
list only — rejected (fragile); the structural heuristic generalizes better.

## D3 — Fabricated-symbol check

**Decision**: For each code-like backticked token in the artifact, it must exist as (a) a name in
`extract_symbols(repo)`, OR (b) a whole-word match somewhere in the repo's source files
(`_list_code_files` + read), OR (c) a real file path. Otherwise → `fabricated_symbol` finding. If the
repo has **no** extractable symbols, fall back to (b)/(c) only (edge case) rather than flag everything.

**Rationale**: Catches invented APIs — the top small-context failure. The file-tree fallback (b) keeps
it robust where symbol extraction is thin (regex extractor limitation), trading a little recall for
precision. Word-boundary matching avoids substring false-negatives/positives.

**Alternatives considered**: require symbol-table membership only — rejected (regex extractor misses
methods/fields; would over-flag). Whole-repo substring — rejected (substring false matches).

## D4 — Unlabeled-claim check

**Decision**: On a claim-bearing artifact (kind via `commit_gate.classify_artifact` ∈
{repo_spec, architecture, impact}), a **prose line** (not a heading `#`, table `|`, code fence, or list
of "Symbols not yet analyzed" accounting) that contains a backticked **resolvable** file/symbol but no
R10 label (`**[fact]**|**[inference]**|**[unknown]**|**[human]**`) is flagged `unlabeled_claim`.

**Rationale**: Weak models drop the label discipline; grounding never inspects unlabeled lines, so a
fabricated fact can hide in unlabeled prose. Requiring a label on lines that assert real repo entities
closes that. Scoping to claim-bearing kinds + skipping headings/tables/accounting protects precision.

**Alternatives considered**: flag any unlabeled sentence — rejected (huge false-positive rate on
narrative prose). Only lines with a *citation* — rejected (misses the "names a real symbol, no cite,
no label" case, which is the actual hallucination vector).

## D5 — Unsupported-quantity check

**Decision**: For each number in a `**[fact]**` claim — excluding the citation's own line/range digits,
the code-fence line anchors, and version tokens (`v2`, `3.10` when adjacent to "python"/"v") — the
number must appear within the cited window (D6). Otherwise → `unsupported_quantity`.

**Rationale**: Fabricated specifics ("3 retries", "5 tables") are common and lexically checkable
against the cited span. Excluding structural numbers (citation anchors, versions) preserves precision.

**Alternatives considered**: check numbers anywhere in the file — rejected (weakens the "supported by
the *cited* location" guarantee). Ignore quantities — rejected (loses a real, cheap signal).

## D6 — Window and its default

**Decision**: For a `line` citation, the window is `[line−W, line+W]` with **W = 3** by default
(7 lines). For a `range` citation, the window is the range itself (± a small pad). For a `symbol`
citation, the window is the symbol's definition span if resolvable, else the whole file. `W` is a
documented parameter (FR-015).

**Rationale**: Weak models often cite the right *region* but the wrong exact line; a small window
tolerates that without letting a token "match" from an unrelated part of the file. `W=3` balances
recall (tolerate off-by-a-few) and precision (don't match distant code).

**Alternatives considered**: exact line only — rejected (too brittle; punishes honest off-by-one).
Whole file — rejected (defeats "supported by the *cited location*").

## D7 — Determinism & finding order

**Decision**: `detect_hallucinations` returns findings sorted by `(artifact_line, check_kind, token)`.
Token/symbol sets are built from sorted inputs. No wall-clock, no randomness.

**Rationale**: SC-003 reproducibility — byte-identical output across runs, which the shell-gate parity
and the benchmark both rely on.

## D8 — Shell-gate ↔ engine parity

**Decision**: `scripts/hallucination-gate.sh` implements the same four checks with `grep/sed/awk` and
the same window/code-like rules. Parity is defined as **same clean-vs-flagged verdict and same set of
finding *kinds*** on a curated shared fixture set (one clean + one per class), **not** byte-identical
messages. A parity test runs both on the fixtures and diffs the (verdict, kinds).

**Rationale**: FR-008/SC-004. Two languages won't produce identical prose, but they can agree on the
decision that matters. A curated fixture set makes parity precise and testable; the shell gate is the
zero-install path (CI/reviewer), the engine is the wired-in path.

**Alternatives considered**: byte-identical output — rejected (impractical across sh/Python). Shell
gate as a strict subset — rejected (spec requires agreement on all four kinds on the shared set).

## D9 — Wiring into the refine loop (additive)

**Decision**: `refine.spec_gaps(repo, spec)` additionally appends the catcher's finding strings (one
gap line per finding) so the existing bounded/monotonic loop revises the spec to fix them. Purely
additive — existing gap sources (grounding failures, section/diagram/malformed) are unchanged.

**Rationale**: FR-010 — makes the loop *target* hallucinations with no new loop. Because `spec_gaps`
is already the shared driver for `refine_loop` **and** `commit_gate.remediate`, one edit wires both.

**Alternatives considered**: a separate hallucination-only loop — rejected (duplicates the monotonic
machinery; the existing loop already carries forward + accepts on improvement).

## D10 — New commit gate

**Decision**: Add a `hallucination` gate id to `commit_gate`. `select_gates` includes it for
`repo_spec`, `architecture`, `impact` (claim-bearing kinds). `run_gates` adds a verdict:
`detect_hallucinations(...) == []`. Remediation already consumes `spec_gaps` (now including
hallucination gaps), so a provider-backed commit auto-fixes; a no-provider commit blocks-and-reports
(feature 021 behavior).

**Rationale**: FR-011 — weak-model commits can't land unsupported claims. Reuses the entire 021
enforcement path; only the gate set + one verdict function are added.

**Alternatives considered**: fold into the existing `grounding` gate — rejected (grounding is frozen
and has a different, resolution-only definition; a distinct gate keeps definitions clean).

## D11 — Mutation benchmark

**Decision**: `halluc_bench.py` provides deterministic **mutators**, one per class:
`flip_citation_line` (mis-cite), `rename_cited_symbol` (fabricated symbol), `invent_api`
(fabricated backticked symbol), `strip_label` (unlabeled), `alter_quantity` (unsupported quantity).
Given a clean grounded spec, it applies each mutator (recording the ground-truth injection site),
runs `detect_hallucinations`, and computes **per-class recall** = flagged-injections / injections and
**overall precision** = 1 − (findings on the *clean* spec > 0). It writes a Markdown+YAML
`calibration report` under `rubric/benchmarks/`, and can label the run with a model id to record that
model's failure mix.

**Rationale**: FR-012/FR-013/SC-006 — this is the meta-loop: measure the detector, tune a check,
re-measure. Recall/precision are computed *by construction* against the known injection set, so the
measurement is itself verifiable. Reuses the 007/008 report conventions (Markdown + YAML front matter,
`rubric/benchmarks/`), not `benchmark.py`'s repo-cloning path.

**Alternatives considered**: hand-authored hallucinated fixtures only — kept as the unit-test tier
(deterministic, fast) but insufficient for *measuring* recall across many injections; the mutator
approach scales and quantifies. Model-generated hallucinations — nondeterministic; used only as the
*subject* of a calibration run, never as the ground truth.
