"""Feature 005 — evidence pack: bounded, line-numbered, omissions recorded."""
import os
import tempfile
import unittest

from reposkillopt_engine.evidence import build_evidence_pack


class TestEvidencePack(unittest.TestCase):
    def _repo(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "README.md"), "w") as f:
            f.write("# Demo\nA test repository.\n")
        with open(os.path.join(d, "pyproject.toml"), "w") as f:
            f.write("[project]\nname='demo'\n")
        os.makedirs(os.path.join(d, "src"))
        with open(os.path.join(d, "src", "app.py"), "w") as f:
            f.write("\n".join(f"line_{i} = {i}" for i in range(1, 60)) + "\n")
        with open(os.path.join(d, "main.py"), "w") as f:
            f.write("def main():\n    return 1\n")
        return d

    def test_includes_real_files_and_line_numbers(self):
        pack = build_evidence_pack(self._repo())
        self.assertEqual(pack.repo_name and True, True)
        self.assertIn("REPOSITORY:", pack.text)
        self.assertIn("=== README (head) ===", pack.text)
        self.assertIn("pyproject.toml", pack.text)
        # line-numbered key file content present
        self.assertTrue(any(f.endswith("app.py") or f.endswith("main.py")
                            for f in pack.included_files))
        self.assertRegex(pack.text, r"\n1: ")   # a numbered first line appears

    def test_bounded_and_omissions_recorded(self):
        repo = self._repo()
        # tiny budget forces file blocks to be dropped and recorded
        pack = build_evidence_pack(repo, char_budget=400)
        self.assertLessEqual(len(pack.text), 400)
        self.assertTrue(pack.omitted, "omitted files must be recorded when truncated")

    def test_included_paths_are_repo_relative_and_exist(self):
        repo = self._repo()
        pack = build_evidence_pack(repo)
        for rel in pack.included_files:
            self.assertTrue(os.path.isfile(os.path.join(repo, rel)), rel)


if __name__ == "__main__":
    unittest.main()
