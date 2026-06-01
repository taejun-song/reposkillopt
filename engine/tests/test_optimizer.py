import unittest

from reposkillopt_engine.gate import GateConfig, HeldOutRepo
from reposkillopt_engine.optimizer import OptimizerConfig, optimize
from reposkillopt_engine.providers import FakeProvider
from tests.helpers import card, full_scores

SKILL = "# Skill\n\n## Operating Principles\n- Rule one.\n"


def repo():
    return HeldOutRepo("six", "1.16.0", "...", full_scores(3))


def add_proposal(payload="\n- Rule two."):
    return {"edit_kind": "ADD", "anchor": "- Rule one.", "payload": payload,
            "scope": "generic", "bump_level": "minor", "expected_effect": "more coverage"}


class TestOptimizer(unittest.TestCase):
    def test_accepts_improving_edit_and_bumps(self):
        # round 1: propose ADD -> gate PASS (no regression) -> accept + bump; round 2: NONE -> converge
        p = FakeProvider(scores=[card(3)], proposals=[add_proposal()])
        res = optimize(p, SKILL, "0.2.0", [repo()],
                       OptimizerConfig(max_rounds=5, gate=GateConfig(mode="single")))
        self.assertEqual(res.accepted_count, 1)
        self.assertEqual(res.version, "0.3.0")          # minor bump
        self.assertIn("- Rule two.", res.skill_text)    # edit applied
        self.assertTrue(any(r.note.startswith("converged") for r in res.history))

    def test_rejects_regressing_edit(self):
        # gate returns a regression -> FAIL -> not accepted, version unchanged
        p = FakeProvider(scores=[card(3, evidence_quality=2)], proposals=[add_proposal()])
        res = optimize(p, SKILL, "0.2.0", [repo()],
                       OptimizerConfig(max_rounds=3, patience=2, gate=GateConfig(mode="single")))
        self.assertEqual(res.accepted_count, 0)
        self.assertEqual(res.version, "0.2.0")
        self.assertNotIn("- Rule two.", res.skill_text)
        self.assertTrue(any(r.verdict == "FAIL" for r in res.history))

    def test_skips_repository_scoped_proposal(self):
        bad = add_proposal(); bad["scope"] = "repository-scoped"
        p = FakeProvider(proposals=[bad])
        res = optimize(p, SKILL, "0.2.0", [repo()], OptimizerConfig(max_rounds=3, patience=1))
        self.assertEqual(res.accepted_count, 0)
        self.assertTrue(any("not generic" in r.note for r in res.history))


if __name__ == "__main__":
    unittest.main()
