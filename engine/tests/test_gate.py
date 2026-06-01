import unittest

from reposkillopt_engine.gate import GateConfig, HeldOutRepo, run_gate
from reposkillopt_engine.providers import FakeProvider
from reposkillopt_engine.rubric import Verdict
from tests.helpers import card, full_scores


def repo(baseline=None):
    return HeldOutRepo(name="six", commit="1.16.0", content="...",
                       baseline=baseline or full_scores(3))


class TestGate(unittest.TestCase):
    def test_pass_single(self):
        p = FakeProvider(scores=[card(3)])
        res = run_gate(p, "skill", [repo()], GateConfig(mode="single"))
        self.assertIs(res.verdict, Verdict.PASS)
        self.assertTrue(res.passed)

    def test_fail_single_on_regression(self):
        p = FakeProvider(scores=[card(3, evidence_quality=2)])  # below baseline 3
        res = run_gate(p, "skill", [repo()], GateConfig(mode="single"))
        self.assertIs(res.verdict, Verdict.FAIL)

    def test_majority_outlier_does_not_fail(self):
        # baseline test_strategy_quality=2; three scorers 3/3/1 -> majority 3 (above) -> PASS
        b = full_scores(3, test_strategy_quality=2)
        p = FakeProvider(scores=[
            card(3, test_strategy_quality=3),
            card(3, test_strategy_quality=3),
            card(3, test_strategy_quality=1),
        ])
        res = run_gate(p, "skill", [repo(b)], GateConfig(mode="majority", n=3))
        self.assertIs(res.verdict, Verdict.PASS)

    def test_majority_held_on_contested_at_baseline(self):
        # baseline risk_awareness=2; scorers 1/2/3 -> median 2 == baseline, low-agree -> HELD
        b = full_scores(3, risk_awareness=2)
        p = FakeProvider(scores=[
            card(3, risk_awareness=1),
            card(3, risk_awareness=2),
            card(3, risk_awareness=3),
        ])
        res = run_gate(p, "skill", [repo(b)], GateConfig(mode="majority", n=3))
        self.assertIs(res.verdict, Verdict.HELD)

    def test_majority_requires_odd_ge3(self):
        with self.assertRaises(ValueError):
            run_gate(FakeProvider(scores=[card(3)]), "skill", [repo()], GateConfig(mode="majority", n=2))


if __name__ == "__main__":
    unittest.main()
