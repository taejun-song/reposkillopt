"""Business-process workflow view (feature 014) — a derived view over the ontology (012).

Enumerates every BUSINESS entrypoint (HTTP route, scheduled job, CLI command) — no silent
omission — and traces each as a course of actions (entry → called in-repo functions →
side-effect/persistence), rendered as a grounded mermaid `flowchart` per process. The deterministic
skeleton (enumeration + one-hop call following) is the guarantee; the diagram is visual-only and
the authoritative cited steps sit beneath it (the v0.5.0 convention). Best-effort regex/grep
(feature 009 posture); unresolved hops are `[unknown]`, never dropped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import _list_code_files
from .ontology import build_ontology
from .structure import _read, extract_symbols


@dataclass(frozen=True)
class Entrypoint:
    kind: str           # route | job | cli
    name: str
    file: str
    line: int
    handler: str = ""


@dataclass(frozen=True)
class Step:
    kind: str           # entry | call | effect | unknown
    label: str
    file: str
    line: int


@dataclass
class Flow:
    entrypoint: Entrypoint
    steps: list[Step] = field(default_factory=list)


@dataclass
class WorkflowReport:
    entrypoints: list[Entrypoint] = field(default_factory=list)
    flows: list[Flow] = field(default_factory=list)
    counts: dict = field(default_factory=dict)


_DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)|^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)")
_CLI = re.compile(r"@\s*(?:[\w.]+\.)?(?:command|group)\b")
_CALL = re.compile(r"\b([a-z_]\w*)\s*\(")
_EFFECT = re.compile(r"\b(commit|save|insert|update|delete|persist|create|bulk_\w+|execute|write)\b"
                     r"|session\.|INSERT\s+INTO|\.add\(", re.I)


def _handler_after(lines: list[str], i: int) -> str:
    for ln in lines[i - 1:i + 3]:
        m = _DEF.match(ln)
        if m:
            return m.group(1) or m.group(2) or ""
    return ""


def _func_body(lines: list[str], start: int, *, cap: int = 60) -> list[tuple[int, str]]:
    """Lines (1-based no) of the function whose `def` is at index `start` (0-based), bounded."""
    out: list[tuple[int, str]] = []
    base = len(lines[start]) - len(lines[start].lstrip())
    for k in range(start + 1, min(len(lines), start + 1 + cap)):
        ln = lines[k]
        if ln.strip() and (len(ln) - len(ln.lstrip())) <= base:
            break
        out.append((k + 1, ln))
    return out


def enumerate_entrypoints(repo_path: str) -> list[Entrypoint]:
    """Routes + jobs from the ontology; CLI commands scanned. Deterministic, model-free."""
    repo = Path(repo_path)
    onto = build_ontology(str(repo))
    eps: list[Entrypoint] = []
    for e in onto.entities:
        if e.kind in ("route", "job"):
            lines = _read(repo / e.file)
            eps.append(Entrypoint(e.kind, e.name, e.file, e.line,
                                  _handler_after(lines, e.line)))
    # CLI commands (decorator-based) — derived scan, recorded as entrypoints
    for rel in sorted(_list_code_files(repo)):
        if Path(rel).suffix not in (".py", ".ts", ".js"):
            continue
        lines = _read(repo / rel)
        for i, ln in enumerate(lines, 1):
            if _CLI.search(ln):
                h = _handler_after(lines, i)
                eps.append(Entrypoint("cli", h or ln.strip()[:40], rel, i, h))
    return sorted(set(eps), key=lambda e: (e.kind, e.file, e.line, e.name))


def trace_flow(repo_path: str, ep: Entrypoint) -> Flow:
    """One-hop course of actions: entry → called in-repo functions → persistence. Best-effort."""
    repo = Path(repo_path)
    syms = {s.name: s for s in extract_symbols(str(repo))}
    lines = _read(repo / ep.file)
    # find the handler def index
    start = next((k for k, ln in enumerate(lines)
                  if (m := _DEF.match(ln)) and (m.group(1) or m.group(2)) == ep.handler), ep.line - 1)
    steps = [Step("entry", f"entry: {ep.handler or ep.name}", ep.file, ep.line)]
    seen: set[str] = set()
    for no, ln in _func_body(lines, start):
        if _EFFECT.search(ln):
            steps.append(Step("effect", f"persist: {ln.strip()[:48]}", ep.file, no))
        for call in _CALL.findall(ln):
            if call in syms and call != ep.handler and call not in seen:
                seen.add(call)
                s = syms[call]
                steps.append(Step("call", f"call: {call}", s.file, s.line))
                # 1 hop: does the called function persist?
                clines = _read(repo / s.file)
                for no2, ln2 in _func_body(clines, s.line - 1):
                    if _EFFECT.search(ln2):
                        steps.append(Step("effect", f"persist: {ln2.strip()[:48]}", s.file, no2))
                        break
    if len(steps) == 1:
        steps.append(Step("unknown", "handler body not statically resolvable", ep.file, ep.line))
    return Flow(ep, steps)


def analyze_workflows(repo_path: str) -> WorkflowReport:
    eps = enumerate_entrypoints(repo_path)
    counts: dict[str, int] = {}
    for e in eps:
        counts[e.kind] = counts.get(e.kind, 0) + 1
    flows = [trace_flow(repo_path, e) for e in eps]
    return WorkflowReport(entrypoints=eps, flows=flows, counts=counts)


def render_workflow_section(rep: WorkflowReport, *, max_diagrams: int = 25) -> str:
    """## 20. Business workflows — enumeration table (no omission) + a flowchart per process."""
    total = sum(rep.counts.values())
    out = ["## 20. Business workflows", ""]
    out.append(f"**{total} business entrypoints** — "
               + ", ".join(f"{k}: {rep.counts[k]}" for k in sorted(rep.counts)) + ".")
    out += ["", "| Kind | Entrypoint | Evidence | Handler |", "|------|-----------|----------|---------|"]
    for e in rep.entrypoints:
        out.append(f"| {e.kind} | {e.name} | `{e.file}:{e.line}` | `{e.handler or '—'}` |")
    out.append("")
    shown = [f for f in rep.flows if len(f.steps) > 1][:max_diagrams]
    for f in shown:
        out.append(f"### {f.entrypoint.kind}: {f.entrypoint.name}")
        nodes = " --> ".join(f'n{i}["{_lab(s)}"]' for i, s in enumerate(f.steps))
        out += ["", "```mermaid", "flowchart TD", f"  {nodes}", "```", ""]
        for i, s in enumerate(f.steps, 1):
            lab = "**[unknown]**" if s.kind == "unknown" else "**[fact]**"
            out.append(f"{i}. {lab} {s.label} `{s.file}:{s.line}`.")
        out.append("")
    if len(rep.flows) > len(shown):
        out.append(f"_… {len(rep.flows) - len(shown)} more flows in the table above (diagrams capped for size)._")
    return "\n".join(out).rstrip() + "\n"


_SAFE = re.compile(r'[\[\]"`]')


def _lab(s: Step) -> str:
    return _SAFE.sub("", s.label)[:40]
