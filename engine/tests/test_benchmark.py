"""Feature 007 — grounding benchmark: scoring, aggregate, report, determinism (model-free)."""
import os
import tempfile
import unittest

from reposkillopt_engine.benchmark import (parse_manifest, render_report, run_benchmark,
                                           run_entry, BenchmarkEntry)
from reposkillopt_engine.grounding import REQUIRED_SECTIONS


def _repo(lines: int = 5):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("import os\n\n\ndef create_app():\n    return 1\n")  # 5 lines, has create_app
    return d


def _spec(citation: str, sections=REQUIRED_SECTIONS) -> str:
    body = "\n".join(f"## {s}\n" for s in sections)
    return body + f"\n**[fact]** the factory `{citation}`\n"


def _write_spec(text: str) -> str:
    fd, p = tempfile.mkstemp(suffix=".md"); os.close(fd)
    with open(p, "w") as f:
        f.write(text)
    return p


class _BoomProvider:
    """Fails if any model call happens — proves score mode is model-free."""
    def complete(self, *a, **k):
        raise AssertionError("score mode must not call a provider")


class TestManifest(unittest.TestCase):
    def test_parse_skips_comments_and_blanks(self):
        m = "# header\n\nalpha\t/a\t/a/spec.md\nbeta\t/b\t/b/spec.md\n"
        entries = parse_manifest(m)
        self.assertEqual([e.name for e in entries], ["alpha", "beta"])
        self.assertEqual(entries[0].repo, "/a")

    def test_malformed_line_raises(self):
        with self.assertRaises(ValueError):
            parse_manifest("only-one-field\n")


class TestScoring(unittest.TestCase):
    def test_grounded_vs_broken_rates(self):
        repo = _repo()
        good = _write_spec(_spec("pkg/app.py:4"))      # resolves
        bad = _write_spec(_spec("pkg/app.py:999"))     # out of range
        rg = run_entry(BenchmarkEntry("good", repo, good), tempfile.mkdtemp())
        rb = run_entry(BenchmarkEntry("bad", repo, bad), tempfile.mkdtemp())
        self.assertIsNone(rg.error)
        self.assertEqual((rg.resolved, rg.total, rg.rate), (1, 1, 1.0))
        self.assertTrue(rg.checks_pass)
        self.assertEqual(rb.rate, 0.0)
        self.assertFalse(rb.checks_pass)

    def test_score_mode_makes_no_model_call(self):
        repo = _repo(); spec = _write_spec(_spec("pkg/app.py:create_app"))
        r = run_entry(BenchmarkEntry("x", repo, spec), tempfile.mkdtemp(),
                      mode="score", provider=_BoomProvider())  # must be ignored
        self.assertIsNone(r.error)
        self.assertEqual(r.rate, 1.0)

    def test_missing_repo_is_error_not_crash(self):
        r = run_entry(BenchmarkEntry("ghost", "/no/such/repo", "/no/spec.md"), tempfile.mkdtemp())
        self.assertIsNotNone(r.error)


class TestAggregateAndReport(unittest.TestCase):
    def _manifest(self):
        repo = _repo()
        good = _write_spec(_spec("pkg/app.py:4"))
        bad = _write_spec(_spec("pkg/app.py:999"))
        return f"good\t{repo}\t{good}\nbad\t{repo}\t{bad}\nghost\t/no/repo\t/no/spec.md\n"

    def test_aggregate_math_and_skip(self):
        rep = run_benchmark(self._manifest(), mode="score", date="2026-06-07")
        a = rep.aggregate
        self.assertEqual(a.n, 2)              # good + bad scored
        self.assertEqual(a.skipped, 1)        # ghost errored
        self.assertEqual(a.mean_rate, 0.5)    # mean(1.0, 0.0)
        self.assertEqual(a.median_rate, 0.5)
        self.assertEqual(a.checks_pass_share, 0.5)  # only 'good' passes all checks

    def test_determinism(self):
        m = self._manifest()
        r1 = run_benchmark(m, mode="score", date="2026-06-07").aggregate
        r2 = run_benchmark(m, mode="score", date="2026-06-07").aggregate
        self.assertEqual((r1.mean_rate, r1.median_rate, r1.checks_pass_share, r1.skipped),
                         (r2.mean_rate, r2.median_rate, r2.checks_pass_share, r2.skipped))

    def test_report_shape_and_tsv_roundtrip(self):
        rep = run_benchmark(self._manifest(), mode="score", date="2026-06-07")
        out = render_report(rep, manifest_path="seed.tsv")
        self.assertIn("mean_rate:", out)                       # front matter
        self.assertIn("Reproduce:", out)
        self.assertIn("benchmark --manifest seed.tsv", out)    # reproduce command
        # machine-readable TSV block round-trips the numbers
        tsv = out.split("```tsv")[1].split("```")[0].strip().splitlines()
        rows = {r.split("\t")[0]: r.split("\t") for r in tsv}
        self.assertEqual(rows["good"][4], "1.0000")
        self.assertEqual(rows["good"][5], "true")
        self.assertEqual(rows["bad"][5], "false")


class TestQualitySurfacing(unittest.TestCase):
    def test_entry_carries_quality_and_report_shows_it(self):
        repo = _repo()
        spec = _write_spec(_spec("pkg/app.py:create_app"))
        rep = run_benchmark(f"q\t{repo}\t{spec}\n", mode="score", date="2026-06-09")
        e = rep.entries[0]
        self.assertIsNotNone(e.quality)                       # deterministic quality block attached
        self.assertIsNone(e.rubric_score)                     # rubric OFF by default
        out = render_report(rep, manifest_path="m.tsv")
        self.assertIn("Deterministic quality metrics", out)   # quality table
        self.assertIn("Deterministic checks (per-repo)", out) # per-check breakdown
        self.assertNotIn("Model-scored", out)                 # no rubric block by default
        # appended TSV columns present and round-trip
        tsv = out.split("```tsv")[1].split("```")[0].strip().splitlines()
        cols = tsv[0].split("\t")
        self.assertEqual(len(cols), 11)                       # 6 original + 5 new
        self.assertEqual(cols[6], f"{e.quality.quality_score:.4f}")

    def test_score_mode_quality_makes_no_model_call(self):
        repo = _repo(); spec = _write_spec(_spec("pkg/app.py:4"))
        # provider that raises if used — quality + grounding must be model-free
        rep = run_benchmark(f"q\t{repo}\t{spec}\n", mode="score", date="2026-06-09",
                            provider=_BoomProvider())
        self.assertIsNotNone(rep.entries[0].quality)
        self.assertIsNone(rep.entries[0].rubric_score)


class TestGenerateMode(unittest.TestCase):
    def test_generate_mode_with_stub_provider(self):
        repo = _repo()

        class StubProvider:
            def complete(self, prompt, system=None):
                return _spec("pkg/app.py:create_app")   # a grounded spec citing a real file

        r = run_entry(BenchmarkEntry("gen", repo, ""), tempfile.mkdtemp(),
                      mode="generate", provider=StubProvider(), skill_text="# skill")
        self.assertIsNone(r.error)
        self.assertEqual(r.rate, 1.0)
        self.assertTrue(r.checks_pass)


if __name__ == "__main__":
    unittest.main()
