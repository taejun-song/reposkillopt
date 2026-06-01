"""Shared test helpers."""
from __future__ import annotations

from reposkillopt_engine.rubric import CHECKS, DIMENSIONS


def full_scores(base: int = 3, **overrides) -> dict[str, int]:
    s = {d: base for d in DIMENSIONS}
    s.update(overrides)
    return s


def full_checks(all_pass: bool = True, **overrides) -> dict[str, str]:
    c = {ch: ("pass" if all_pass else "fail") for ch in CHECKS}
    for k, v in overrides.items():
        c[k] = "pass" if v else "fail"
    return c


def card(base: int = 3, *, checks_pass: bool = True, **dim_overrides) -> dict:
    """A SCORE_SPEC JSON payload (as the FakeProvider returns)."""
    return {"scores": full_scores(base, **dim_overrides), "checks": full_checks(checks_pass)}
