"""Build a cached, bounded *evidence pack* from a real repository (feature 005).

This replaces the ~8 KB `build_repo_digest` proxy for the optimizer's fitness: the
pack carries real structure plus **line-numbered** contents of key files, so the
spec a candidate skill generates can cite `file:line` anchors that actually
resolve (see `grounding.py`). Built once per run and reused across all candidates
and rounds (FR-002). Bounded to a character budget; anything dropped to fit is
recorded in `omitted` (FR-003). Stdlib + git/grep/find only (FR-014).
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

_CODE_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb",
             ".php", ".c", ".cc", ".cpp", ".h", ".hpp", ".kt", ".swift", ".sh", ".scala")
_MANIFESTS = ("pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml",
              "requirements.txt", "composer.json", "Gemfile", "build.gradle", "setup.py")
_ENTRYPOINT_HINTS = ("main.py", "serve.py", "app.py", "cli.py", "__main__.py",
                     "index.ts", "index.js", "server.py", "manage.py", "wsgi.py", "asgi.py")
# language-agnostic-ish markers for entrypoints/routes/CLI registration
_GREP_MARKERS = r"def main\(|if __name__|create_app|FastAPI\(|Flask\(|@app\.|@router\.|" \
                r"add_typer|@click|argparse|express\(|app\.listen|func main\("


@dataclass
class EvidencePack:
    repo_path: str
    repo_name: str
    text: str
    included_files: list[str] = field(default_factory=list)
    omitted: list[str] = field(default_factory=list)
    char_budget: int = 60_000


def _run(repo: Path, cmd: str) -> str:
    try:
        return subprocess.run(["bash", "-c", f"cd {repo!s} && {cmd}"],
                              capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:  # noqa: BLE001 - any tooling failure degrades to empty
        return ""


def _numbered(path: Path, max_lines: int) -> str:
    try:
        lines = path.read_text(errors="ignore").splitlines()
    except Exception:  # noqa: BLE001
        return ""
    shown = lines[:max_lines]
    body = "\n".join(f"{i}: {ln}" for i, ln in enumerate(shown, 1))
    if len(lines) > max_lines:
        body += f"\n… ({len(lines) - max_lines} more lines)"
    return body


def _list_code_files(repo: Path) -> list[str]:
    out = _run(repo, "git ls-files 2>/dev/null")
    files = out.splitlines() if out else [
        str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file()
    ]
    skip = ("/node_modules/", "/.git/", "/.venv/", "/vendor/", "/dist/", "/build/", "/.next/")
    return [f for f in files
            if f.endswith(_CODE_EXT) and not any(s in f"/{f}" for s in skip)]


def _select_key_files(repo: Path, code_files: list[str], max_files: int) -> list[str]:
    """Entrypoint-looking files first, then the largest source files, deduped."""
    selected: list[str] = []
    for f in code_files:
        if Path(f).name in _ENTRYPOINT_HINTS:
            selected.append(f)
    by_size: list[tuple[int, str]] = []
    for f in code_files:
        try:
            with (repo / f).open(errors="ignore") as fh:
                n = sum(1 for _ in fh)
        except Exception:  # noqa: BLE001
            n = 0
        by_size.append((n, f))
    for _, f in sorted(by_size, reverse=True):
        if f not in selected:
            selected.append(f)
        if len(selected) >= max_files:
            break
    return selected[:max_files]


def build_evidence_pack(repo_path: str, *, char_budget: int = 60_000,
                        max_files: int = 25, max_file_lines: int = 400) -> EvidencePack:
    """Assemble a bounded, line-numbered evidence pack for `repo_path`."""
    repo = Path(repo_path)
    pack = EvidencePack(repo_path=str(repo), repo_name=repo.name, text="",
                        char_budget=char_budget)
    parts: list[str] = [f"REPOSITORY: {repo.name}"]

    for r in ("README.md", "README.rst", "README"):
        if (repo / r).exists():
            head = "\n".join((repo / r).read_text(errors="ignore").splitlines()[:40])
            parts.append(f"=== README (head) ===\n{head}")
            break

    for m in _MANIFESTS:
        if (repo / m).exists():
            parts.append(f"=== {m} ===\n" +
                         "\n".join((repo / m).read_text(errors="ignore").splitlines()[:120]))

    parts.append("=== top-level entries ===\n" + _run(repo, "ls -A | head -60"))
    parts.append("=== directory tree (depth 3) ===\n" + _run(
        repo, "find . -maxdepth 3 -type d "
        r"-not -path '*/.*' -not -path '*/node_modules/*' -not -path '*/vendor/*' "
        "| sort | head -80"))
    parts.append("=== file types ===\n" + _run(
        repo, r"git ls-files 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15"))
    parts.append("=== entrypoint/route markers ===\n" + _run(
        repo, f"grep -rnE '{_GREP_MARKERS}' --include='*.py' --include='*.ts' "
        "--include='*.js' --include='*.go' . 2>/dev/null | head -40"))

    # Assemble the fixed sections first (budget permitting), then line-numbered key files.
    base = "\n\n".join(parts)
    if len(base) > char_budget:
        base = base[:char_budget]
        pack.omitted.append("structural-sections (budget)")
    pack.text = base

    code_files = _list_code_files(repo)
    key_files = _select_key_files(repo, code_files, max_files)
    used = len(pack.text)
    for f in key_files:
        block = f"\n\n=== FILE {f} (line-numbered) ===\n{_numbered(repo / f, max_file_lines)}"
        if used + len(block) > char_budget:
            pack.omitted.append(f)
            continue
        pack.text += block
        pack.included_files.append(f)
        used += len(block)

    return pack
