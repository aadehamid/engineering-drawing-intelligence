#!/usr/bin/env python3
"""Tests for scripts/graph_publish.py.

The Neo4j tests need a server: set LIONG_NEO4J to "uri,user,password"; CI sets it.
The graph below is R0's cross-sheet piece, typed by hand: L-101-4 runs into the
off-page connector TO-S2/A on sheet 1, which continues to FROM-S1/A on sheet 2.
"""
from __future__ import annotations

import copy
import os
from pathlib import Path
import sys
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graph_publish as gp  # noqa: E402

AT = "2026-10-14T00:00:00+00:00"
LINK = [{"table": "SheetConnectorLink", "RowId": 1}]
GRAPH = {
    "source_revision": "p3d:revision:R0",
    "nodes": [
        {"id": "p3d:drawing:901", "kind": "drawing", "name": "DEMO-PID-001"},
        {"id": "p3d:drawing:902", "kind": "drawing", "name": "DEMO-PID-002"},
        {"id": "p3d:object:113", "kind": "pipe_segment", "tag": "L-101-4"},
        {"id": "p3d:object:108", "kind": "sheet_connector", "name": "TO-S2/A",
         "evidence": [{"drawing": "p3d:drawing:901", "handle": "30C"}]},
        {"id": "p3d:object:109", "kind": "sheet_connector", "name": "FROM-S1/A",
         "evidence": [{"drawing": "p3d:drawing:902", "handle": "30D"}]},
        {"id": "p3d:object:115", "kind": "pipe_segment", "tag": "L-101-5"},
    ],
    "edges": [
        {"kind": "FLOW", "source": "p3d:object:113", "target": "p3d:object:108"},
        {"kind": "FLOW", "source": "p3d:object:108", "target": "p3d:object:109", "evidence": LINK},
        {"kind": "CROSS_SHEET_REFERENCE", "source": "p3d:object:108", "target": "p3d:object:109", "evidence": LINK},
        {"kind": "FLOW", "source": "p3d:object:109", "target": "p3d:object:115"},
        {"kind": "ON_SHEET", "source": "p3d:object:108", "target": "p3d:drawing:901"},
        {"kind": "ON_SHEET", "source": "p3d:object:109", "target": "p3d:drawing:902"},
        {"kind": "ON_SHEET", "source": "p3d:object:113", "target": "p3d:drawing:901"},
        {"kind": "ON_SHEET", "source": "p3d:object:115", "target": "p3d:drawing:902"},
    ],
}


class ShapeTest(unittest.TestCase):
    def test_a_missing_endpoint_is_refused_with_its_name(self):
        graph = copy.deepcopy(GRAPH)
        graph["edges"].append({"kind": "FLOW", "source": "p3d:object:115", "target": "p3d:object:104"})
        with self.assertRaisesRegex(gp.PublishError, "^FLOW p3d:object:115->p3d:object:104 has missing endpoint p3d:object:104$"):
            gp.canonical(graph)

    def test_duplicate_nodes_unknown_kinds_and_extra_fields_are_refused(self):
        for change in (lambda g: g["nodes"].append(dict(g["nodes"][0])),
                       lambda g: g["edges"].append({"kind": "PIPED_TO", "source": "p3d:object:113", "target": "p3d:object:108"}),
                       lambda g: g["nodes"][0].update(colour="red"),
                       lambda g: g.pop("source_revision")):
            graph = copy.deepcopy(GRAPH)
            change(graph)
            with self.subTest(graph=graph), self.assertRaises(gp.PublishError):
                gp.canonical(graph)

    def test_snapshot_id_ignores_order_and_absent_evidence(self):
        reordered = copy.deepcopy(GRAPH)
        reordered["nodes"].reverse()
        reordered["edges"].reverse()
        reordered["nodes"][0]["evidence"] = []
        self.assertEqual(gp.snapshot_id(reordered), gp.snapshot_id(GRAPH))

    def test_snapshot_id_changes_with_any_fact(self):
        for change in (lambda g: g["nodes"][2].update(tag="L-101-9"),
                       lambda g: g["edges"][0].update(target="p3d:object:109"),
                       lambda g: g["edges"][1].update(evidence=[]),
                       lambda g: g.update(source_revision="p3d:revision:R1")):
            graph = copy.deepcopy(GRAPH)
            change(graph)
            with self.subTest(graph=graph):
                self.assertNotEqual(gp.snapshot_id(graph), gp.snapshot_id(GRAPH))


