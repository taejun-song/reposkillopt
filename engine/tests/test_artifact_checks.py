"""Feature 019 — deterministic artifact checks (TDD, written before implementation)."""
import os
import tempfile
import unittest

from reposkillopt_engine.artifact_checks import (check_adr, check_architecture_view,
                                                 check_impact_analysis, check_task_ledger)


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "pkg"))
    with open(os.path.join(d, "pkg", "app.py"), "w") as f:
        f.write("def create_app():\n    return 1\n")          # create_app at line 1, file has 2 lines
    return d


# ---- Task Ledger ----
_LEDGER_OK = """---
goal: add caching
topological_order: [T001, T002, T003]
---
| id | goal | acceptance | depends_on |
|----|------|------------|------------|
| T001 | build cache layer | unit tests pass | |
| T002 | wire cache into reads | read path uses cache | T001 |
| T003 | add metrics | metrics emitted | T001, T002 |
"""


class TestTaskLedger(unittest.TestCase):
    def test_valid_ledger_passes(self):
        self.assertTrue(check_task_ledger(_LEDGER_OK).passed)

    def test_missing_acceptance_fails(self):
        bad = _LEDGER_OK.replace("| read path uses cache |", "|  |")
        r = check_task_ledger(bad)
        self.assertFalse(r.passed)
        self.assertTrue(any("acceptance" in f.lower() for f in r.failures))

    def test_unknown_dependency_fails(self):
        bad = _LEDGER_OK.replace("| T001, T002 |", "| T001, T099 |")
        r = check_task_ledger(bad)
        self.assertFalse(r.passed)
        self.assertTrue(any("T099" in f for f in r.failures))

    def test_cycle_detected(self):
        bad = _LEDGER_OK.replace("| T001 | build cache layer | unit tests pass | |",
                                 "| T001 | build cache layer | unit tests pass | T003 |")
        r = check_task_ledger(bad)
        self.assertFalse(r.passed)
        self.assertTrue(any("cycl" in f.lower() for f in r.failures))

    def test_invalid_topological_order_fails(self):
        bad = _LEDGER_OK.replace("topological_order: [T001, T002, T003]",
                                 "topological_order: [T002, T001, T003]")   # T002 before its dep T001
        r = check_task_ledger(bad)
        self.assertFalse(r.passed)
        self.assertTrue(any("topolog" in f.lower() for f in r.failures))


# ---- ADR ----
_ADR_OK = """---
id: ADR-001
title: cache backend
status: proposed
---
## Context
We need a cache.
## Options considered
- In-memory: fast, not shared.
- Redis: shared, an extra dependency.
## Decision
Use Redis.
## Consequences
Operational dependency added.
"""


class TestADR(unittest.TestCase):
    def test_valid_adr_passes(self):
        self.assertTrue(check_adr(_ADR_OK).passed)

    def test_single_option_fails(self):
        bad = _ADR_OK.replace("- In-memory: fast, not shared.\n", "")
        r = check_adr(bad)
        self.assertFalse(r.passed)
        self.assertTrue(any("option" in f.lower() for f in r.failures))

    def test_missing_decision_fails(self):
        bad = _ADR_OK.replace("## Decision\nUse Redis.\n", "")
        self.assertFalse(check_adr(bad).passed)


# ---- Architecture View + Impact (need a repo for citation resolution) ----
class TestArchitectureView(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_cited_components_pass(self):
        text = ("## Components\n- **[fact]** app factory `pkg/app.py:1`.\n\n"
                "## Dependency graph\n- **[fact]** pkg depends on stdlib `pkg/app.py:1`.\n")
        self.assertTrue(check_architecture_view(self.repo, text).passed)

    def test_uncited_component_fails(self):
        text = "## Components\n- the app factory does things.\n"   # no citation
        r = check_architecture_view(self.repo, text)
        self.assertFalse(r.passed)

    def test_unresolved_citation_fails(self):
        text = "## Components\n- **[fact]** factory `pkg/app.py:9999`.\n"   # out of range
        self.assertFalse(check_architecture_view(self.repo, text).passed)


class TestImpactAnalysis(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_rows_with_citation_and_confidence_pass(self):
        text = ("| Item | Why | Confidence | Evidence |\n|---|---|---|---|\n"
                "| create_app | entrypoint | high | `pkg/app.py:1` |\n")
        self.assertTrue(check_impact_analysis(self.repo, text).passed)

    def test_row_missing_confidence_fails(self):
        text = ("| Item | Why | Confidence | Evidence |\n|---|---|---|---|\n"
                "| create_app | entrypoint |  | `pkg/app.py:1` |\n")
        self.assertFalse(check_impact_analysis(self.repo, text).passed)

    def test_row_missing_citation_fails(self):
        text = ("| Item | Why | Confidence | Evidence |\n|---|---|---|---|\n"
                "| create_app | entrypoint | high | n/a |\n")
        self.assertFalse(check_impact_analysis(self.repo, text).passed)


if __name__ == "__main__":
    unittest.main()
