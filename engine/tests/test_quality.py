"""Feature 008 — deterministic quality metrics (model-free)."""
import os
import tempfile
import unittest

from reposkillopt_engine.grounding import REQUIRED_SECTIONS, ground_spec
from reposkillopt_engine.quality import compute_quality


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("import os\n\n\ndef create_app():\n    return 1\n")  # 5 lines
    return d


def _full(extra: str = "") -> str:
    body = "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)
    return body + "\n" + extra


class TestQuality(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def _q(self, spec):
        return compute_quality(spec, ground_spec(self.repo, spec), self.repo)

    def test_clean_beats_malformed_same_grounding(self):
        """SC-001 / FR-011: same resolving citation, but one spec is malformed + unlabeled + incomplete."""
        clean = _full("**[fact]** the factory `pkg/app.py:4`\n")
        # dirty: a comma-malformed citation, an unlabeled fact, and drop a required section heading
        dirty = clean.replace("## Data model\nContent for Data model.\n", "")  # missing section
        dirty += "**[fact]** disjoint `pkg/app.py:4,5`\n**[fact]** an uncited claim with no anchor here.\n"
        qc, qd = self._q(clean), self._q(dirty)
        self.assertGreater(qc.quality_score, qd.quality_score)
        self.assertEqual(qc.malformed_citation_rate, 0.0)
        self.assertGreater(qd.malformed_citation_rate, 0.0)       # comma list detected
        self.assertLess(qd.labeled_claim_rate, 1.0)               # the uncited fact
        self.assertLess(qd.section_completeness, qc.section_completeness)

    def test_no_facts_density_none_labeled_one(self):
        q = self._q(_full())   # no [fact] claims
        self.assertIsNone(q.citation_density)
        self.assertEqual(q.labeled_claim_rate, 1.0)

    def test_labeled_rate_counts_cited_facts(self):
        spec = _full("**[fact]** a `pkg/app.py:4`\n**[fact]** uncited claim with nothing after it.\n")
        q = self._q(spec)
        self.assertEqual(q.fact_count, 2)
        self.assertEqual(q.labeled_claim_rate, 0.5)

    def test_deterministic(self):
        spec = _full("**[fact]** `pkg/app.py:4`\n")
        a, b = self._q(spec), self._q(spec)
        self.assertEqual(
            (a.quality_score, a.malformed_citation_rate, a.section_completeness, a.citation_density),
            (b.quality_score, b.malformed_citation_rate, b.section_completeness, b.citation_density))

    def test_numbered_headings_count_as_complete(self):
        """Readable numbered/decorated headings must still match the canonical section names.

        Regression: `## 1. Repository overview` previously failed the strict startswith and a
        fully-sectioned spec read section_completeness=0% (the live generate-mode anomaly)."""
        numbered = "\n".join(
            f"## {i}. {s}\nContent for {s}.\n" for i, s in enumerate(REQUIRED_SECTIONS, 1))
        self.assertEqual(self._q(numbered).section_completeness, 1.0)
        # a decorated heading variant ("## **Repository overview**") also matches
        decorated = numbered.replace("## 1. Repository overview", "## **Repository overview**")
        self.assertEqual(self._q(decorated).section_completeness, 1.0)


if __name__ == "__main__":
    unittest.main()
