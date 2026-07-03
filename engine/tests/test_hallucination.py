"""Feature 022 — deterministic hallucination catcher (TDD, written before implementation).

Four checks, model-free, reproducible. claim_code_mismatch = a REAL symbol cited at the wrong place;
fabricated_symbol = an identifier that exists NOWHERE (disjoint by construction). Plus determinism,
the clean-spec-zero precision guard, and the refine/commit-gate wiring.
"""
import os
import tempfile
import unittest

from reposkillopt_engine import hallucination as h
from reposkillopt_engine.completeness import ensure_symbol_completeness
from reposkillopt_engine.grounding import REQUIRED_SECTIONS


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass Service:\n    pass\n")
    return d


def _sections():
    return "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)


def _clean_spec(repo):
    body = _sections() + "\n**[fact]** the factory `create_app` `pkg/app.py:1`\n"
    return ensure_symbol_completeness(body, repo)


def _kinds(findings):
    return sorted({f.kind for f in findings})


class TestTokens(unittest.TestCase):
    def test_code_like_rule(self):
        for good in ("create_app", "createApp", "foo()", "a.b", "Service"):
            self.assertTrue(h._ident_like(good) or good in ("Service",), good)
        for bad in ("TODO", "note", "Redis", "the"):
            self.assertFalse(h._ident_like(bad), bad)


