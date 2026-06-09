"""Feature 009 — deterministic structural extraction + coverage metrics (model-free)."""
import os
import tempfile
import unittest

from reposkillopt_engine.quality import compute_structure
from reposkillopt_engine.structure import (extract_schema, extract_symbols,
                                           parse_er_entities)


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n\n\nclass AuthService:\n    pass\n")
    with open(os.path.join(d, "ui.ts"), "w") as f:
        f.write("export function render() {}\nexport const handleClick = () => {}\nclass Widget {}\n")
    os.makedirs(os.path.join(d, "db"))
    with open(os.path.join(d, "db", "schema.sql"), "w") as f:
        f.write("CREATE TABLE users (\n  id INTEGER PRIMARY KEY\n);\n"
                "CREATE TABLE posts (\n  id INTEGER,\n  author_id INTEGER REFERENCES users\n);\n")
    return d


class TestExtraction(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_symbols(self):
        syms = {(s.name, s.kind) for s in extract_symbols(self.repo)}
        self.assertIn(("create_app", "func"), syms)
        self.assertIn(("AuthService", "class"), syms)
        self.assertIn(("render", "func"), syms)         # TS function
        self.assertIn(("handleClick", "func"), syms)    # TS exported arrow
        self.assertIn(("Widget", "class"), syms)

    def test_schema(self):
        ents = {e.name: e for e in extract_schema(self.repo)}
        self.assertEqual(set(ents), {"users", "posts"})
        self.assertTrue(any(t == "users" for _, t in ents["posts"].fks))   # FK posts -> users

    def test_parse_er_entities(self):
        spec = "## Data model\n```mermaid\nerDiagram\n  USERS {\n    int id\n  }\n  POSTS }o--|| USERS : author\n```\n"
        self.assertEqual(set(parse_er_entities(spec)), {"USERS", "POSTS"})


class TestStructureMetrics(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.syms = extract_symbols(self.repo)
        self.schema = extract_schema(self.repo)

    def test_full_coverage_when_all_named(self):
        names = " ".join(s.name for s in self.syms)
        spec = f"## Core modules\n**[fact]** uses {names}.\n"
        m = compute_structure(spec, self.syms, self.schema)
        self.assertEqual(m.symbol_total, len(self.syms))
        self.assertEqual(m.symbol_coverage, 1.0)

    def test_omitted_symbol_below_100(self):
        names = " ".join(s.name for s in self.syms if s.name != "Widget")
        spec = f"## Core modules\n{names}\n"
        m = compute_structure(spec, self.syms, self.schema)
        self.assertLess(m.symbol_coverage, 1.0)               # SC-002: omission detected

    def test_listed_counts_as_accounted_not_analyzed(self):
        analyzed = "create_app AuthService render handleClick"
        spec = (f"## Core modules\n{analyzed}\n\n## Symbols not yet analyzed\n- ui.ts: Widget\n")
        m = compute_structure(spec, self.syms, self.schema)
        self.assertEqual(m.symbol_coverage, 1.0)              # Widget accounted (listed)
        self.assertLess(m.analyzed_fraction, 1.0)            # but not analyzed

    def test_per_file_count_accounting(self):
        # large-repo style: pkg/app.py symbols are named (analyzed); ui.ts is listed by file
        # with a count (no names) -> its symbols are accounted (no silent omission) but not analyzed.
        spec = ("## Core modules\n**[fact]** create_app and AuthService.\n"
                "\n## Symbols not yet analyzed\n- ui.ts: 3 symbols\n")
        m = compute_structure(spec, self.syms, self.schema)
        self.assertEqual(m.symbol_coverage, 1.0)      # all 5 accounted (2 named, 3 file-listed)
        self.assertLess(m.analyzed_fraction, 1.0)     # ui.ts's 3 not analyzed

    def test_diagram_grounding(self):
        grounded = "```mermaid\nerDiagram\n  users {\n int id\n }\n  posts }o--|| users : a\n```\n"
        fabricated = "```mermaid\nerDiagram\n  ghosttable {\n int id\n }\n```\n"
        mg = compute_structure(grounded, self.syms, self.schema)
        mf = compute_structure(fabricated, self.syms, self.schema)
        self.assertEqual(mg.diagram_grounding, 1.0)           # users/posts are real tables
        self.assertEqual(mf.diagram_grounding, 0.0)           # SC-003: fabricated entity

    def test_no_schema_or_no_diagram_is_none(self):
        m = compute_structure("## Data model\nNot applicable.\n", self.syms, self.schema)
        self.assertIsNone(m.diagram_grounding)               # no diagram -> n/a

    def test_deterministic(self):
        spec = "## Core modules\ncreate_app\n"
        a = compute_structure(spec, self.syms, self.schema)
        b = compute_structure(spec, self.syms, self.schema)
        self.assertEqual((a.symbol_coverage, a.analyzed_fraction, a.diagram_grounding),
                         (b.symbol_coverage, b.analyzed_fraction, b.diagram_grounding))


if __name__ == "__main__":
    unittest.main()
