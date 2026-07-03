"""Deterministic hallucination catcher — a model-free lexical claim-support verifier (feature 022).

Frozen `grounding` proves a citation *resolves*; it does not prove the cited location *supports* the
claim. This module adds four lexical checks that read the repo FROM DISK (never the context window, so
it suits small/weak models and cannot itself hallucinate):

  claim_code_mismatch   — a REAL symbol the claim names is absent from the cited window (mis-cited)
  fabricated_symbol     — a code-like identifier that exists NOWHERE in the repo (invented API)
  unlabeled_claim       — a prose line names a real file/symbol but carries no R10 label
  unsupported_quantity  — a number in a [fact] is absent from the cited window (fabricated specific)

`claim_code_mismatch` (real-but-misplaced) and `fabricated_symbol` (nowhere) are disjoint by
construction. Deterministic/reproducible; stdlib only; reuses grounding (frozen)/structure/evidence;
does NOT modify any of them. Honest blind spot (FR-014): a fluent claim that shares NO code token with
the cited code (pure-prose paraphrase) is NOT caught — and is never implied verified.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .evidence import _list_code_files
from .grounding import parse_citations
from .structure import _read, extract_symbols

CLAIM_CODE_MISMATCH = "claim_code_mismatch"
FABRICATED_SYMBOL = "fabricated_symbol"
UNLABELED_CLAIM = "unlabeled_claim"
UNSUPPORTED_QUANTITY = "unsupported_quantity"

_LABEL_RE = re.compile(r"\*\*\[(?:fact|inference|unknown|human)\]\*\*")
_FACT_RE = re.compile(r"\*\*\[fact\]\*\*")
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_NUM_RE = re.compile(r"\d+")
_CLAIM_BEARING = {"repo_spec", "architecture", "impact"}
DEFAULT_WINDOW = 3


@dataclass
class Finding:
    kind: str
    line: int
    claim: str
    token: str = ""
    citation: str = ""
    reason: str = ""


# ---------------- token rules (D2) ----------------

def _ident_like(tok: str) -> bool:
    """A backticked token that denotes code (not prose). Excludes paths/citations (handled elsewhere)."""
    t = tok.strip()
    if not t or "/" in t or ":" in t or " " in t:
        return False
    if t.endswith(")"):                                   # foo() / foo(x)
        return True
    if re.search(r"[a-z][A-Z]", t):                       # camelCase
        return True
    if "_" in t and re.fullmatch(r"[A-Za-z_]\w*", t):     # snake_case
        return True
    if re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+", t):  # dotted a.b
        return True
    return False


def _bare(tok: str) -> str:
    return tok.strip().rstrip("()").split("(")[0]


# ---------------- repo facts (built once per run) ----------------

class _Repo:
    def __init__(self, repo_path: str):
        self.root = Path(repo_path)
        self.symbols = {s.name for s in extract_symbols(repo_path)}
        self._file_texts: list[str] | None = None
        self._line_cache: dict[str, list[str]] = {}

    def _texts(self) -> list[str]:
        if self._file_texts is None:
            out = []
            for rel in sorted(_list_code_files(self.root)):
                try:
                    out.append((self.root / rel).read_text(errors="ignore"))
                except OSError:
                    pass
            self._file_texts = out
        return self._file_texts

    def symbol_exists(self, token: str) -> bool:
        t = _bare(token)
        if t in self.symbols:
            return True
        pat = re.compile(rf"\b{re.escape(t)}\b")
        return any(pat.search(tx) for tx in self._texts())

    def lines(self, rel: str) -> list[str]:
        if rel not in self._line_cache:
            p = self.root / rel
            self._line_cache[rel] = _read(p) if p.is_file() else []
        return self._line_cache[rel]

    def window_text(self, rel: str, line: int | None, window: int) -> str | None:
        lines = self.lines(rel)
        if not lines:
            return None
        if line is None:
            return "\n".join(lines)
        lo = max(0, line - 1 - window)
        hi = min(len(lines), line + window)
        return "\n".join(lines[lo:hi])


def _windows_for_line(repo: _Repo, text_line: str, window: int) -> list[tuple[str, str]]:
    """(raw citation, window text) for each resolvable citation on a claim line."""
    out = []
    for c in parse_citations(text_line):
        rel = c.path
        ln = c.line if c.kind in ("line", "symbol_line") else (c.start if c.kind == "range" else None)
        wt = repo.window_text(rel, ln, window)
        if wt is not None:
            out.append((c.raw, wt))
    return out


# ---------------- the four checks ----------------

def _check_fact_line(repo: _Repo, lineno: int, line: str, window: int) -> list[Finding]:
    findings: list[Finding] = []
    wins = _windows_for_line(repo, line, window)
    if not wins:
        return findings
    win_all = "\n".join(w for _, w in wins)
    cit0 = wins[0][0]
    # backticked identifiers in the claim (exclude the citation tokens themselves)
    for tok in _BACKTICK_RE.findall(line):
        if not _ident_like(tok):
            continue
        bare = _bare(tok)
        real = repo.symbol_exists(tok)
        present = re.search(rf"\b{re.escape(bare)}\b", win_all) is not None
        if real and not present:
            findings.append(Finding(CLAIM_CODE_MISMATCH, lineno, line.strip(), bare, cit0,
                                    f"symbol `{bare}` not found near {cit0}"))
        # fabricated handled globally in _check_fabricated (over the whole artifact)
    # quantities: numbers in the claim after removing backticked spans (drops citations + code)
    prose = _BACKTICK_RE.sub(" ", line)
    for m in _NUM_RE.finditer(prose):
        n = m.group(0)
        before = prose[m.start() - 1] if m.start() > 0 else " "
        after = prose[m.end()] if m.end() < len(prose) else " "
        if before in ".v" or after == ".":                 # version-ish / decimal — skip
            continue
        if re.search(rf"\b{re.escape(n)}\b", win_all) is None:
            findings.append(Finding(UNSUPPORTED_QUANTITY, lineno, line.strip(), n, cit0,
                                    f'quantity "{n}" not found near {cit0}'))
    return findings


def _check_fabricated(repo: _Repo, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(("#", "|")):
            continue
        for tok in _BACKTICK_RE.findall(line):
            if _ident_like(tok) and not repo.symbol_exists(tok):
                findings.append(Finding(FABRICATED_SYMBOL, i, line.strip(), _bare(tok), "",
                                        f"`{_bare(tok)}` not found in repo (symbols or files)"))
    return findings


def _resolvable_backtick(repo: _Repo, tok: str) -> bool:
    """Token names a real symbol or an existing file path (→ a repo fact)."""
    if "/" in tok or ("." in tok and not tok.endswith(".")):
        return (repo.root / tok.split(":")[0]).is_file()
    return _bare(tok) in repo.symbols


def _check_unlabeled(repo: _Repo, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    in_fence = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith(("#", "|", ">")):
            continue
        if _LABEL_RE.search(line):
            continue
        toks = _BACKTICK_RE.findall(line)
        if not any(_resolvable_backtick(repo, t) for t in toks):
            continue
        prose = _BACKTICK_RE.sub(" ", line)
        words = re.findall(r"[A-Za-z]{2,}", prose)
        if len(words) >= 4:                                 # a real sentence, not an accounting entry
            findings.append(Finding(UNLABELED_CLAIM, i, s, "", "",
                                    "names a real file/symbol but carries no [fact]/[inference]/… label"))
    return findings


# ---------------- entry point ----------------

def detect_hallucinations(repo_path: str, artifact_path: str, text: str, *,
                          window: int = DEFAULT_WINDOW) -> list[Finding]:
    """Deterministic, model-free findings for one artifact. Sorted by (line, kind, token) — reproducible."""
    from .commit_gate import classify_artifact
    repo = _Repo(repo_path)
    lines = text.splitlines()
    findings: list[Finding] = []
    for i, line in enumerate(lines, 1):
        if _FACT_RE.search(line):
            findings += _check_fact_line(repo, i, line, window)
    findings += _check_fabricated(repo, lines)
    if classify_artifact(artifact_path, text) in _CLAIM_BEARING:
        findings += _check_unlabeled(repo, lines)
    findings.sort(key=lambda f: (f.line, f.kind, f.token))
    return findings


def finding_lines(findings: list[Finding]) -> list[str]:
    """Human/gap-consumable one-liners (used by refine.spec_gaps and the CLI)."""
    return [f"{f.kind}: {f.reason}" for f in findings]
