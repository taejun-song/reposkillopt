"""Feature 018 — continuous spec refinement loop (TDD, written before implementation)."""
import os
import re
import tempfile
import unittest

from reposkillopt_engine.refine import refine_loop, score_spec, spec_gaps
from reposkillopt_engine.judge import revise_spec
from reposkillopt_engine.grounding import REQUIRED_SECTIONS


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n")          # 2 lines: create_app at line 1
    return d


def _spec(cite: str) -> str:
    body = "\n".join(f"## {s}\nContent for {s}.\n" for s in REQUIRED_SECTIONS)
    return body + f"\n**[fact]** the app factory `{cite}`\n"


class _FixStub:
    """A model that revises the prior spec by fixing the bad citation -> grounding improves."""
    def __init__(self, bad, good):
        self.bad, self.good, self.prompts = bad, good, []

    def complete(self, prompt, system=None):
        self.prompts.append(prompt)
        m = re.search(r"<current-spec>\n(.*)\n</current-spec>", prompt, re.S)
        return (m.group(1) if m else "").replace(self.bad, self.good)


class _WorsenStub:
    """A model that returns a worse spec (drops a required section) — must be rejected."""
    def complete(self, prompt, system=None):
        m = re.search(r"<current-spec>\n(.*)\n</current-spec>", prompt, re.S)
        cur = m.group(1) if m else ""
        return cur.replace("## Repository overview\nContent for Repository overview.\n", "")


class TestGapsAndScore(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_gaps_list_unresolved_citation_deterministically(self):
        g1 = spec_gaps(self.repo, _spec("pkg/app.py:9999"))
        g2 = spec_gaps(self.repo, _spec("pkg/app.py:9999"))
        self.assertEqual(g1, g2)                               # deterministic
        self.assertTrue(any("9999" in x or "out of range" in x for x in g1))

    def test_no_gaps_when_clean(self):
        self.assertEqual(spec_gaps(self.repo, _spec("pkg/app.py:1")), [])

    def test_score_rewards_resolved_citation(self):
        bad, _ = score_spec(self.repo, _spec("pkg/app.py:9999"))
        good, _ = score_spec(self.repo, _spec("pkg/app.py:1"))
        self.assertGreater(good, bad)                          # resolving the citation scores higher


class TestRevisePrompt(unittest.TestCase):
    def test_prompt_carries_prior_spec_and_gaps(self):
        stub = _FixStub("x", "y")
        revise_spec(stub, "# skill", "demo", "PRIOR_SPEC_TEXT", ["gap A", "gap B"])
        p = stub.prompts[0]
        self.assertIn("PRIOR_SPEC_TEXT", p)                    # the prior spec is fed forward
        self.assertIn("gap A", p)
        self.assertIn("gap B", p)


class TestRefineLoop(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.initial = _spec("pkg/app.py:9999")                # starts with a fabricated citation

    def test_loop_carries_forward_and_improves_monotonically(self):
        stub = _FixStub("pkg/app.py:9999", "pkg/app.py:1")
        res = refine_loop(stub, "# skill", self.repo, "demo", initial_spec=self.initial, rounds=3)
        init_score, _ = score_spec(self.repo, self.initial)
        final_score, _ = score_spec(self.repo, res.spec)
        self.assertGreater(final_score, init_score)            # SC-001 improved
        scores = [init_score] + [s.score for s in res.history if s.accepted]
        self.assertEqual(scores, sorted(scores))               # monotonic non-decreasing
        self.assertIn("pkg/app.py:1", res.spec)                # the fix is in the carried-forward doc

    def test_worse_candidate_rejected(self):
        res = refine_loop(_WorsenStub(), "# skill", self.repo, "demo",
                          initial_spec=self.initial, rounds=2)
        self.assertEqual(res.spec, _ensure(self.repo, self.initial))   # prior retained, never regress
        self.assertTrue(all(not s.accepted for s in res.history))

    def test_early_stop_when_no_gaps(self):
        clean = _spec("pkg/app.py:1")
        stub = _FixStub("x", "y")
        res = refine_loop(stub, "# skill", self.repo, "demo", initial_spec=clean, rounds=5)
        self.assertEqual(res.history, [])                      # no gaps -> no rounds run
        self.assertEqual(len(stub.prompts), 0)                 # zero model calls


def _ensure(repo, spec):
    from reposkillopt_engine.completeness import ensure_symbol_completeness
    return ensure_symbol_completeness(spec, repo)


if __name__ == "__main__":
    unittest.main()
