"""Deterministic codebase ontology (feature 012) — the substrate for the workflow (013) and
refactor (014) views.

A model-free knowledge graph of the whole repo: ENTITIES (modules, classes, functions, data
entities, routes, jobs, abstractions) + RELATIONS (imports, inherits, foreign_key,
registers_route, schedules), each pinned to a real `file:line`. Reuses `structure.extract_symbols`
/`extract_schema` and the deterministic file manifest; under-resolvable targets go to
`Ontology.unresolved` (an `[inference]`/`[unknown]` frontier), never a rendered hard edge.

Engine extraction reads files locally (deterministic, portable, costs no model tokens); the
canonical skill directs the *agent* path to `rg`-first scan-don't-read where token cost lives.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import _list_code_files
from .structure import _read, extract_schema, extract_symbols

ENTITY_KINDS = ("module", "class", "function", "data_entity", "route", "job", "abstraction")
RELATION_KINDS = ("imports", "inherits", "foreign_key", "registers_route", "schedules")


@dataclass(frozen=True)
class Entity:
    kind: str
    name: str
    file: str
    line: int


@dataclass(frozen=True)
class Relation:
    kind: str
    src: str
    dst: str
    file: str
    line: int


@dataclass
class Ontology:
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    unresolved: list[Relation] = field(default_factory=list)


# line-anchored detectors (best-effort, like feature 009)
_ROUTE = re.compile(r"""@\s*(?:[\w.]+\.)?(get|post|put|patch|delete|route|websocket)\s*\(\s*["']?([^"',)]*)""", re.I)
_NEST_ROUTE = re.compile(r"""@\s*(Get|Post|Put|Patch|Delete)\s*\(\s*["']?([^"',)]*)""")
_JOB = re.compile(r"(@(?:[\w.]+\.)?(?:task|shared_task|periodic_task|scheduled|repeat_every)\b|add_job\s*\(|CronTrigger|IntervalTrigger|day_of_week\s*=|@cron\b)", re.I)
_DEFNAME = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)|^\s*function\s+(\w+)|^\s*(\w+)\s*[:=]\s*(?:async\s*)?\(")
_IMPORT_PY = re.compile(r"^\s*(?:from\s+([.\w]+)\s+import|import\s+([.\w]+))")
_IMPORT_JS = re.compile(r"""^\s*import\s+.*\bfrom\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]""")
_CLASS_BASES_PY = re.compile(r"^\s*class\s+(\w+)\s*\(([^)]*)\)")
_CLASS_EXT_JS = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)\s+extends\s+(\w+)")

_PY = (".py",)
_JSTS = (".ts", ".tsx", ".js", ".jsx", ".mjs")


def build_ontology(repo_path: str) -> Ontology:
    """Deterministic, model-free ontology of `repo_path`. Same input ⇒ byte-identical to_structured."""
    repo = Path(repo_path)
    files = sorted(_list_code_files(repo))
    onto = Ontology()
    ents: list[Entity] = []
    rels: list[Relation] = []

    # modules
    for rel in files:
        ents.append(Entity("module", rel, rel, 1))

    # classes + functions (reuse the frozen extractor)
    class_names: set[str] = set()
    for s in extract_symbols(str(repo)):
        ents.append(Entity("class" if s.kind == "class" else "function", s.name, s.file, s.line))
        if s.kind == "class":
            class_names.add(s.name)

    # data entities (reuse the frozen schema extractor)
    for e in extract_schema(str(repo)):
        f, _, ln = e.source.partition(":")
        ents.append(Entity("data_entity", e.name, f or "?", int(ln) if ln.isdigit() else 1))
        for col, target in e.fks:
            rels.append(Relation("foreign_key", e.name, target, f or "?",
                                 int(ln) if ln.isdigit() else 1))

    # routes, jobs, imports, inherits — local line scans over the manifest
    for rel in files:
        suf = Path(rel).suffix
        lines = _read(repo / rel)
        for i, ln in enumerate(lines, 1):
            mr = _ROUTE.search(ln) or _NEST_ROUTE.search(ln)
            if mr:
                verb, path = mr.group(1).upper(), (mr.group(2) or "").strip()
                name = f"{verb} {path}".strip()
                ents.append(Entity("route", name, rel, i))
                rels.append(Relation("registers_route", rel, name, rel, i))
            if _JOB.search(ln):
                nm = next((g for g in (_defname_near(lines, i)) if g), None)
                name = nm or ln.strip()[:48]
                ents.append(Entity("job", name, rel, i))
                rels.append(Relation("schedules", rel, name, rel, i))
            if suf in _PY:
                mi = _IMPORT_PY.match(ln)
                if mi:
                    rels.append(Relation("imports", rel, (mi.group(1) or mi.group(2)), rel, i))
                mc = _CLASS_BASES_PY.match(ln)
                if mc:
                    for base in (b.strip() for b in mc.group(2).split(",") if b.strip()):
                        base = base.split(".")[-1].split("[")[0]
                        if base and base[0].isalpha():
                            rels.append(Relation("inherits", mc.group(1), base, rel, i))
            elif suf in _JSTS:
                mj = _IMPORT_JS.match(ln)
                if mj:
                    rels.append(Relation("imports", rel, (mj.group(1) or mj.group(2)), rel, i))
                me = _CLASS_EXT_JS.match(ln)
                if me:
                    rels.append(Relation("inherits", me.group(1), me.group(2), rel, i))

    # abstractions: structural base-class fan-in (≥2 children), vendor-neutral (no allowlist)
    fanin: dict[str, int] = {}
    for r in rels:
        if r.kind == "inherits":
            fanin[r.dst] = fanin.get(r.dst, 0) + 1
    by_name = {e.name: e for e in ents if e.kind == "class"}
    for base, n in fanin.items():
        if n >= 2 and base in by_name:
            c = by_name[base]
            ents.append(Entity("abstraction", base, c.file, c.line))

    # resolve: a relation is "resolved" only when dst binds to a known entity name
    names = {e.name for e in ents} | {Path(e.name).stem for e in ents if e.kind == "module"}
    for r in rels:
        dst_key = r.dst if r.dst in names else r.dst.split(".")[-1]
        (onto.relations if dst_key in names or r.kind == "registers_route" or r.kind == "schedules"
         else onto.unresolved).append(r)

    onto.entities = sorted(set(ents), key=lambda e: (ENTITY_KINDS.index(e.kind) if e.kind in ENTITY_KINDS else 9, e.file, e.line, e.name))
    onto.relations = sorted(set(onto.relations), key=_relkey)
    onto.unresolved = sorted(set(onto.unresolved), key=_relkey)
    return onto


def _defname_near(lines: list[str], i: int) -> tuple:
    for ln in lines[i - 1:i + 3]:   # the marker line + next 2
        m = _DEFNAME.match(ln)
        if m:
            return (m.group(1), m.group(2), m.group(3))
    return ()


def _relkey(r: Relation):
    return (RELATION_KINDS.index(r.kind) if r.kind in RELATION_KINDS else 9, r.src, r.dst, r.file, r.line)


# ---- pure renderers (deterministic) ----

def _counts(onto: Ontology) -> dict[str, int]:
    out: dict[str, int] = {k: 0 for k in ENTITY_KINDS}
    for e in onto.entities:
        out[e.kind] = out.get(e.kind, 0) + 1
    return out


def render_entity_map(onto: Ontology, *, per_kind: int = 8) -> str:
    """Markdown table: per-kind counts + a bounded sample, each pinned to file:line."""
    lines = ["| Kind | Count | Examples (file:line) |", "|------|-------|----------------------|"]
    for kind in ENTITY_KINDS:
        items = [e for e in onto.entities if e.kind == kind]
        if not items:
            continue
        sample = "; ".join(f"`{e.name}` ({e.file}:{e.line})" for e in items[:per_kind])
        if len(items) > per_kind:
            sample += f"; … (+{len(items) - per_kind} more)"
        lines.append(f"| {kind} | {len(items)} | {sample} |")
    return "\n".join(lines)


def render_relationship_graph(onto: Ontology, *, max_edges: int = 40) -> str:
    """Mermaid `graph LR` of resolvable structural edges (inherits/registers_route/schedules),
    deterministically capped."""
    drawn = [r for r in onto.relations if r.kind in ("inherits", "registers_route", "schedules")]
    extra = max(0, len(drawn) - max_edges)
    arrows = {"inherits": "-->|inherits|", "registers_route": "-->|route|", "schedules": "-->|job|"}
    body = [f'    {_node(r.src)} {arrows[r.kind]} {_node(r.dst)}' for r in drawn[:max_edges]]
    if extra:
        body.append(f"    %% … {extra} more edges omitted for size")
    return "```mermaid\ngraph LR\n" + "\n".join(body) + "\n```"


_SAFE = re.compile(r"[^A-Za-z0-9_]")


def _node(name: str) -> str:
    nid = _SAFE.sub("_", name)[:40]
    return f'{nid}["{name[:48]}"]'


def render_er_diagram(onto: Ontology) -> str:
    """erDiagram matching the existing convention so `parse_er_entities` round-trips and
    `compute_structure.diagram_grounding` keeps working unchanged. 'Not applicable' when no schema."""
    data = [e for e in onto.entities if e.kind == "data_entity"]
    if not data:
        return "Not applicable — no persistent schema detected."
    fks = [r for r in onto.relations if r.kind == "foreign_key"]
    out = ["```mermaid", "erDiagram"]
    for r in fks:
        col = r.dst  # label only; relation drawn src -> dst
        out.append(f'    {r.src} ||--o{{ {r.dst} : "{(r.src and col) and "fk"}"')
    for e in data:
        out.append(f"    {e.name} {{")
        out.append(f"        TEXT {e.name.lower()}_id")
        out.append("    }")
    out.append("```")
    return "\n".join(out)


def to_structured(onto: Ontology) -> dict:
    def rl(rs):
        return [{"kind": r.kind, "src": r.src, "dst": r.dst, "file": r.file, "line": r.line} for r in rs]
    return {
        "counts": _counts(onto),
        "entities": [{"kind": e.kind, "name": e.name, "file": e.file, "line": e.line} for e in onto.entities],
        "relations": rl(onto.relations),
        "unresolved": rl(onto.unresolved),
    }
