"""Tests for the real microsoft/SkillOpt integration.

These exercise the actual `skillopt` package (apply_edit + evaluate_gate). They skip
cleanly when skillopt is not installed, so the suite still passes without the optional dep.
"""
import unittest

from reposkillopt_engine import skillopt_backend as so
from reposkillopt_engine.gate import GateConfig, HeldOutRepo
from reposkillopt_engine.optimizer import OptimizerConfig, optimize
from reposkillopt_engine.proposal import Proposal
from reposkillopt_engine.providers import FakeProvider
from tests.helpers import card, full_scores

SKILL = "# Skill\n\n## Operating Principles\n- Rule one.\n"

skipif = unittest.skipUnless(so.HAS_SKILLOPT, "skillopt not installed")


def repo():
    return HeldOutRepo("six", "1.16.0", "...", full_scores(3))


def add_proposal():
    return {"edit_kind": "ADD", "anchor": "- Rule one.", "payload": "\n- Rule two.",
            "scope": "generic", "bump_level": "minor"}


@skipif
class TestSkillOptBackend(unittest.TestCase):
    def test_edit_op_mapping(self):
        self.assertEqual(so.to_skillopt_edit(Proposal("ADD", anchor="x", payload="y")).op, "insert_after")
        self.assertEqual(so.to_skillopt_edit(Proposal("ADD", payload="y")).op, "append")
        self.assertEqual(so.to_skillopt_edit(Proposal("REPLACE", anchor="x", payload="y")).op, "replace")
        self.assertEqual(so.to_skillopt_edit(Proposal("DELETE", anchor="x")).op, "delete")

    def test_apply_uses_real_skillopt(self):
        out = so.apply_proposal(SKILL, Proposal("ADD", anchor="- Rule one.", payload="\n- Rule two."))
        self.assertIn("- Rule two.", out)

    def test_gate_decision_real(self):
        improve = so.gate_decision("cand", 0.95, "cur", 0.80, "cur", 0.80, 0, 1)
        self.assertEqual(improve.action, "accept_new_best")
        worse = so.gate_decision("cand", 0.70, "cur", 0.80, "cur", 0.80, 0, 1)
        self.assertEqual(worse.action, "reject")

    def test_rubric_score_in_unit_range(self):
        from reposkillopt_engine.rubric import RepoResult, ScoreCard, aggregate, CHECKS
        c = [ScoreCard(full_scores(3), {k: True for k in CHECKS})]
        dims, checks = aggregate(c, full_scores(3))
        self.assertAlmostEqual(so.rubric_score([RepoResult("r", dims, checks)]), 1.0)

    def test_optimizer_skillopt_backend_accepts_improvement(self):
        # current skill scores below max (usefulness=2); the edit's candidate scores 1.0 -> SkillOpt accepts
        p = FakeProvider(scores=[card(3, usefulness=2), card(3)], proposals=[add_proposal()])
        res = optimize(p, SKILL, "0.2.0", [repo()],
                       OptimizerConfig(max_rounds=2, backend="skillopt", gate=GateConfig(mode="single")))
        self.assertEqual(res.accepted_count, 1)
        self.assertEqual(res.version, "0.3.0")
        self.assertIn("- Rule two.", res.skill_text)            # applied via skillopt.apply_edit
        self.assertIn(res.history[0].verdict, ("accept", "accept_new_best"))  # SkillOpt GateAction


class TestSkillOptOptional(unittest.TestCase):
    def test_require_raises_when_absent(self):
        if so.HAS_SKILLOPT:
            self.skipTest("skillopt installed; absence path not exercised here")
        with self.assertRaises(RuntimeError):
            so.require()


if __name__ == "__main__":
    unittest.main()
