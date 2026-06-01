import unittest

from reposkillopt_engine.proposal import Proposal, ProposalError

SKILL = "# Skill\n\n## Operating Principles\n- Rule one.\n"


class TestProposal(unittest.TestCase):
    def test_add_after_anchor(self):
        p = Proposal("ADD", anchor="- Rule one.", payload="\n- Rule two.")
        self.assertIn("- Rule two.", p.apply(SKILL))

    def test_add_at_end_when_no_anchor(self):
        p = Proposal("ADD", payload="\n## New\n")
        self.assertTrue(p.apply(SKILL).endswith("## New\n"))

    def test_replace(self):
        p = Proposal("REPLACE", anchor="- Rule one.", payload="- Rule ONE (clarified).")
        out = p.apply(SKILL)
        self.assertIn("clarified", out)
        self.assertNotIn("- Rule one.", out)

    def test_delete(self):
        p = Proposal("DELETE", anchor="- Rule one.")
        self.assertNotIn("- Rule one.", p.apply(SKILL))

    def test_missing_anchor_raises(self):
        p = Proposal("REPLACE", anchor="nope", payload="x")
        with self.assertRaises(ProposalError):
            p.apply(SKILL)

    def test_invalid_kind(self):
        with self.assertRaises(ProposalError):
            Proposal.from_dict({"edit_kind": "FROBNICATE"})

    def test_eligibility(self):
        self.assertTrue(Proposal("ADD", scope="generic", payload="x").eligible())
        self.assertFalse(Proposal("ADD", scope="repository-scoped", payload="x").eligible())
        self.assertFalse(Proposal("NONE").eligible())


if __name__ == "__main__":
    unittest.main()
