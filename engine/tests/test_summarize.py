"""Feature 020 — summarize-then-analyze (TDD, written before implementation)."""
import os
import tempfile
import unittest

from reposkillopt_engine.summarize import (assemble_from_summaries, enumerate_source_files,
                                           generate_spec_from_summaries, normalize_repo_relative,
                                           summarize_repo)
from reposkillopt_engine.evidence import _list_code_files
from reposkillopt_engine.grounding import REQUIRED_SECTIONS, ground_spec
from reposkillopt_engine.quality import compute_structure
from reposkillopt_engine.structure import extract_symbols
from pathlib import Path


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    open(os.path.join(d, "pkg", "__init__.py"), "w").close()          # the file the demo skipped
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass Service:\n    pass\n")
    return d


class _ProseStub:
    """A model that returns a one-line role/notes blurb (the prose half)."""
    def complete(self, prompt, system=None):
        return "Role: a small package module. Notes: returns an app and a service."


class _SpecStub:
    """Returns a full 19-section spec citing a real symbol (for the reduce test)."""
    def complete(self, prompt, system=None):
        body = "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)
        return body + "\n**[fact]** the factory `pkg/app.py:1`\n"


class _FailStub:
    def complete(self, prompt, system=None):
        raise RuntimeError("model unavailable")


class TestDeterministicCore(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_enumerate_matches_list_code_files_and_reproducible(self):
        a = enumerate_source_files(self.repo)
        self.assertEqual(a, enumerate_source_files(self.repo))         # reproducible
        self.assertEqual(sorted(a), sorted(_list_code_files(Path(self.repo))))
        self.assertIn("pkg/__init__.py", a)                           # the skipped-file is enumerated

    def test_normalize_repo_relative(self):
        t = f"see `{self.repo}/pkg/app.py:1` here"
        out = normalize_repo_relative(t, self.repo)
        self.assertIn("`pkg/app.py:1`", out)
        self.assertNotIn(self.repo, out)
        self.assertEqual(normalize_repo_relative(out, self.repo), out)  # idempotent
        self.assertEqual(normalize_repo_relative("`pkg/app.py:1`", self.repo), "`pkg/app.py:1`")  # no-op


class TestSummarizeRepo(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_every_file_summarized_no_omission(self):
        rep = summarize_repo(_ProseStub(), self.repo)
        self.assertEqual(rep.files_total, rep.files_summarized)        # FR-004: 100% file coverage
        files = enumerate_source_files(self.repo)
        for rel in files:
            self.assertTrue(os.path.isfile(os.path.join(self.repo, ".reposkillopt", "summaries", rel + ".md")))
        self.assertLessEqual(rep.peak_chars, rep.total_chars)

    def test_summary_citations_resolve_repo_relative(self):
        summarize_repo(_ProseStub(), self.repo)
        s = open(os.path.join(self.repo, ".reposkillopt", "summaries", "pkg/app.py.md")).read()
        self.assertIn("`pkg/app.py:1`", s)                            # grounded skeleton citation
        self.assertEqual(ground_spec(self.repo, s).rate, 1.0)         # resolves

    def test_model_failure_falls_back_to_skeleton(self):
        rep = summarize_repo(_FailStub(), self.repo)
        self.assertEqual(rep.files_total, rep.files_summarized)        # still 100% covered
        self.assertGreaterEqual(rep.skeleton_fallbacks, 1)
        s = open(os.path.join(self.repo, ".reposkillopt", "summaries", "pkg/app.py.md")).read()
        self.assertIn("create_app", s)                                # skeleton symbols present


class TestReduce(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        summarize_repo(_ProseStub(), self.repo)

    def test_assemble_reports_missing(self):
        ev = assemble_from_summaries(self.repo)
        self.assertIn("create_app", ev.text)                          # summaries are the evidence
        # delete one summary -> reported missing, not silent
        os.remove(os.path.join(self.repo, ".reposkillopt", "summaries", "pkg/app.py.md"))
        self.assertTrue(assemble_from_summaries(self.repo).missing)

    def test_generate_from_summaries_completeness_and_grounding(self):
        spec, stats = generate_spec_from_summaries(_SpecStub(), "# skill", self.repo)
        cov = compute_structure(spec, extract_symbols(self.repo), []).symbol_coverage
        self.assertEqual(cov, 1.0)                                     # FR-006 completeness ran
        self.assertEqual(ground_spec(self.repo, spec).rate, 1.0)      # citations resolve
        self.assertIn("peak", stats)
        self.assertIn("total", stats)


if __name__ == "__main__":
    unittest.main()
