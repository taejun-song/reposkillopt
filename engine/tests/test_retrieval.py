"""Feature 011 — deterministic section-scoped retrieval (model-free)."""
import os
import tempfile
import unittest

from reposkillopt_engine.evidence import build_evidence_pack
from reposkillopt_engine.retrieval import (SECTION_EVIDENCE, build_retrieval_report,
                                           retrieve_section_evidence)
from reposkillopt_engine.grounding import REQUIRED_SECTIONS


def _repo():
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# Demo\nA test repo.\n")
    with open(os.path.join(d, "pyproject.toml"), "w") as f:
        f.write("[project]\nname='demo'\n")
    os.makedirs(os.path.join(d, "src"))
    with open(os.path.join(d, "src", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass Service:\n    pass\n")
    with open(os.path.join(d, "main.py"), "w") as f:
        f.write("def main():\n    return create_app()\n")
    with open(os.path.join(d, "schema.sql"), "w") as f:
        f.write("CREATE TABLE users (id INT PRIMARY KEY);\n"
                "CREATE TABLE posts (id INT, author_id INT REFERENCES users(id));\n")
    return d


class TestSectionMapping(unittest.TestCase):
    def test_all_19_sections_mapped(self):
        # every required section has a retrieval mapping
        self.assertEqual(set(SECTION_EVIDENCE), set(REQUIRED_SECTIONS))
        self.assertEqual(len(SECTION_EVIDENCE), 19)

    def test_unknown_section_raises(self):
        with self.assertRaises(ValueError):
            retrieve_section_evidence(_repo(), "Not A Section")


class TestRetrieve(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_deterministic_byte_identical(self):
        a = retrieve_section_evidence(self.repo, "Data model")
        b = retrieve_section_evidence(self.repo, "Data model")
        self.assertEqual(a.text, b.text)                      # FR-003 / SC-003

    def test_slice_within_budget_and_below_full_pack(self):
        full = len(build_evidence_pack(self.repo).text)
        for section in SECTION_EVIDENCE:
            se = retrieve_section_evidence(self.repo, section, char_budget=4000)
            self.assertLessEqual(len(se.text), 4000)          # FR-004 budget
            self.assertLessEqual(len(se.text), full)          # FR-004 ≤ full pack

    def test_data_model_pulls_schema(self):
        se = retrieve_section_evidence(self.repo, "Data model")
        self.assertIn("schema", se.categories)
        self.assertTrue(any("users" in se.text and "posts" in se.text for _ in [0]))

    def test_technology_stack_pulls_manifest(self):
        se = retrieve_section_evidence(self.repo, "Technology stack")
        self.assertIn("pyproject.toml", se.text)

    def test_fallback_to_inventory(self):
        # "Known risks" maps only to the inventory fallback
        se = retrieve_section_evidence(self.repo, "Known risks")
        self.assertTrue(se.fell_back)
        self.assertEqual(se.categories, ["inventory"])
        self.assertIn("SYMBOLS", se.text)

    def test_model_free(self):
        # retrieval imports no embedding/vector library (check imports, not prose)
        import reposkillopt_engine.retrieval as r
        with open(r.__file__) as f:
            body = f.read().lower()
        for banned in ("import openai", "sentence_transformers", "import faiss",
                       "chromadb", "pinecone", "import torch"):
            self.assertNotIn(banned, body)


class TestReport(unittest.TestCase):
    def test_peak_vs_total_fields(self):
        rep = build_retrieval_report(_repo(), char_budget=4000)
        self.assertGreater(rep.baseline_chars, 0)
        self.assertLessEqual(rep.peak_section_chars, rep.baseline_chars)   # peak ≤ baseline
        self.assertGreaterEqual(rep.total_chars, rep.peak_section_chars)   # total ≥ peak
        self.assertEqual(len(rep.per_section), 19)
        self.assertGreaterEqual(rep.peak_reduction, 0.0)


class _SlicingStub:
    """Fake provider: records every prompt it sees, returns a heading + one line per section."""
    def __init__(self):
        self.prompt_sizes = []

    def complete(self, prompt, system=None):
        self.prompt_sizes.append(len(prompt))
        # the section heading is carried in <section>…</section>
        import re
        m = re.search(r"<section>(.*?)</section>", prompt)
        head = m.group(1) if m else "X"
        return f"## {head}\n**[fact]** stub line.\n"


class TestSectionScopedGeneration(unittest.TestCase):
    def test_loop_assembles_19_sections_each_from_its_slice(self):
        from reposkillopt_engine.judge import generate_spec_section_scoped
        repo = _repo()
        stub = _SlicingStub()
        spec, stats = generate_spec_section_scoped(stub, "# skill", "demo", repo, char_budget=4000)
        self.assertEqual(stats["sections"], 19)
        self.assertEqual(len(stub.prompt_sizes), 19)             # one model call per section
        # each per-section prompt is bounded by skill + one slice (≤ budget + overhead), never the full pack
        full = len(build_evidence_pack(repo).text)
        self.assertTrue(all(p < full + 4000 for p in stub.prompt_sizes))
        # assembled spec carries all 19 section headings
        for section in SECTION_EVIDENCE:
            self.assertIn(section, spec)
        self.assertEqual(stats["peak_chars"], max(p for _, p in build_retrieval_report(
            repo, char_budget=4000).per_section))


if __name__ == "__main__":
    unittest.main()
