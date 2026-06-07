"""Feature 005 — deterministic grounding: citation resolution + checks + failures."""
import os
import tempfile
import unittest

from reposkillopt_engine.grounding import (REQUIRED_SECTIONS, ground_spec,
                                           parse_citations)


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        # 5 lines; defines create_app
        f.write("import os\n\n\ndef create_app():\n    return 1\n")
    return d


def _spec_with(citations: str) -> str:
    # a minimal spec that contains every required section heading + the given citations
    body = "\n".join(f"## {s}\n" for s in REQUIRED_SECTIONS)
    return body + "\n**[fact]** something " + citations + "\n"


class TestParse(unittest.TestCase):
    def test_forms(self):
        cits = parse_citations("see `pkg/app.py:4`, `pkg/app.py:1-5`, `pkg/app.py:create_app`")
        kinds = sorted(c.kind for c in cits)
        self.assertEqual(kinds, ["line", "range", "symbol"])

    def test_ignores_ip_and_version(self):
        # 127.0.0.1:18080 and v0.2.0 must NOT be parsed as path citations
        cits = parse_citations("bind 127.0.0.1:18080 version 0.2.0 here")
        self.assertEqual(cits, [])

    def test_comma_line_list_expands(self):
        cits = parse_citations("`pkg/app.py:1,3,5`")
        self.assertEqual([c.line for c in cits], [1, 3, 5])


class TestResolve(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_line_in_and_out_of_range(self):
        g_ok = ground_spec(self.repo, _spec_with("`pkg/app.py:4`"))
        g_bad = ground_spec(self.repo, _spec_with("`pkg/app.py:999`"))
        self.assertEqual(g_ok.rate, 1.0)
        self.assertEqual(g_bad.rate, 0.0)
        self.assertTrue(any("out of range" in f for f in g_bad.failures))

    def test_symbol_present_absent(self):
        self.assertEqual(ground_spec(self.repo, _spec_with("`pkg/app.py:create_app`")).rate, 1.0)
        g = ground_spec(self.repo, _spec_with("`pkg/app.py:nonexistent_symbol`"))
        self.assertEqual(g.rate, 0.0)
        self.assertFalse(g.checks["cited_symbols_exist"])

    def test_missing_file(self):
        g = ground_spec(self.repo, _spec_with("`pkg/ghost.py:1`"))
        self.assertEqual(g.rate, 0.0)
        self.assertFalse(g.checks["cited_paths_exist"])
        self.assertTrue(any("does not exist" in f for f in g.failures))

    def test_grounded_beats_fabricated(self):
        """SC-001 / FR-008: identical specs, only citation targets differ."""
        grounded = ground_spec(self.repo, _spec_with("`pkg/app.py:4`"))
        fabricated = ground_spec(self.repo, _spec_with("`pkg/app.py:999`"))
        self.assertGreater(grounded.rate, fabricated.rate)
        det_grounded = sum(grounded.checks.values()) / len(grounded.checks)
        det_fabricated = sum(fabricated.checks.values()) / len(fabricated.checks)
        self.assertGreater(det_grounded, det_fabricated)

    def test_missing_section_flagged(self):
        spec = "## Repository overview\n**[fact]** x `pkg/app.py:4`\n"  # only 1 of 19 sections
        g = ground_spec(self.repo, spec)
        self.assertFalse(g.checks["sections_present"])
        self.assertTrue(any("missing" in f for f in g.failures))

    def test_unmarked_fact_flagged(self):
        spec = _spec_with("") + "\n**[fact]** an uncited claim with no anchor at all here.\n"
        g = ground_spec(self.repo, spec)
        self.assertFalse(g.checks["unsupported_claims_marked"])


if __name__ == "__main__":
    unittest.main()
