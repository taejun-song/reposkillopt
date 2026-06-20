"""Deterministic, model-free checks for the as-is/to-be artifacts (feature 019).

The deterministic half of the validation gate for the `repo-architecture` and `repo-orchestration`
skills. Each check returns a `CheckResult{passed, failures}`; citation resolution reuses
`grounding` (frozen). Stdlib only, reproducible.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .grounding import _resolve, parse_citations


@dataclass
class CheckResult:
    passed: bool
    failures: list = field(default_factory=list)


_CONF = re.compile(r"\b(high|medium|low)\b", re.I)
_SEP = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
_FM = re.compile(r"(?s)\A---\n(.*?)\n---\n")


def _front_matter(text: str) -> dict:
    m = _FM.match(text)
    fm: dict[str, str] = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, _, v = ln.partition(":")
                fm[k.strip()] = v.strip()
    return fm


def _parse_list(s: str) -> list[str]:
    return [x.strip() for x in s.strip().lstrip("[").rstrip("]").split(",") if x.strip()]


def _table_rows(text: str) -> list[list[str]]:
    """Data rows (header + separator dropped) of the first Markdown table."""
    raw = [ln for ln in text.splitlines() if ln.strip().startswith("|") and not _SEP.match(ln)]
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in raw]
    return rows[1:] if rows else []   # drop header


def _section_bullets(text: str, name: str) -> list[str]:
    out, capturing = [], False
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("## "):
            capturing = name.lower() in s.lower()
            continue
        if capturing and s.startswith(("- ", "* ")):
            out.append(ln)
    return out


def _unresolved(repo_path: str, text: str) -> list[str]:
    repo, lc, tx = Path(repo_path), {}, {}
    bad = []
    for c in parse_citations(text):
        ok, reason = _resolve(repo, c, lc, tx)
        if not ok:
            bad.append(f'cited "{c.raw}" — {reason}')
    return bad


# ---- the four checks ----

def check_architecture_view(repo_path: str, text: str) -> CheckResult:
    failures: list[str] = []
    bullets = _section_bullets(text, "Components") + _section_bullets(text, "Dependency")
    if not bullets:
        failures.append("no Components/Dependency bullets found")
    for b in bullets:
        if not parse_citations(b):
            failures.append(f"uncited architecture line: {b.strip()[:70]}")
    failures += _unresolved(repo_path, text)
    return CheckResult(not failures, failures)


def check_impact_analysis(repo_path: str, text: str) -> CheckResult:
    failures: list[str] = []
    rows = _table_rows(text)
    if not rows:
        failures.append("no impact rows found")
    for r in rows:
        joined = " ".join(r)
        if not parse_citations(joined):
            failures.append(f"impact row missing citation: {joined[:70]}")
        if not _CONF.search(joined):
            failures.append(f"impact row missing confidence label: {joined[:70]}")
    failures += _unresolved(repo_path, text)
    return CheckResult(not failures, failures)


def check_adr(text: str) -> CheckResult:
    failures: list[str] = []
    opts = len(_section_bullets(text, "Options"))
    if opts < 2:
        failures.append(f"ADR weighs only {opts} option(s); need ≥2")
    if not re.search(r"^##\s*Decision\b", text, re.M | re.I):
        failures.append("no Decision section")
    if not re.search(r"^##\s*Consequences\b", text, re.M | re.I):
        failures.append("no Consequences section")
    return CheckResult(not failures, failures)


def check_task_ledger(text: str) -> CheckResult:
    failures: list[str] = []
    topo = _parse_list(_front_matter(text).get("topological_order", ""))
    tasks: dict[str, dict] = {}
    for cells in _table_rows(text):
        if len(cells) < 4:
            continue
        tid, goal, acc, deps = cells[0], cells[1], cells[2], cells[3]
        tasks[tid] = {"goal": goal, "acc": acc,
                      "deps": [d.strip() for d in deps.split(",") if d.strip()]}
        if not goal.strip():
            failures.append(f"{tid}: empty goal")
        if not acc.strip():
            failures.append(f"{tid}: empty acceptance")
    if not tasks:
        return CheckResult(False, ["no tasks found in ledger"])
    ids = set(tasks)
    for tid, t in tasks.items():
        for d in t["deps"]:
            if d not in ids:
                failures.append(f"{tid}: depends on unknown id {d}")
    cyc = _find_cycle(tasks)
    if cyc:
        failures.append(f"dependency cycle: {' -> '.join(cyc)}")
    if topo:
        if set(topo) != ids:
            failures.append("topological_order does not cover exactly the task ids")
        pos = {tid: i for i, tid in enumerate(topo)}
        for tid, t in tasks.items():
            for d in t["deps"]:
                if d in pos and tid in pos and pos[d] >= pos[tid]:
                    failures.append(f"topological_order: {d} must precede {tid}")
    return CheckResult(not failures, failures)


def _find_cycle(tasks: dict[str, dict]) -> list[str]:
    WHITE, GREY, BLACK = 0, 1, 2
    color = {t: WHITE for t in tasks}
    stack: list[str] = []

    def dfs(u: str) -> list[str] | None:
        color[u] = GREY
        stack.append(u)
        for v in tasks.get(u, {}).get("deps", []):
            if v not in tasks:
                continue
            if color[v] == GREY:
                return stack[stack.index(v):] + [v]
            if color[v] == WHITE:
                r = dfs(v)
                if r:
                    return r
        stack.pop()
        color[u] = BLACK
        return None

    for t in sorted(tasks):
        if color[t] == WHITE:
            c = dfs(t)
            if c:
                return c
    return []
