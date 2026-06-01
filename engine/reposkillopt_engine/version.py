"""Semantic-version bumping (Keep-a-Changelog + semver, mirroring the project's rule)."""
from __future__ import annotations


def parse(v: str) -> tuple[int, int, int]:
    parts = v.strip().split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"not a semver: {v!r}")
    a, b, c = (int(p) for p in parts)
    return a, b, c


def bump(v: str, level: str) -> str:
    a, b, c = parse(v)
    if level == "major":
        return f"{a + 1}.0.0"
    if level == "minor":
        return f"{a}.{b + 1}.0"
    if level == "patch":
        return f"{a}.{b}.{c + 1}"
    raise ValueError(f"unknown bump level: {level!r}")
