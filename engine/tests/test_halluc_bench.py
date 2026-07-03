"""Feature 022 — mutation benchmark for the hallucination catcher (TDD)."""
import os
import tempfile
import unittest

from reposkillopt_engine import halluc_bench as hb
from reposkillopt_engine.completeness import ensure_symbol_completeness
from reposkillopt_engine.grounding import REQUIRED_SECTIONS
from reposkillopt_engine.hallucination import (CLAIM_CODE_MISMATCH, FABRICATED_SYMBOL,
                                               UNLABELED_CLAIM, UNSUPPORTED_QUANTITY,
                                               detect_hallucinations)


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass Service:\n    def run(self):\n        return 2\n")
    return d


def _clean_spec(repo):
    body = "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)
    body += "\n**[fact]** the factory `create_app` `pkg/app.py:1`\n"
    return ensure_symbol_completeness(body, repo)


class TestBenchmark(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.clean = _clean_spec(self.repo)

    def test_clean_spec_has_no_findings_precision_basis(self):
        self.assertEqual(detect_hallucinations(self.repo, "specs/repository-specification.md", self.clean), [])

    def test_mutators_inject_detectable_hallucinations(self):
        muts = hb.build_mutations(self.repo, self.clean)
        self.assertTrue(muts)
        for m in muts:
            fs = detect_hallucinations(self.repo, "specs/repository-specification.md", m.after)
            self.assertTrue(any(f.kind == m.expect for f in fs),
                            f"{m.cls} did not yield {m.expect}: {[f.kind for f in fs]}")

    def test_report_recall_precision_by_construction(self):
        rep = hb.run_mutation_benchmark(self.repo, self.clean, model="fixtures")
        # every class present with recall == flagged/injected
        self.assertEqual(set(rep.per_class), {CLAIM_CODE_MISMATCH, FABRICATED_SYMBOL,
                                              UNLABELED_CLAIM, UNSUPPORTED_QUANTITY})
        for cls, (inj, fl) in rep.per_class.items():
            self.assertGreaterEqual(inj, 1, cls)
            self.assertEqual(fl, inj, f"{cls} recall < 1.0 ({fl}/{inj})")   # SC-001 on fixtures
        self.assertEqual(rep.precision, 1.0)                                 # SC-002 clean not flagged
        self.assertIn("hallucination-calibration", rep.render())
        self.assertIn("recall", rep.render())


if __name__ == "__main__":
    unittest.main()
