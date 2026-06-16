"""Feature 013 — open-source / local LLM robustness (TDD, written before implementation)."""
import os
import tempfile
import unittest

# These imports/attrs do not exist yet — tests are RED first, then implementation makes them GREEN.
from reposkillopt_engine.sanitize import sanitize_model_spec
from reposkillopt_engine.providers import make_provider


CLEAN = """---
spec_id: demo
---

# Repository Specification — demo

## 1. Repository overview
- **[fact]** demo. `setup.py:1`.

## 8. Data model

```mermaid
erDiagram
    users ||--o{ posts : "author"
```
"""


class TestSanitize(unittest.TestCase):
    def test_strips_outer_markdown_fence_keeps_inner_mermaid(self):
        wrapped = "```markdown\n" + CLEAN + "```\n"
        out = sanitize_model_spec(wrapped)
        self.assertFalse(out.lstrip().startswith("```markdown"))     # outer fence gone
        self.assertIn("```mermaid", out)                              # inner diagram preserved
        self.assertIn("## 1. Repository overview", out)

    def test_strips_tilde_fence_and_bare_fence(self):
        for fence in ("~~~\n", "```\n"):
            wrapped = fence + CLEAN + fence.strip() + "\n"
            out = sanitize_model_spec(wrapped)
            self.assertTrue(out.lstrip().startswith("---") or out.lstrip().startswith("#"))

    def test_trims_chat_preamble_and_postamble(self):
        chatty = ("Sure! Here is the repository specification you asked for:\n\n"
                  + CLEAN + "\nLet me know if you'd like any changes!\n")
        out = sanitize_model_spec(chatty)
        self.assertTrue(out.lstrip().startswith("---") or out.lstrip().startswith("#"))
        self.assertNotIn("Let me know if", out)
        self.assertNotIn("Sure! Here is", out)

    def test_idempotent_and_noop_on_clean(self):
        self.assertEqual(sanitize_model_spec(CLEAN), CLEAN)           # FR-005 no-op on clean
        once = sanitize_model_spec("```md\n" + CLEAN + "```")
        self.assertEqual(sanitize_model_spec(once), once)            # idempotent


class TestThinkBlocks(unittest.TestCase):
    """Qwen3-style reasoning models emit <think>…</think> before the answer."""
    def test_strips_think_even_with_markdown_inside(self):
        q = ("<think>\n# step 1: read files\n- maybe a table\n---\n</think>\n" + CLEAN)
        out = sanitize_model_spec(q)
        self.assertNotIn("<think>", out)
        self.assertNotIn("</think>", out)
        self.assertNotIn("step 1: read files", out)
        self.assertTrue(out.lstrip().startswith("---") or out.lstrip().startswith("#"))

    def test_strips_thinking_and_reasoning_variants(self):
        for tag in ("thinking", "reasoning", "think"):
            q = f"<{tag}>planning the spec, considering # headings and lists</{tag}>\n\n" + CLEAN
            out = sanitize_model_spec(q)
            self.assertNotIn(f"<{tag}>", out)
            self.assertNotIn("planning the spec", out)

    def test_think_then_fenced_spec(self):
        q = "<think>reason ## stuff</think>\n```markdown\n" + CLEAN + "```\n"
        out = sanitize_model_spec(q)
        self.assertNotIn("<think>", out)
        self.assertFalse(out.lstrip().startswith("```markdown"))
        self.assertIn("## 1. Repository overview", out)

    def test_noop_when_no_think(self):
        self.assertEqual(sanitize_model_spec(CLEAN), CLEAN)


class TestOllamaAlias(unittest.TestCase):
    def test_ollama_alias_targets_local_endpoint(self):
        p = make_provider("ollama:qwen2.5-coder")
        self.assertEqual(p.model, "qwen2.5-coder")
        self.assertEqual(p.base_url, "http://localhost:11434/v1")    # SC-003 local, no real key
        self.assertTrue(p.api_key)                                    # dummy key is fine

    def test_openai_alias_unchanged(self):
        # existing behavior preserved: openai:<model> still works and is OpenAI-compatible
        p = make_provider("openai:gpt-4o-mini")
        self.assertEqual(p.model, "gpt-4o-mini")
        self.assertTrue(p.base_url.endswith("/v1"))


class TestGenerationAppliesSanitize(unittest.TestCase):
    def test_generate_spec_sanitizes_fenced_output(self):
        from reposkillopt_engine.judge import generate_spec

        class _Fenced:
            def complete(self, prompt, system=None):
                return "```markdown\n" + CLEAN + "```\n"
        out = generate_spec(_Fenced(), "# skill", "demo", "evidence")
        self.assertFalse(out.lstrip().startswith("```markdown"))     # FR-002 sanitized in the path
        self.assertIn("## 1. Repository overview", out)


class TestWeakModelGuaranteesHold(unittest.TestCase):
    def _repo(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "pkg"))
        with open(os.path.join(d, "pkg", "app.py"), "w") as f:
            f.write("def create_app():\n    return 1\n\n\nclass Service:\n    pass\n")
        return d

    def test_completeness_forces_100_even_for_thin_spec(self):
        from reposkillopt_engine.completeness import ensure_symbol_completeness
        from reposkillopt_engine.quality import compute_structure
        from reposkillopt_engine.structure import extract_symbols
        repo = self._repo()
        thin = "## Core modules\ncreate_app only.\n"                  # weak model named one symbol
        done = ensure_symbol_completeness(thin, repo)
        cov = compute_structure(done, extract_symbols(repo), []).symbol_coverage
        self.assertEqual(cov, 1.0)                                    # SC-002 guarantee model-independent

    def test_fabricated_citation_flagged(self):
        from reposkillopt_engine.grounding import ground_spec
        repo = self._repo()
        g = ground_spec(repo, "## Repository overview\n**[fact]** x `pkg/app.py:9999`.\n")
        self.assertLess(g.rate, 1.0)                                  # fabricated line caught


if __name__ == "__main__":
    unittest.main()