class TestClaimCodeMismatch(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_real_symbol_cited_at_wrong_line_flagged(self):
        # create_app is real (line 1) but cited at line 5 (class Service, window 2-8) -> mis-cited
        spec = _sections() + "\n**[fact]** the `create_app` factory `pkg/app.py:5`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertIn(h.CLAIM_CODE_MISMATCH, _kinds(fs))
        self.assertNotIn(h.FABRICATED_SYMBOL, _kinds(fs))

    def test_supported_claim_not_flagged(self):
        spec = _sections() + "\n**[fact]** the `create_app` factory `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.CLAIM_CODE_MISMATCH, _kinds(fs))

    def test_prose_only_claim_not_flagged(self):
        # no code token -> semantic blind spot, never flagged
        spec = _sections() + "\n**[fact]** the system uses caching `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.CLAIM_CODE_MISMATCH, _kinds(fs))


class TestFabricatedSymbol(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_invented_identifier_flagged(self):
        spec = _sections() + "\n**[fact]** uses `create_sessionX` `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertIn(h.FABRICATED_SYMBOL, _kinds(fs))

    def test_real_symbol_not_flagged(self):
        spec = _sections() + "\n**[fact]** the `create_app` factory `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.FABRICATED_SYMBOL, _kinds(fs))

    def test_non_code_backtick_not_flagged(self):
        spec = _sections() + "\n**[fact]** marked `TODO` here `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.FABRICATED_SYMBOL, _kinds(fs))


class TestUnlabeledClaim(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_unlabeled_prose_naming_real_symbol_flagged(self):
        spec = _sections() + "\nThe factory `create_app` builds the app and returns it.\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertIn(h.UNLABELED_CLAIM, _kinds(fs))

    def test_labeled_line_not_flagged(self):
        spec = _sections() + "\n**[fact]** the `create_app` factory `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.UNLABELED_CLAIM, _kinds(fs))

    def test_non_claim_artifact_not_flagged(self):
        # a feedback note is not a claim-bearing artifact -> label discipline not enforced
        spec = "The factory `create_app` builds the app and returns it now.\n"
        fs = h.detect_hallucinations(self.repo, "feedback/note.md", spec)
        self.assertNotIn(h.UNLABELED_CLAIM, _kinds(fs))


class TestUnsupportedQuantity(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_fabricated_quantity_flagged(self):
        spec = _sections() + "\n**[fact]** exposes 7 routes `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertIn(h.UNSUPPORTED_QUANTITY, _kinds(fs))

    def test_supported_quantity_not_flagged(self):
        # app.py line 1 window contains "1" (return 1) -> supported
        spec = _sections() + "\n**[fact]** returns 1 value `pkg/app.py:1`\n"
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertNotIn(h.UNSUPPORTED_QUANTITY, _kinds(fs))


class TestDeterminismAndClean(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_clean_spec_zero_findings(self):
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", _clean_spec(self.repo))
        self.assertEqual(fs, [], [f"{x.kind}@{x.line}:{x.reason}" for x in fs])

    def test_reproducible(self):
        spec = _sections() + "\n**[fact]** uses `create_sessionX` `pkg/app.py:5`\n"
        a = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        b = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertEqual([(x.kind, x.line, x.token) for x in a],
                         [(x.kind, x.line, x.token) for x in b])


class TestAllKindsOnCombinedSpec(unittest.TestCase):
    """US2 + SC-001/SC-002 on the fixtures."""
    def setUp(self):
        self.repo = _repo()

    def test_one_of_each_kind(self):
        spec = (_sections()
                + "\n**[fact]** the `create_app` factory `pkg/app.py:5`\n"        # mismatch
                + "**[fact]** uses `create_sessionX` `pkg/app.py:1`\n"            # fabricated
                + "The factory `create_app` builds the app and returns it.\n"    # unlabeled
                + "**[fact]** exposes 7 routes `pkg/app.py:1`\n")                 # quantity
        fs = h.detect_hallucinations(self.repo, "specs/repository-specification.md", spec)
        self.assertEqual(_kinds(fs),
                         sorted([h.CLAIM_CODE_MISMATCH, h.FABRICATED_SYMBOL,
                                 h.UNLABELED_CLAIM, h.UNSUPPORTED_QUANTITY]))


class TestWiring(unittest.TestCase):
    """US4 — spec_gaps includes hallucination gaps; commit gate has a hallucination gate."""
    def setUp(self):
        self.repo = _repo()
        self.hallucinated = _sections() + "\n**[fact]** uses `create_sessionX` `pkg/app.py:1`\n"

    def test_spec_gaps_include_hallucinations(self):
        from reposkillopt_engine.refine import spec_gaps
        gaps = spec_gaps(self.repo, self.hallucinated)
        self.assertTrue(any("create_sessionX" in g or "fabricated" in g.lower() for g in gaps), gaps)

    def test_commit_gate_has_hallucination_gate(self):
        from reposkillopt_engine import commit_gate as cg
        self.assertIn(cg.HALLUCINATION, cg.select_gates(cg.REPO_SPEC))
        rep = cg.run_gates(self.repo, "specs/repository-specification.md", self.hallucinated)
        self.assertIn(cg.HALLUCINATION, {v.gate for v in rep.verdicts})
        self.assertNotIn(cg.HALLUCINATION, rep.passing)          # fails on the hallucinated spec
        clean = _clean_spec(self.repo)
        rep2 = cg.run_gates(self.repo, "specs/repository-specification.md", clean)
        self.assertIn(cg.HALLUCINATION, rep2.passing)            # passes once clean


class TestCheckHallucinationCli(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.d = os.path.join(self.repo, ".reposkillopt", "specs")
        os.makedirs(self.d)
        self.rel = os.path.join(self.d, "repository-specification.md")

    def test_clean_exit_zero(self):
        open(self.rel, "w").write(_clean_spec(self.repo))
        from reposkillopt_engine.cli import main
        self.assertEqual(main(["check-hallucination", "--repo", self.repo, "--file", self.rel]), 0)

    def test_hallucinated_exit_one(self):
        open(self.rel, "w").write(_sections() + "\n**[fact]** uses `create_sessionX` `pkg/app.py:1`\n")
        from reposkillopt_engine.cli import main
        self.assertEqual(main(["check-hallucination", "--repo", self.repo, "--file", self.rel]), 1)

    def test_missing_file_exit_two(self):
        from reposkillopt_engine.cli import main
        self.assertEqual(main(["check-hallucination", "--repo", self.repo, "--file", "/no/such"]), 2)


if __name__ == "__main__":
    unittest.main()
