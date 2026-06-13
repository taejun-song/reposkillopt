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
    from .sanitize import sanitize_model_spec
    return sanitize_model_spec(provider.complete(prompt, system="You are a careful repository-understanding agent."))


def generate_section(provider: LLMProvider, skill_text: str, repo_name: str,
                     section_heading: str, section_evidence: str) -> str:
    """Generate ONE spec section from only that section's retrieved evidence (feature 011)."""
    prompt = (
        "REGENERATE_SPEC\n"
        f"Apply the following skill's discipline and write ONLY the `## {section_heading}` section "
        "of a Repository Specification (Markdown): the heading line, then its body, with R10 claim "
        "labels and `file:line` citations grounded strictly in the evidence below. Output that one "
        "section and nothing else.\n\n"
        f"<skill>\n{skill_text}\n</skill>\n\n"
        f"<section>{section_heading}</section>\n"
        f"<repository name=\"{repo_name}\">\n{section_evidence}\n</repository>\n"
    )
    from .sanitize import sanitize_model_spec
    return sanitize_model_spec(provider.complete(prompt, system="You are a careful repository-understanding agent."))


def generate_spec_section_scoped(provider: LLMProvider, skill_text: str, repo_name: str,
                                 repo_path: str, *, char_budget: int = 8_000):
    """Section-scoped generation: each section from only its slice (feature 011, opt-in).

    Returns (spec_text, stats). Peak MODEL-call context is one section's slice, not the whole
    pack — the completeness step is applied by the caller once, after all sections.
    """
    from .retrieval import SECTION_EVIDENCE, retrieve_section_evidence
    parts = [f"# Repository Specification — {repo_name}"]
    peak = total = 0
    fallbacks: list[str] = []
    for i, section in enumerate(SECTION_EVIDENCE, 1):
        se = retrieve_section_evidence(repo_path, section, char_budget=char_budget)
        peak = max(peak, len(se.text))
        total += len(se.text)
        if se.fell_back:
            fallbacks.append(section)
        body = generate_section(provider, skill_text, repo_name, f"{i}. {section}", se.text)
        parts.append(body.strip())
    stats = {"peak_chars": peak, "total_chars": total, "fallbacks": fallbacks,
             "sections": len(SECTION_EVIDENCE)}
    return "\n\n".join(parts) + "\n", stats


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
