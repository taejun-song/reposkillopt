"""Deterministic tests for the SkillOpt-native per-repo optimizer.

These exercise backend selection, the SkillOpt apply/gate chain, rollout shaping, and the
repo-digest builder — all WITHOUT model calls. They skip cleanly when skillopt is absent.
The full optimize_repo loop (which makes real model calls) is validated live, not here.
"""
import unittest

from reposkillopt_engine import skillopt_native as N

skipif = unittest.skipUnless(N.HAS_SKILLOPT, "skillopt not installed")


@skipif
class TestSkillOptNative(unittest.TestCase):
    def test_backend_selection_keyless_and_apikey(self):
        import skillopt.model as M
        self.assertEqual(N.configure_opt_backend("claude-code"), "claude_chat")  # keyless local CLI
        self.assertEqual(M.get_optimizer_backend(), "claude_chat")
        self.assertEqual(N.configure_opt_backend("qwen"), "qwen_chat")           # API key
        self.assertEqual(N.configure_opt_backend("minimax"), "minimax_chat")     # API key
        N.configure_opt_backend("claude-code")  # reset to keyless default

    def test_unknown_backend_raises(self):
        with self.assertRaises(ValueError):
            N.configure_opt_backend("nonsense-backend")

    def test_skillopt_apply_patch_and_gate(self):
        from skillopt.evaluation import evaluate_gate
        from skillopt.optimizer import apply_patch
        skill = "# Skill\n\n## Operating Principles\n- Ground every claim in evidence.\n"
        patch = {"edits": [{"op": "insert_after", "target": "- Ground every claim in evidence.",
                            "content": "\n- Enumerate secondary structures."}], "reasoning": "t"}
        cand = apply_patch(skill, patch)
        self.assertIn("Enumerate secondary structures", cand)
        self.assertEqual(evaluate_gate(candidate_skill=cand, cand_hard=0.92, current_skill=skill,
                                       current_score=0.80, best_skill=skill, best_score=0.80,
                                       best_step=0, global_step=1, metric="hard").action,
                         "accept_new_best")

    def test_rollout_result_shape(self):
        r = N._rollout_results(0.7, "# spec", N.RepoTask("demo", "files"))
        self.assertEqual(r[0]["id"], "demo")
        self.assertEqual(r[0]["hard"], 0.7)
        self.assertEqual(r[0]["task_type"], "repo_spec")
        self.assertIn("predicted_answer", r[0])

    def test_build_repo_digest(self):
        import os
        digest = N.build_repo_digest(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/
        self.assertIn("REPOSITORY:", digest)
        self.assertLessEqual(len(digest), 8000)

    def test_snap_patch_resolves_anchor_and_applies(self):
        # SkillOpt's analyst returns a near-verbatim/truncated target; snap -> exact -> apply.
        from skillopt.optimizer import apply_patch
        skill = ("# Skill\n\n(e) **Trace behavior from entrypoint to core logic and side "
                 "effects.** Do at least one.\n")
        raw = {"patch": {"edits": [{
            "op": "replace",
            "target": "(e) **Trace behavior from entrypoint to core logic and side effects.** ...",
            "content": "(e) **Trace TWO behaviors end to end with citations.**",
        }], "reasoning": "deeper tracing"}}
        snapped = N._snap_patch(skill, raw)
        self.assertEqual(len(snapped["edits"]), 1)
        self.assertIn(snapped["edits"][0]["target"], skill)       # snapped to an exact substring
        cand = apply_patch(skill, snapped)
        self.assertIn("Trace TWO behaviors", cand)                 # SkillOpt's edit actually applied
        self.assertNotEqual(cand, skill)

    def test_snap_patch_drops_unresolvable(self):
        skill = "# Skill\n\n- Ground every claim in evidence.\n"
        raw = {"patch": {"edits": [{"op": "replace", "target": "no such line anywhere here xyz",
                                    "content": "x"}], "reasoning": "r"}}
        self.assertEqual(N._snap_patch(skill, raw)["edits"], [])


# Combined-reward + grounding plumbing — deterministic, no skillopt and no real model needed.
import json  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402

from reposkillopt_engine.evidence import EvidencePack  # noqa: E402
from reposkillopt_engine.grounding import REQUIRED_SECTIONS, GroundingResult  # noqa: E402
from reposkillopt_engine.rubric import CHECKS, DIMENSIONS  # noqa: E402


class _StubProvider:
    """Returns a fixed spec for REGENERATE_SPEC and a fixed scorecard for SCORE_SPEC."""
    def __init__(self, spec: str, dim_value: int = 3):
        self.spec = spec
        self._score = json.dumps({
            "scores": {d: dim_value for d in DIMENSIONS},
            "checks": {c: "pass" for c in CHECKS},
        })

    def complete(self, prompt, system=None):
        if prompt.startswith("REGENERATE_SPEC"):
            return self.spec
        if prompt.startswith("SCORE_SPEC"):
            return self._score
        raise AssertionError("unexpected prompt")


def _tmp_repo_with_app():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("import os\n\n\ndef create_app():\n    return 1\n")  # 5 lines, defines create_app
    return d


def _full_spec(citation: str) -> str:
    body = "\n".join(f"## {s}\n" for s in REQUIRED_SECTIONS)
    return body + f"\n**[fact]** the app factory `{citation}`\n"


class TestCombinedReward(unittest.TestCase):
    def test_grounded_spec_scores_perfect_reward(self):
        repo = _tmp_repo_with_app()
        task = N.RepoTask("demo", digest="x",
                          pack=EvidencePack(repo_path=repo, repo_name="demo", text="x"))
        prov = _StubProvider(_full_spec("pkg/app.py:create_app"), dim_value=3)
        reward, spec, card, ground = N._score_skill(prov, "# skill", task)
        self.assertIsInstance(ground, GroundingResult)
        self.assertEqual(ground.rate, 1.0)
        self.assertEqual(reward, 1.0)                      # 0.5*1.0 rubric + 0.5*1.0 det
        self.assertTrue(all(card.checks.values()))         # checks came from real grounding

    def test_fabricated_citation_scores_lower_than_grounded(self):
        """SC-001/FR-008 at the reward level: same rubric, only citations differ."""
        repo = _tmp_repo_with_app()
        task = N.RepoTask("demo", digest="x",
                          pack=EvidencePack(repo_path=repo, repo_name="demo", text="x"))
        grounded, *_ = N._score_skill(_StubProvider(_full_spec("pkg/app.py:create_app")), "#", task)
        fabricated, *_ = N._score_skill(_StubProvider(_full_spec("pkg/app.py:9999")), "#", task)
        self.assertGreater(grounded, fabricated)

    def test_no_pack_falls_back_to_rubric_only(self):
        task = N.RepoTask("demo", digest="some digest")     # no pack
        reward, spec, card, ground = N._score_skill(_StubProvider(_full_spec("pkg/app.py:1")), "#", task)
        self.assertIsNone(ground)
        self.assertEqual(reward, 1.0)                        # rubric-only, all dims = 3

    def test_fail_reason_uses_grounding_failures(self):
        g = GroundingResult(failures=['cited "pkg/app.py:999" — line 999 out of range (file has 5)'])
        msg = N._fail_reason(0.42, g)
        self.assertIn("out of range", msg)
        self.assertIn("0.42", msg)
        generic = N._fail_reason(0.42, None)
        self.assertIn("tracing", generic)                    # falls back to the generic guidance

    def test_native_result_carries_outputs(self):
        r = N.NativeResult(skill_text="s", version="0.2.0")
        self.assertEqual(r.best_spec, "")
        self.assertEqual(r.best_reward, 0.0)
        self.assertEqual(r.citation_rate, 1.0)

    def test_set_version_rewrites_front_matter(self):
        skill = "---\nname: repo-skillopt\nversion: 0.2.0\n---\n# body version: keep this\n"
        out = N._set_version(skill, "0.3.0")
        self.assertIn("version: 0.3.0", out)
        self.assertNotIn("version: 0.2.0", out)
        self.assertIn("# body version: keep this", out)        # only the front-matter line changes
        self.assertEqual(N._set_version("no front matter", "0.3.0"), "no front matter")  # no-op


if __name__ == "__main__":
    unittest.main()
