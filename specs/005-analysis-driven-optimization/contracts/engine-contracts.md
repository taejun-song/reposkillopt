# Engine Contracts — 005 Real-Analysis-Driven Optimization

Function-level contracts for the new/changed engine surface. These are the testable
interfaces; signatures are indicative (Python).

## evidence.py (NEW)

```python
def build_evidence_pack(repo_path: str, *, char_budget: int = 60_000,
                        max_files: int = 25, max_file_lines: int = 400) -> EvidencePack: ...
```
- **MUST** include: repo name; README head; manifest contents; top-level + source tree (vendor/.git/node_modules excluded); file-type histogram; **line-numbered** contents of up to `max_files` key files (entrypoints + manifests + largest source files), each capped at `max_file_lines`; targeted grep hits for entrypoint/route/CLI markers.
- **MUST** keep `len(pack.text) ≤ char_budget`; record dropped items in `pack.omitted` (FR-003).
- **MUST NOT** require any tool beyond the stdlib + `git`/`grep`/`find` (FR-014).
- Pure w.r.t. the repo (no writes).

## grounding.py (NEW)

```python
def parse_citations(spec_text: str) -> list[Citation]: ...
def resolve_citation(repo_path: str, c: Citation) -> bool: ...
def ground_spec(repo_path: str, spec_text: str, *, hallucination_threshold: float = 0.9) -> GroundingResult: ...
```
- `parse_citations` extracts `path:line`, `path:start-end`, `path:Symbol`, `path:Symbol:line`, and recognizes `cmd:`/`output:` (excluded from rate). Malformed → `kind="malformed"`.
- `resolve_citation` per R3 rules; **no LLM, no network** (SC-006). Paths resolved under `repo_path`.
- `ground_spec` returns `GroundingResult` with `rate`, the 7 `checks` (citation-bearing ones deterministic; `prior_feedback_addressed`/`adapter_preserves_intent` default True), and concrete `failures`.
- **Contract test (SC-001/FR-008)**: `ground_spec(repo, grounded).rate > ground_spec(repo, fabricated).rate` for specs identical but for citation targets.

## skillopt_native.py (CHANGED)

```python
@dataclass
class RepoTask:
    name: str
    digest: str
    pack: EvidencePack | None = None     # NEW
    baseline: dict[str, int] = ...

def _score_skill(provider, skill_text, task) -> tuple[float, str, ScoreCard, GroundingResult]:
    # generate spec from task.pack.text (fallback task.digest);
    # card = score_spec(...); ground = ground_spec(task's repo, spec);
    # override card.checks with ground.checks;
    # rubric_norm = Σ dim.aggregate/(15*3); det_rate = mean(ground.checks);
    # reward = 0.5*rubric_norm + 0.5*det_rate
    ...
```
- `optimize_repo(...)` **MUST**: build/accept the pack once; set the reflect `fail_reason` from the current spec's `ground.failures` (FR-009); carry `best_spec`/`best_reward` on `NativeResult`.
- Gate, reflect, apply unchanged in ownership (FR-012).

## cli.py (CHANGED)

```python
def cmd_optimize_repo(args) -> int:
    # task = RepoTask(name, digest=build_repo_digest(repo), pack=build_evidence_pack(repo))
    # res = optimize_repo(...)
    # write res.skill_text -> <repo>/.reposkillopt/best_skill.md
    # write res.best_spec  -> <repo>/.reposkillopt/specs/optimized-repository-specification.md
    # print accepted count + best_reward + citation rate
```
- **MUST** write both outputs (FR-010) and never touch the canonical skill (FR-011).
- **MUST** complete and emit even when `accepted == 0` (FR-013).
