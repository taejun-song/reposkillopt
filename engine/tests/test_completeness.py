"""Feature 010 — deterministic completeness guarantee (model-free, idempotent)."""
import os
import tempfile
import unittest

from reposkillopt_engine.completeness import ensure_symbol_completeness
from reposkillopt_engine.quality import compute_structure
from reposkillopt_engine.structure import extract_symbols


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass AuthService:\n    pass\n")
    with open(os.path.join(d, "ui.ts"), "w") as f:
        f.write("export function render() {}\nclass Widget {}\n")
    return d


class TestCompleteness(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.syms = extract_symbols(self.repo)            # create_app, AuthService, render, Widget

    def _cov(self, spec):
        return compute_structure(spec, self.syms, []).symbol_coverage

    def test_append_makes_coverage_100(self):
        spec = "## Core modules\n**[fact]** only create_app is discussed `pkg/app.py:1`.\n"
        self.assertLess(self._cov(spec), 1.0)             # AuthService/render/Widget missing
        done = ensure_symbol_completeness(spec, self.repo)
        self.assertEqual(self._cov(done), 1.0)            # SC-001: guaranteed 100%
        self.assertIn("Symbols not yet analyzed", done)
        self.assertIn("defined,", done)                   # counts line

    def test_idempotent(self):
        spec = "## Core modules\ncreate_app\n"
        once = ensure_symbol_completeness(spec, self.repo)
        twice = ensure_symbol_completeness(once, self.repo)
        self.assertEqual(once, twice)                     # SC-002: byte-identical

    def test_analyzed_fraction_unchanged(self):
        # only create_app + AuthService analyzed (named in body); the rest get listed.
        spec = "## Core modules\n**[fact]** create_app and AuthService `pkg/app.py:1`.\n"
        before = compute_structure(spec, self.syms, []).analyzed_fraction
        done = ensure_symbol_completeness(spec, self.repo)
        after = compute_structure(done, self.syms, [])
        self.assertEqual(after.symbol_coverage, 1.0)      # accounted 100%
        self.assertEqual(after.analyzed_fraction, before)  # SC-003: listing != analysis

    def test_already_complete_is_noop(self):
        names = " ".join(s.name for s in self.syms)
        spec = f"## Core modules\n{names}\n"
        self.assertEqual(ensure_symbol_completeness(spec, self.repo), spec)

    def test_model_free_deterministic(self):
        spec = "## Core modules\ncreate_app\n"
        a = ensure_symbol_completeness(spec, self.repo)
        b = ensure_symbol_completeness(spec, self.repo)
        self.assertEqual(a, b)

    def test_model_emitted_partial_section_still_reaches_100(self):
        # Regression: the skill tells the model to write its own "Symbols not yet analyzed"
        # section. When it does so PARTIALLY and mid-document, the old code judged "missing"
        # against the removed section and dropped the files it named (live 71%/94% leak).
        spec = (
            "## Core modules\n**[fact]** create_app `pkg/app.py:1`.\n\n"
            "## Symbols not yet analyzed\n\n- pkg/app.py: AuthService\n\n"   # PARTIAL, mid-doc
            "## Data model\nThe Widget renders.\n"                           # heading AFTER it
        )
        done = ensure_symbol_completeness(spec, self.repo)
        self.assertEqual(self._cov(done), 1.0)                      # render must not vanish
        self.assertEqual(done.count("## Symbols not yet analyzed"), 1)  # no duplicate section
        # idempotent even from the partial-section starting point
        self.assertEqual(ensure_symbol_completeness(done, self.repo), done)


if __name__ == "__main__":
    unittest.main()