def server() -> str | None:
    return os.environ.get("LIONG_NEO4J")


@unittest.skipUnless(server(), "LIONG_NEO4J is not set; CI runs these against Neo4j")
class Neo4jTest(unittest.TestCase):
    def setUp(self):
        self.driver = gp.connect(server())
        for attempt in range(60):  # a fresh Neo4j container takes several seconds to accept connections
            try:
                self.driver.verify_connectivity()
                break
            except Exception:
                if attempt == 59:
                    raise
                time.sleep(2)
        self.graphs: list[dict] = []
        self.addCleanup(self.driver.close)
        self.addCleanup(self.remove)

    def remove(self):
        for graph in self.graphs:
            self.driver.execute_query("MATCH (n {snapshot_id: $sid}) DETACH DELETE n", sid=gp.snapshot_id(graph))

    def graph(self, revision: str) -> dict:
        """GRAPH under its own source revision, so each test owns a separate snapshot."""
        graph = copy.deepcopy(GRAPH) | {"source_revision": f"test:{self.id()}:{revision}"}
        self.graphs.append(graph)
        return graph

    def count(self, sid: str) -> tuple[int, int, int]:
        records, _, _ = self.driver.execute_query(
            "OPTIONAL MATCH (s:Snapshot {snapshot_id: $sid}) WITH count(s) AS s "
            "OPTIONAL MATCH (n:Entity {snapshot_id: $sid}) WITH s, count(n) AS n "
            "OPTIONAL MATCH ()-[r {snapshot_id: $sid}]->() RETURN s, n, count(r) AS r", sid=sid)
        return tuple(records[0].values())

    def test_publish_stores_exactly_the_graph(self):
        graph = self.graph("a")
        receipt = gp.publish(self.driver, graph, AT)
        self.assertEqual((receipt["outcome"], receipt["node_count"], receipt["edge_count"]), ("published", 6, 8))
        with self.driver.session() as session:
            self.assertEqual(gp.canonical(gp.read_back(session, receipt["snapshot_id"])), gp.canonical(graph))

    def test_publishing_again_changes_nothing(self):
        graph = self.graph("b")
        first = gp.publish(self.driver, graph, AT)
        second = gp.publish(self.driver, graph, "2026-10-15T00:00:00+00:00")
        self.assertEqual(second["outcome"], "unchanged")
        self.assertEqual(second["published_at"], first["published_at"])
        self.assertEqual(self.count(first["snapshot_id"]), (1, 6, 8))

    def test_a_changed_stored_snapshot_is_refused(self):
        graph = self.graph("c")
        sid = gp.publish(self.driver, graph, AT)["snapshot_id"]
        self.driver.execute_query("MATCH (n:Entity {snapshot_id: $sid, id: 'p3d:object:113'}) SET n.tag = 'L-999'", sid=sid)
        with self.assertRaisesRegex(gp.PublishError, "exists with other content"):
            gp.publish(self.driver, graph, AT)

    def test_a_failed_publish_leaves_nothing(self):
        graph = self.graph("d")
        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            gp.publish(self.driver, graph, AT, fail_after_nodes=True)
        self.assertEqual(self.count(gp.snapshot_id(graph)), (0, 0, 0))

    def test_cross_sheet_query_returns_the_connection_and_its_evidence(self):
        sid = gp.publish(self.driver, self.graph("e"), AT)["snapshot_id"]
        self.assertEqual(gp.cross_sheet(self.driver, sid), [{
            "from_id": "p3d:object:108", "from_label": "TO-S2/A", "from_sheet": "DEMO-PID-001",
            "from_evidence": [{"drawing": "p3d:drawing:901", "handle": "30C"}],
            "to_id": "p3d:object:109", "to_label": "FROM-S1/A", "to_sheet": "DEMO-PID-002",
            "to_evidence": [{"drawing": "p3d:drawing:902", "handle": "30D"}],
            "evidence": LINK,
        }])
        self.assertEqual(len(gp.cross_sheet(self.driver, sid, "FROM-S1/A")), 1)
        self.assertEqual(gp.cross_sheet(self.driver, sid, "TO-S9/Z"), [])

    def test_the_query_reads_one_snapshot_only(self):
        first = gp.publish(self.driver, self.graph("f1"), AT)["snapshot_id"]
        gp.publish(self.driver, self.graph("f2"), AT)
        self.assertEqual(len(gp.cross_sheet(self.driver, first)), 1)


if __name__ == "__main__":
    unittest.main()
