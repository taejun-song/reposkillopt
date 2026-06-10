"""Low-context knobs: --pack-budget / --low-context resolution + effect on the evidence pack."""
import os
import tempfile
import unittest
from argparse import Namespace

from reposkillopt_engine.cli import _LOW_CTX, _pack_opts
from reposkillopt_engine.evidence import build_evidence_pack


def _ns(**kw):
    kw.setdefault("low_context", False)
    kw.setdefault("pack_budget", None)
    return Namespace(**kw)


class TestPackOptsResolution(unittest.TestCase):
    def test_default_is_empty(self):
        self.assertEqual(_pack_opts(_ns()), {})                       # uses build_evidence_pack defaults

    def test_low_context_applies_preset(self):
        self.assertEqual(_pack_opts(_ns(low_context=True)), _LOW_CTX)
        self.assertLess(_LOW_CTX["char_budget"], 60_000)              # smaller than the default budget

    def test_explicit_budget_overrides(self):
        self.assertEqual(_pack_opts(_ns(pack_budget=10_000)), {"char_budget": 10_000})

    def test_low_context_plus_explicit_budget(self):
        opts = _pack_opts(_ns(low_context=True, pack_budget=8_000))
        self.assertEqual(opts["char_budget"], 8_000)                  # explicit wins
        self.assertEqual(opts["max_files"], _LOW_CTX["max_files"])    # but keeps preset file caps


class TestLowContextShrinksPack(unittest.TestCase):
    def _repo(self):
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "README.md"), "w") as f:
            f.write("# Demo\n")
        os.makedirs(os.path.join(d, "src"))
        for n in range(8):                                            # several large files
            with open(os.path.join(d, "src", f"m{n}.py"), "w") as f:
                f.write("\n".join(f"def f{n}_{i}(): return {i}" for i in range(300)) + "\n")
        return d

    def test_preset_pack_smaller_than_default(self):
        repo = self._repo()
        default = build_evidence_pack(repo)
        low = build_evidence_pack(repo, **_pack_opts(_ns(low_context=True)))
        self.assertLess(len(low.text), len(default.text))
        self.assertLessEqual(len(low.text), _LOW_CTX["char_budget"])
        # the high-signal structure inventory survives the shrink
        self.assertIn("=== SYMBOLS (deterministic inventory", low.text)


if __name__ == "__main__":
    unittest.main()
