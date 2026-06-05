"""Live end-to-end test using the local Claude CLI as the LLM (no API key).

Opt-in and slow (makes real `claude -p` calls), so it is SKIPPED by default. Enable with:

    RSO_LIVE_CLAUDE=1 python3 -m unittest tests.test_claude_cli_live -v

It proves the real LLM path: regenerate a spec for a tiny synthetic repo and score it
into a valid 15-dimension / 7-check ScoreCard.
"""
import os
import shutil
import unittest

from reposkillopt_engine.judge import generate_spec, score_spec
from reposkillopt_engine.providers import make_provider
from reposkillopt_engine.rubric import DIMENSIONS, CHECKS

_ENABLED = os.environ.get("RSO_LIVE_CLAUDE") == "1" and shutil.which("claude") is not None

REPO = """\
file: calc.py
---
def add(a, b): return a + b
def main():
    import sys
    print(add(int(sys.argv[1]), int(sys.argv[2])))
if __name__ == "__main__": main()
"""


@unittest.skipUnless(_ENABLED, "set RSO_LIVE_CLAUDE=1 and have the claude CLI to run the live test")
class TestClaudeCLILive(unittest.TestCase):
    def test_regenerate_and_score(self):
        prov = make_provider("claude-cli")
        skill = "# Skill\n\n## Repository Understanding Workflow\nProduce a spec; cite path:line.\n"
        spec = generate_spec(prov, skill, "tinycalc", REPO)
        self.assertIn("calc.py", spec)
        card = score_spec(prov, spec, "tinycalc")
        self.assertTrue(all(d in card.scores for d in DIMENSIONS))
        self.assertTrue(all(c in card.checks for c in CHECKS))


if __name__ == "__main__":
    unittest.main()
