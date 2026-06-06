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


if __name__ == "__main__":
    unittest.main()
