"""Feature 015 — refactoring opportunities (TDD, written before implementation)."""
import json
import os
import tempfile
import unittest

from reposkillopt_engine.refactor import analyze_refactors, render_refactor_section
from reposkillopt_engine.grounding import REQUIRED_SECTIONS, ground_spec
from reposkillopt_engine.quality import compute_quality


def _repo():
    d = tempfile.mkdtemp()
    # three functions with the SAME shape but different names/literals -> one cluster
    body = ("def {n}(x):\n"
            "    try:\n"
            "        y = compute(x) + {k}\n"
            "        return y\n"
            "    except ValueError:\n"
            "        return None\n")
    with open(os.path.join(d, "mod.py"), "w") as f:
        f.write(body.format(n="alpha", k=1) + "\n\n"
                + body.format(n="beta", k=2) + "\n\n"
                + body.format(n="gamma", k=3) + "\n\n"
                # a differently-shaped function (unique) — must NOT cluster
                + "def solo(z):\n    return z * z\n\n\n"
                # same shape but DIFFERENT except type — must NOT merge with the cluster
                + body.replace("ValueError", "KeyError").format(n="delta", k=9))
    return d


class TestRefactor(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.rep = analyze_refactors(self.repo)

    def test_three_same_shape_cluster(self):
        big = [c for c in self.rep.clusters if len(c.members) >= 3]
        self.assertTrue(big, "the alpha/beta/gamma shape should cluster")
        members = {(m["file"], m["line"]) for c in big for m in c.members}
        self.assertGreaterEqual(len(members), 3)
        self.assertTrue(all(c.suggestion for c in big))           # a suggested abstraction

    def test_unique_not_reported(self):
        # 'solo' is unique; it must not appear in any cluster
        labels = [m for c in self.rep.clusters for m in c.members]
        self.assertFalse(any("solo" in str(m) for m in labels))

    def test_except_type_separates_clusters(self):
        # delta (KeyError) must NOT be a member of the ValueError cluster of 3
        for c in self.rep.clusters:
            if len(c.members) >= 3:
                self.assertFalse(any(m["line"] >= 1 and "delta" in str(m) for m in c.members))

    def test_deterministic(self):
        a = json.dumps(_d(analyze_refactors(self.repo)), sort_keys=True)
        b = json.dumps(_d(analyze_refactors(self.repo)), sort_keys=True)
        self.assertEqual(a, b)

    def test_section_is_inference_only_and_grounded(self):
        section = render_refactor_section(self.rep)
        self.assertIn("16a. Refactoring opportunities", section)
        self.assertIn("**[inference]**", section)
        self.assertNotIn("**[fact]**", section)                   # advisory only (FR-005)
        g = ground_spec(self.repo, section)
        self.assertEqual(g.rate, 1.0)                             # SC-003 citations resolve

    def test_metric_safety(self):
        self.assertNotIn("Refactoring opportunities", REQUIRED_SECTIONS)
        self.assertEqual(len(REQUIRED_SECTIONS), 19)
        # inference-only section adds no [fact], so labeled-claim fact_count is unaffected
        q = compute_quality(render_refactor_section(self.rep), ground_spec(self.repo, render_refactor_section(self.rep)), self.repo)
        self.assertEqual(q.fact_count, 0)


def _d(rep):
    return {"counts": rep.counts,
            "clusters": [[c.signature, c.ntokens, c.severity, sorted((m["file"], m["line"]) for m in c.members)]
                         for c in rep.clusters]}


if __name__ == "__main__":
    unittest.main()
