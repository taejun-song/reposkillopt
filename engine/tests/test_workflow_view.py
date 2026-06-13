"""Feature 014 — business-process workflow view (TDD, written before implementation)."""
import json
import os
import tempfile
import unittest

from reposkillopt_engine.workflow import (analyze_workflows, enumerate_entrypoints,
                                          render_workflow_section, trace_flow)
from reposkillopt_engine.grounding import REQUIRED_SECTIONS, ground_spec


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "app"))
    with open(os.path.join(d, "app", "api.py"), "w") as f:
        f.write("from app.svc import place_order\n\n\n"
                "@router.post('/orders')\n"
                "async def create_order():\n"
                "    return place_order()\n")
    with open(os.path.join(d, "app", "svc.py"), "w") as f:
        f.write("def place_order():\n"
                "    db.session.commit()\n"      # side effect / persistence
                "    return 1\n")
    with open(os.path.join(d, "app", "cli.py"), "w") as f:
        f.write("@app.command()\ndef settle():\n    return place_order()\n")
    with open(os.path.join(d, "app", "jobs.py"), "w") as f:
        f.write("@celery.task\ndef nightly():\n    return place_order()\n")
    return d


class TestEnumerate(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.eps = enumerate_entrypoints(self.repo)

    def test_finds_route_job_cli_no_silent_omission(self):
        kinds = sorted({e.kind for e in self.eps})
        self.assertEqual(kinds, ["cli", "job", "route"])
        for e in self.eps:
            self.assertTrue(e.file and e.line >= 1)         # each pinned to file:line
        # the route is the POST /orders handler
        self.assertTrue(any(e.kind == "route" and "/orders" in e.name for e in self.eps))


class TestTrace(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()

    def test_flow_reaches_persistence_with_grounding(self):
        route = next(e for e in enumerate_entrypoints(self.repo) if e.kind == "route")
        flow = trace_flow(self.repo, route)
        self.assertGreaterEqual(len(flow.steps), 1)         # at least the entry hop
        # a called in-repo function (place_order) becomes a hop
        self.assertTrue(any("place_order" in s.label for s in flow.steps))
        # a side effect / persistence terminal is reached (commit)
        self.assertTrue(any(s.kind == "effect" for s in flow.steps))

    def test_every_box_file_line_resolves(self):
        rep = analyze_workflows(self.repo)
        section = render_workflow_section(rep)
        g = ground_spec(self.repo, section)
        self.assertEqual(g.rate, 1.0)                       # SC-003 every box grounded


class TestReportAndRender(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.rep = analyze_workflows(self.repo)

    def test_counts_and_no_omission(self):
        total = sum(self.rep.counts.values())
        self.assertEqual(total, len(self.rep.entrypoints))  # table total == enumerated
        self.assertGreaterEqual(total, 3)                   # route + job + cli

    def test_render_has_table_and_flowchart(self):
        s = render_workflow_section(self.rep)
        self.assertIn("|", s)                               # enumeration table
        self.assertIn("flowchart", s)                       # at least one flowchart

    def test_deterministic(self):
        a = json.dumps(_to_dict(analyze_workflows(self.repo)), sort_keys=True)
        b = json.dumps(_to_dict(analyze_workflows(self.repo)), sort_keys=True)
        self.assertEqual(a, b)


class TestMetricSafety(unittest.TestCase):
    def test_section_name_not_required(self):
        # "Business workflows" must NOT be a required section (denominator stays 19)
        self.assertNotIn("Business workflows", REQUIRED_SECTIONS)
        self.assertEqual(len(REQUIRED_SECTIONS), 19)


def _to_dict(rep):
    return {"counts": rep.counts,
            "flows": [[(s.kind, s.label, s.file, s.line) for s in f.steps] for f in rep.flows]}


if __name__ == "__main__":
    unittest.main()
