"""LLM-facing operations: regenerate a spec, score a spec, propose an edit.

Each builds a prompt (carrying a phase marker the FakeProvider routes on) and parses
the provider's response. Real providers see the full instructions; the fake provider
keys off the marker. JSON is extracted leniently (first balanced object) so models that
wrap output in prose or fences still parse.
"""
from __future__ import annotations

import json

from .providers.base import LLMProvider, ProviderError
from .proposal import Proposal
from .rubric import CHECKS, DIMENSIONS, ScoreCard


def _extract_json(text: str) -> dict:
    start = text.find("{")
    if start < 0:
        raise ProviderError(f"no JSON object in response: {text[:200]!r}")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ProviderError("unbalanced JSON in response")


def generate_spec(provider: LLMProvider, skill_text: str, repo_name: str, repo_content: str) -> str:
    prompt = (
        "REGENERATE_SPEC\n"
        "Apply the following skill to the repository and produce a Repository "
        "Specification (Markdown) with all 19 sections.\n\n"
        f"<skill>\n{skill_text}\n</skill>\n\n"
        f"<repository name=\"{repo_name}\">\n{repo_content}\n</repository>\n"
    )
    return provider.complete(prompt, system="You are a careful repository-understanding agent.")


def score_spec(provider: LLMProvider, spec_text: str, repo_name: str) -> ScoreCard:
    dims = ", ".join(DIMENSIONS)
    checks = ", ".join(CHECKS)
    prompt = (
        "SCORE_SPEC\n"
        "Score this Repository Specification against the rubric. Return ONLY JSON: "
        '{"scores": {<dimension>: 0-3, ...}, "checks": {<check>: "pass"|"fail", ...}}.\n'
        f"Dimensions (all required): {dims}\n"
        f"Checks (all required): {checks}\n\n"
        f"<spec repo=\"{repo_name}\">\n{spec_text}\n</spec>\n"
    )
    raw = provider.complete(prompt, system="You are an exacting evaluation rubric scorer.")
    obj = _extract_json(raw)
    scores = {d: int(obj["scores"][d]) for d in DIMENSIONS}
    checks_out = {c: str(obj["checks"][c]).lower() in ("pass", "true", "1") for c in CHECKS}
    card = ScoreCard(scores=scores, checks=checks_out)
    card.validate()
    return card


def propose_edit(provider: LLMProvider, skill_text: str, guidance: str) -> Proposal:
    prompt = (
        "PROPOSE_EDIT\n"
        "Propose ONE bounded, generalizable edit to improve the skill, or return "
        '{"edit_kind":"NONE"} if no improving edit remains. Return ONLY JSON with keys: '
        "edit_kind (ADD|REPLACE|DELETE|REORDER|SPECIALIZE|GENERALIZE|NONE), target_section, "
        "anchor (exact existing text to locate), payload (new text), expected_effect, "
        "rationale, scope (generic|repository-scoped), bump_level (major|minor|patch).\n\n"
        f"Guidance: {guidance}\n\n"
        f"<skill>\n{skill_text}\n</skill>\n"
    )
    raw = provider.complete(prompt, system="You propose bounded, reviewable skill edits.")
    return Proposal.from_dict(_extract_json(raw))
