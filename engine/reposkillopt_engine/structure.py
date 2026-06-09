"""Deterministic structural extraction (feature 009): functions/classes + DB schema.

Regex/grep best-effort — NOT a language-server/AST resolver (documented limitation). It is
deterministic and model-free, reusing the evidence pack's code-file selection + exclusions, so
the benchmark can measure: did the spec account for every symbol, and is the ER diagram drawn
from real tables.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .evidence import _list_code_files


@dataclass
class Symbol:
    name: str
    kind: str          # "func" | "class"
    file: str
    line: int


@dataclass
class SchemaEntity:
    name: str
    columns: list[str] = field(default_factory=list)
    fks: list[tuple[str, str]] = field(default_factory=list)   # (column, target entity)
    source: str = ""


# Per-language definition patterns: (compiled regex, kind). Best-effort, line-anchored.
_PATTERNS: dict[str, list[tuple[re.Pattern, str]]] = {
    "py": [(re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)"), "func"),
           (re.compile(r"^\s*class\s+([A-Za-z_]\w*)"), "class")],
    "rb": [(re.compile(r"^\s*def\s+([A-Za-z_][\w?!]*)"), "func"),
           (re.compile(r"^\s*class\s+([A-Za-z_]\w*)"), "class")],
    "go": [(re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)"), "func"),
           (re.compile(r"^\s*type\s+([A-Za-z_]\w*)\s+struct"), "class")],
    "rs": [(re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)"), "func"),
           (re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+([A-Za-z_]\w*)"), "class")],
    "java": [(re.compile(r"^\s*(?:public|private|protected|abstract|final|\s)*(?:class|interface|enum)\s+([A-Za-z_]\w*)"), "class")],
    # JS/TS family — shared
    "ts": [(re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_]\w*)"), "func"),
           (re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_]\w*)"), "class"),
           (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_]\w*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"), "func")],
}
_EXT_LANG = {".py": "py", ".rb": "rb", ".go": "go", ".rs": "rs", ".java": "java", ".kt": "java",
             ".scala": "java", ".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts", ".mjs": "ts"}

_CREATE_TABLE = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`\[]?([A-Za-z_]\w*)', re.I)
_REFERENCES = re.compile(r'REFERENCES\s+["`\[]?([A-Za-z_]\w*)', re.I)
_ORM_CLASS = re.compile(r"^\s*class\s+([A-Za-z_]\w*)\s*\(([^)]*)\)")
_ORM_BASES = ("Base", "Model", "models.Model", "BaseModel", "db.Model", "SQLModel")
_FK_CALL = re.compile(r'(?:ForeignKey|references)\s*\(\s*["\']?([A-Za-z_]\w*)', re.I)


def _read(path: Path) -> list[str]:
    try:
        with path.open(errors="ignore") as fh:
            return fh.read().splitlines()
    except Exception:  # noqa: BLE001
        return []


def extract_symbols(repo_path: str) -> list[Symbol]:
    """Every function/class definition (best-effort, deterministic)."""
    repo = Path(repo_path)
    out: list[Symbol] = []
    for rel in _list_code_files(repo):
        pats = _PATTERNS.get(_EXT_LANG.get(Path(rel).suffix, ""))
        if not pats:
            continue
        for i, ln in enumerate(_read(repo / rel), 1):
            for rx, kind in pats:
                m = rx.match(ln)
                if m:
                    out.append(Symbol(name=m.group(1), kind=kind, file=rel, line=i))
                    break
    return out


def extract_schema(repo_path: str) -> list[SchemaEntity]:
    """Tables/models + columns + foreign keys (SQL DDL, ORM model classes). Deterministic."""
    repo = Path(repo_path)
    entities: dict[str, SchemaEntity] = {}

    def files(*exts: str) -> list[str]:
        out = _list_code_files(repo)
        try:
            out += [str(p.relative_to(repo)) for p in repo.rglob("*.sql")]
        except Exception:  # noqa: BLE001
            pass
        return [f for f in out if f.endswith(exts)]

    # SQL CREATE TABLE
    for rel in {f for f in files(".sql", ".py", ".ts", ".js", ".rb", ".go")}:
        lines = _read(repo / rel)
        for i, ln in enumerate(lines):
            mt = _CREATE_TABLE.search(ln)
            if mt:
                name = mt.group(1)
                ent = entities.setdefault(name, SchemaEntity(name=name, source=f"{rel}:{i+1}"))
                # scan forward to the closing ');' for columns + FK targets
                for ln2 in lines[i:i + 60]:
                    fk = _REFERENCES.search(ln2)
                    if fk:
                        col = ln2.split()[0].strip('"`[],') if ln2.split() else ""
                        ent.fks.append((col, fk.group(1)))
                    if ");" in ln2 or ") ;" in ln2:
                        break
    # ORM model classes
    for rel in {f for f in files(".py", ".ts", ".js", ".rb")}:
        lines = _read(repo / rel)
        for i, ln in enumerate(lines):
            mc = _ORM_CLASS.match(ln)
            if mc and any(b in mc.group(2) for b in _ORM_BASES):
                name = mc.group(1)
                ent = entities.setdefault(name, SchemaEntity(name=name, source=f"{rel}:{i+1}"))
                for ln2 in lines[i + 1:i + 60]:
                    if ln2 and not ln2[0].isspace():
                        break
                    fk = _FK_CALL.search(ln2)
                    if fk:
                        ent.fks.append(("", fk.group(1)))
    return list(entities.values())


_ER_BLOCK = re.compile(r"```mermaid\s*(.*?)```", re.S | re.I)
_ER_ENTITY = re.compile(r"^\s*([A-Za-z_]\w*)\s*\{", re.M)
_ER_REL = re.compile(r"^\s*([A-Za-z_]\w*)\s*[|}o{<>ox.\-]+\s*([A-Za-z_]\w*)\s*:", re.M)


def parse_er_entities(spec_text: str) -> list[str]:
    """Entity names declared in the spec's mermaid erDiagram block(s)."""
    names: set[str] = set()
    for block in _ER_BLOCK.findall(spec_text):
        if "erdiagram" not in block.lower():
            continue
        names.update(_ER_ENTITY.findall(block))
        for a, b in _ER_REL.findall(block):
            names.update({a, b})
    return sorted(names)
