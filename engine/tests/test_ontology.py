"""Feature 012 — deterministic codebase ontology (model-free)."""
import os
import tempfile
import unittest

from reposkillopt_engine.ontology import (ENTITY_KINDS, build_ontology, render_er_diagram,
                                          render_relationship_graph, to_structured)
from reposkillopt_engine.structure import parse_er_entities


def _repo():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "app"))
    with open(os.path.join(d, "app", "base.py"), "w") as f:
        f.write("class Service:\n    pass\n")
    with open(os.path.join(d, "app", "svc.py"), "w") as f:
        f.write("from app.base import Service\n\n\n"
                "class OrderService(Service):\n    pass\n\n\n"
                "class UserService(Service):\n    pass\n")   # Service inherited by 2 -> abstraction
    with open(os.path.join(d, "app", "api.py"), "w") as f:
        f.write("@router.post('/orders')\nasync def place_order():\n    return 1\n\n\n"
                "@app.get('/health')\ndef health():\n    return 'ok'\n")
    with open(os.path.join(d, "app", "jobs.py"), "w") as f:
        f.write("@celery.task\ndef nightly_settle():\n    return 1\n")
    with open(os.path.join(d, "schema.sql"), "w") as f:
        f.write("CREATE TABLE users (id INT PRIMARY KEY);\n"
                "CREATE TABLE orders (id INT, user_id INT REFERENCES users(id));\n")
    return d


class TestOntology(unittest.TestCase):
    def setUp(self):
        self.repo = _repo()
        self.onto = build_ontology(self.repo)

    def test_deterministic_byte_identical(self):
        import json
        a = json.dumps(to_structured(build_ontology(self.repo)), sort_keys=True)
        b = json.dumps(to_structured(build_ontology(self.repo)), sort_keys=True)
        self.assertEqual(a, b)                                   # FR-004 / SC-003

    def test_entities_have_fixed_kinds_and_locations(self):
        kinds = {e.kind for e in self.onto.entities}
        self.assertTrue(kinds.issubset(set(ENTITY_KINDS)))
        for e in self.onto.entities:
            self.assertTrue(e.file and e.line >= 1)              # pinned to file:line
        names = {e.name for e in self.onto.entities}
        self.assertIn("OrderService", names)
        self.assertTrue(any(e.kind == "route" for e in self.onto.entities))
        self.assertTrue(any(e.kind == "job" for e in self.onto.entities))
        self.assertTrue(any(e.kind == "data_entity" for e in self.onto.entities))

    def test_abstraction_by_fanin(self):
        # Service is inherited by OrderService + UserService (>=2) -> abstraction
        abstractions = {e.name for e in self.onto.entities if e.kind == "abstraction"}
        self.assertIn("Service", abstractions)

    def test_er_diagram_round_trips(self):
        diagram = render_er_diagram(self.onto)
        data = {e.name for e in self.onto.entities if e.kind == "data_entity"}
        parsed = set(parse_er_entities(diagram))
        self.assertEqual(parsed, data)                           # SC-002 round-trip
        self.assertIn("users", data)
        self.assertIn("orders", data)

    def test_foreign_key_relation_present(self):
        fks = [r for r in self.onto.relations if r.kind == "foreign_key"]
        self.assertTrue(any(r.dst == "users" for r in fks))

    def test_unresolved_frontier(self):
        # imports of external modules / non-repo targets land in unresolved, never drawn
        graph = render_relationship_graph(self.onto)
        self.assertIn("graph LR", graph)
        # the graph only draws inherits/registers_route/schedules, never raw imports
        self.assertNotIn("imports", graph)

    def test_no_schema_says_not_applicable(self):
        empty = tempfile.mkdtemp()
        with open(os.path.join(empty, "x.py"), "w") as f:
            f.write("def f():\n    return 1\n")
        self.assertIn("Not applicable", render_er_diagram(build_ontology(empty)))


if __name__ == "__main__":
    unittest.main()
