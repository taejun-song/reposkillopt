"""Feature 021 — commit-time gate hook (TDD, written before implementation).

Covers the DETERMINISTIC core: artifact classification + gate selection, gate evaluation, the
bounded gate-set-monotonic remediation loop (never regresses a passing gate; terminates), the
no-provider block-and-report fallback, and re-stage accounting. The live model remediation is
validated separately (a real keyless provider on a small repo).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from reposkillopt_engine.completeness import ensure_symbol_completeness
from reposkillopt_engine.grounding import REQUIRED_SECTIONS
from reposkillopt_engine import commit_gate as cg


# ---------- fixtures ----------

def _repo():
    """A tiny repo where every source file defines a symbol (so file- and symbol-coverage agree)."""
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass Service:\n    pass\n")
    return d


def _full_spec(cite="`pkg/app.py:1`", extra=""):
    body = "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)
    return body + f"\n**[fact]** the factory {cite}\n" + extra


def _passing_repo_spec(repo):
    """A repo spec that passes coverage + grounding + completeness."""
    return ensure_symbol_completeness(_full_spec(), repo)


# ---------- provider stubs (deterministic) ----------

class _ConvergeStub:
    """revise() always returns a fully-passing repo spec (after the deterministic completeness step)."""
    def __init__(self, repo):
        self._fixed = _full_spec()      # grounded + all sections; completeness added by the loop
        self.calls = 0
    def complete(self, prompt, *, system=None):
        self.calls += 1
        return self._fixed


class _ArchRegressStub:
    """revise() returns an architecture artifact with a BAD citation — drops the grounding gate that
    was passing in the start (so the round must be rejected as a regression)."""
    def __init__(self):
        self.calls = 0
    def complete(self, prompt, *, system=None):
        self.calls += 1
        return "## Architecture\n\n**[fact]** entry `pkg/app.py:999`\n"   # bad cite → grounding fails


class _NoProgressStub:
    """revise() echoes the same still-failing spec every round (no improvement)."""
    def __init__(self):
        self.calls = 0
    def complete(self, prompt, *, system=None):
        self.calls += 1
        return _full_spec(cite="`pkg/app.py:999`")     # still ungrounded


class _ExplodeStub:
    """Any model call is a test failure (asserts the no-model paths)."""
    def complete(self, prompt, *, system=None):
        raise AssertionError("model must NOT be called on this path")


# ---------- T002 ----------

class TestClassifyAndSelect(unittest.TestCase):
    def test_classify_kinds(self):
        self.assertEqual(cg.classify_artifact("specs/repository-specification.md", _full_spec()), cg.REPO_SPEC)
        self.assertEqual(cg.classify_artifact("x/architecture-view.md", "## Architecture\n- comp `a:1`"), cg.ARCHITECTURE)
        self.assertEqual(cg.classify_artifact("x/impact-report.md", "| a | high | `f:1` |"), cg.IMPACT)
        self.assertEqual(cg.classify_artifact("x/adr-001.md", "## Decision\nx\n## Consequences\ny"), cg.ADR)
        self.assertEqual(cg.classify_artifact("x/task-ledger.md", "---\ntopological_order: [T1]\n---\n"), cg.LEDGER)
        self.assertEqual(cg.classify_artifact("feedback/note.md", "a plain note"), cg.OTHER)

    def test_select_gates(self):
        self.assertEqual(set(cg.select_gates(cg.REPO_SPEC)), {cg.COVERAGE, cg.GROUNDING, cg.COMPLETENESS})
        self.assertIn(cg.CHECK_ARTIFACT, cg.select_gates(cg.ARCHITECTURE))
        self.assertIn(cg.GROUNDING, cg.select_gates(cg.ARCHITECTURE))
        self.assertEqual(cg.select_gates(cg.ADR), [cg.CHECK_ARTIFACT])
        self.assertEqual(cg.select_gates(cg.OTHER), [cg.GROUNDING])

    def test_reproducible(self):
        a = cg.classify_artifact("specs/repository-specification.md", _full_spec())
        b = cg.classify_artifact("specs/repository-specification.md", _full_spec())
        self.assertEqual(a, b)


# ---------- T003 ----------

class TestRunGates(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_passing_repo_spec_all_pass(self):
        rep = cg.run_gates(self.repo, "specs/repository-specification.md", _passing_repo_spec(self.repo))
        self.assertTrue(rep.all_pass, rep.verdicts)
        self.assertEqual(rep.passing, set(cg.select_gates(cg.REPO_SPEC)))

    def test_undergrounded_fails_grounding_only(self):
        spec = ensure_symbol_completeness(_full_spec(cite="`pkg/app.py:999`"), self.repo)
        rep = cg.run_gates(self.repo, "specs/repository-specification.md", spec)
        self.assertFalse(rep.all_pass)
        self.assertNotIn(cg.GROUNDING, rep.passing)
        self.assertIn(cg.COVERAGE, rep.passing)        # path still mentioned
        self.assertIn(cg.COMPLETENESS, rep.passing)


# ---------- T004 ----------

class TestMonotonicBoundedLoop(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.start = ensure_symbol_completeness(_full_spec(cite="`pkg/app.py:999`"), self.repo)  # grounding fails

    def test_converges_and_passing_is_non_decreasing(self):
        res = cg.remediate(_ConvergeStub(self.repo), "# skill", self.repo, "repo",
                           "specs/repository-specification.md", self.start, rounds=3)
        self.assertTrue(res.converged)
        self.assertTrue(res.changed)
        prev = None
        for r in res.rounds:
            self.assertTrue(r.after >= r.before)       # never regressed an accepted carry
            if prev is not None:
                self.assertTrue(r.before >= prev)      # carried passing set non-decreasing
            if r.accepted:
                prev = r.after

    def test_regression_is_rejected(self):
        # start: an architecture artifact where grounding PASSES but check-artifact FAILS (no
        # Components/Dependency bullets). The stub's candidate breaks grounding → its passing set is
        # not a superset → the round must be rejected and the start carried forward unchanged.
        start = "## Architecture\n\nOverview prose.\n\n**[fact]** the app `pkg/app.py:1`\n"
        rep0 = cg.run_gates(self.repo, "arch-view.md", start)
        self.assertIn(cg.GROUNDING, rep0.passing)
        self.assertNotIn(cg.CHECK_ARTIFACT, rep0.passing)
        res = cg.remediate(_ArchRegressStub(), "# skill", self.repo, "repo",
                           "arch-view.md", start, rounds=3)
        self.assertFalse(res.converged)
        self.assertTrue(any(r.regressed and not r.accepted for r in res.rounds))
        self.assertEqual(res.final_text, start)        # the regressing candidate was never carried

    def test_no_progress_stops_within_budget(self):
        res = cg.remediate(_NoProgressStub(), "# skill", self.repo, "repo",
                           "specs/repository-specification.md", self.start, rounds=5)
        self.assertFalse(res.converged)
        self.assertLessEqual(len(res.rounds), 5)
        self.assertGreaterEqual(len(res.rounds), 1)


# ---------- T005 ----------

class TestProviderFallback(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_auto_returns_none_when_nothing_available(self):
        orig = shutil.which
        try:
            shutil.which = lambda *a, **k: None
            avail = cg.detect_keyless_provider("auto", timeout=0.05, _ollama_up=lambda t: False)
        finally:
            shutil.which = orig
        self.assertIsNone(avail.provider)

    def test_rejects_api_key_provider(self):
        with self.assertRaises(ValueError):
            cg.detect_keyless_provider("anthropic:claude-x")

    def test_no_provider_blocks_without_model_call(self):
        spec = ensure_symbol_completeness(_full_spec(cite="`pkg/app.py:999`"), self.repo)
        d = os.path.join(self.repo, ".reposkillopt", "specs")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "repository-specification.md"), "w").write(spec)
        out = cg.gate_commit(self.repo, "# skill",
                             [".reposkillopt/specs/repository-specification.md"],
                             provider=None, rounds=3, restage=False)
        self.assertTrue(out.degraded)
        self.assertEqual(out.exit_code, 1)
        self.assertEqual(out.restaged, [])


# ---------- T006 ----------

@unittest.skipUnless(shutil.which("git"), "git required")
class TestRestageAccounting(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.repo, check=True)
        self.rel = ".reposkillopt/specs/repository-specification.md"
        os.makedirs(os.path.join(self.repo, ".reposkillopt", "specs"))

    def _stage(self, text):
        p = os.path.join(self.repo, self.rel)
        open(p, "w").write(text)
        subprocess.run(["git", "add", self.rel], cwd=self.repo, check=True)

    def test_already_passing_no_restage_no_model(self):
        self._stage(_passing_repo_spec(self.repo))
        stub = _ExplodeStub()
        out = cg.gate_commit(self.repo, "# skill", [self.rel], provider=stub, rounds=3, restage=True)
        self.assertEqual(out.exit_code, 0)
        self.assertEqual(out.restaged, [])

    def test_converged_artifact_is_restaged_with_gated_content(self):
        self._stage(ensure_symbol_completeness(_full_spec(cite="`pkg/app.py:999`"), self.repo))
        out = cg.gate_commit(self.repo, "# skill", [self.rel],
                             provider=_ConvergeStub(self.repo), rounds=3, restage=True)
        self.assertEqual(out.exit_code, 0)
        self.assertIn(self.rel, out.restaged)
        # the re-staged (index) content is exactly what passed the gates
        idx = subprocess.run(["git", "show", f":{self.rel}"], cwd=self.repo,
                             capture_output=True, text=True).stdout
        self.assertTrue(cg.run_gates(self.repo, self.rel, idx).all_pass)


# ---------- T009 ----------

class TestGateCommitCli(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.d = os.path.join(self.repo, ".reposkillopt", "specs")
        os.makedirs(self.d)
        self.rel = ".reposkillopt/specs/repository-specification.md"

    def _write(self, text):
        open(os.path.join(self.repo, self.rel), "w").write(text)

    def test_clean_artifact_exits_zero_without_provider(self):
        # an already-passing artifact needs no provider, so PATH state is irrelevant
        self._write(_passing_repo_spec(self.repo))
        from reposkillopt_engine.cli import main
        rc = main(["gate-commit", "--repo", self.repo, "--staged", self.rel, "--no-restage"])
        self.assertEqual(rc, 0)

    def test_api_key_provider_rejected_exit_2(self):
        self._write(ensure_symbol_completeness(_full_spec(cite="`pkg/app.py:999`"), self.repo))
        from reposkillopt_engine.cli import main
        rc = main(["gate-commit", "--repo", self.repo, "--staged", self.rel,
                   "--rollout-provider", "anthropic:claude-x", "--no-restage"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
