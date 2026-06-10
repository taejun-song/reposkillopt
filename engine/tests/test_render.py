"""Deterministic audience-specific spec projections (render module)."""
import json
import unittest

from reposkillopt_engine.render import render, to_agent_view, to_structured

SPEC = """---
spec_id: demo
adapter: claude-code
---

## 1. Repository overview

- **[fact]** demo is a CLI library. `setup.py:4`.

## 10. Control-flow traces

<!-- authoring hint: lead with a flowchart -->

```mermaid
flowchart TD
  a["entry"] --> b["core"]
```

1. **[fact]** entry calls core. `src/app.py:12`.
2. **[inference]** core persists state. basis: `src/app.py:30-40`.

## 19. Evidence index

| Citation | What it supports |
|----------|------------------|
| `setup.py:4` | package name |
"""


class TestAgentView(unittest.TestCase):
    def setUp(self):
        self.view = to_agent_view(SPEC)

    def test_drops_mermaid_and_comments(self):
        self.assertNotIn("```mermaid", self.view)
        self.assertNotIn("flowchart", self.view)
        self.assertNotIn("authoring hint", self.view)

    def test_keeps_claims_citations_tables_headings(self):
        for keep in ("**[fact]**", "`src/app.py:12`", "## 19. Evidence index",
                     "| Citation |", "`setup.py:4`"):
            self.assertIn(keep, self.view)

    def test_idempotent_and_deterministic(self):
        self.assertEqual(to_agent_view(self.view), self.view)   # already lean -> stable
        self.assertEqual(to_agent_view(SPEC), to_agent_view(SPEC))


class TestStructuredView(unittest.TestCase):
    def setUp(self):
        self.obj = to_structured(SPEC)

    def test_meta_and_sections(self):
        self.assertEqual(self.obj["meta"]["spec_id"], "demo")
        names = [s["section"] for s in self.obj["sections"]]
        self.assertIn("Repository overview", names)            # enumerator stripped
        self.assertIn("Control-flow traces", names)

    def test_claims_carry_label_and_citations(self):
        flat = [c for s in self.obj["sections"] for c in s["claims"]]
        labels = {c["label"] for c in flat}
        self.assertEqual(labels, {"fact", "inference"})
        cited = [c for c in flat if c["citations"]]
        self.assertTrue(any("src/app.py:12" in c["citations"] for c in cited))

    def test_evidence_index_deduped_sorted(self):
        ev = self.obj["evidence_index"]
        self.assertEqual(ev, sorted(set(ev)))
        self.assertIn("setup.py:4", ev)

    def test_counts(self):
        self.assertEqual(self.obj["counts"]["claims"], 3)
        self.assertGreaterEqual(self.obj["counts"]["sections"], 3)

    def test_render_dispatch_and_validity(self):
        self.assertEqual(render(SPEC, "agent"), to_agent_view(SPEC))
        parsed = json.loads(render(SPEC, "structured"))   # valid JSON
        self.assertEqual(parsed["counts"]["claims"], 3)
        with self.assertRaises(ValueError):
            render(SPEC, "nonsense")


if __name__ == "__main__":
    unittest.main()
