import unittest

from reposkillopt_engine.rubric import (
    RepoResult, ScoreCard, Verdict, aggregate, verdict_for,
)
from tests.helpers import full_scores


class TestAggregate(unittest.TestCase):
    def _cards(self, dim, values):
        out = []
        for v in values:
            out.append(ScoreCard(scores=full_scores(**{dim: v}),
                                  checks={k: True for k in __import__(
                                      "reposkillopt_engine.rubric", fromlist=["CHECKS"]).CHECKS}))
        return out

    def test_majority_outvotes_outlier(self):
        c = self._cards("usefulness", [3, 3, 1])  # 2 agree on 3, one outlier 1
        dims, _ = aggregate(c, baseline={"usefulness": 2})
        d = next(x for x in dims if x.dimension == "usefulness")
        self.assertEqual(d.aggregate, 3)        # outlier did not flip the majority
        self.assertEqual(d.method, "majority")
        self.assertTrue(d.low_agreement)        # range 3-1 = 2
        self.assertEqual(d.vs_baseline, "above")

    def test_no_majority_uses_median(self):
        c = self._cards("risk_awareness", [1, 2, 3])  # all distinct
        dims, _ = aggregate(c, baseline={"risk_awareness": 2})
        d = next(x for x in dims if x.dimension == "risk_awareness")
        self.assertEqual(d.aggregate, 2)
        self.assertEqual(d.method, "median")
        self.assertTrue(d.low_agreement)
        self.assertEqual(d.vs_baseline, "equal")


class TestVerdict(unittest.TestCase):
    def _result(self, dim, values, baseline):
        c = []
        from reposkillopt_engine.rubric import CHECKS
        for v in values:
            c.append(ScoreCard(scores=full_scores(**{dim: v}), checks={k: True for k in CHECKS}))
        dims, checks = aggregate(c, baseline={dim: baseline})
        return RepoResult(repo="r", dims=dims, checks=checks)

    def test_pass_when_no_regression(self):
        r = self._result("usefulness", [3, 3, 3], baseline=3)
        self.assertIs(verdict_for([r]), Verdict.PASS)

    def test_fail_on_regression(self):
        r = self._result("evidence_quality", [2, 2, 2], baseline=3)  # below baseline
        self.assertIs(verdict_for([r]), Verdict.FAIL)

    def test_held_on_contested_at_baseline(self):
        r = self._result("risk_awareness", [1, 2, 3], baseline=2)  # median 2 == baseline, low-agree
        self.assertIs(verdict_for([r]), Verdict.HELD)

    def test_adjudication_clears_held(self):
        r = self._result("risk_awareness", [1, 2, 3], baseline=2)
        r.adjudicated.add("risk_awareness")
        self.assertIs(verdict_for([r]), Verdict.PASS)

    def test_fail_on_check(self):
        from reposkillopt_engine.rubric import CHECKS
        c = [ScoreCard(scores=full_scores(), checks={k: (k != "cited_paths_exist") for k in CHECKS})
             for _ in range(3)]
        dims, checks = aggregate(c, baseline=full_scores())
        self.assertIs(verdict_for([RepoResult("r", dims, checks)]), Verdict.FAIL)

    def test_unrealized_effect_fails(self):
        r = self._result("usefulness", [3, 3, 3], baseline=3)
        self.assertIs(verdict_for([r], effect_realized=False), Verdict.FAIL)


if __name__ == "__main__":
    unittest.main()
