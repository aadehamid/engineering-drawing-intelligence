#!/usr/bin/env python3
"""Tests for scripts/compare_answer_key.py.

The small answer key and graphs below are typed by hand. The Rbad test uses the real
answer key, to show the pipeline's rejection reads as the key's reason once mapped.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_answer_key as cmp  # noqa: E402

REAL_KEY = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "answer-keys" / "p3d-r0.json").read_text())
KEY = {
    "keys": {"X1": 108, "X2": 109, "P5": 115, "S1": 901, "S2": 902},
    "revisions": {
        "R0": {"expected": "accepted", "reason": None, "nodes": ["P5", "S1", "S2", "X1", "X2"],
               "edges": [["CROSS_SHEET_REFERENCE", "X1", "X2"], ["FLOW", "X1", "X2"], ["FLOW", "X2", "P5"],
                         ["ON_SHEET", "P5", "S2"], ["ON_SHEET", "X1", "S1"], ["ON_SHEET", "X2", "S2"]]},
        "Rbad": {"expected": "rejected", "reason": "FLOW X2->P5 has missing endpoint P5", "nodes": [], "edges": []},
    },
}
GRAPH = {
    "source_revision": "p3d:revision:R0",
    "nodes": [{"id": "p3d:object:108", "kind": "sheet_connector"}, {"id": "p3d:object:109", "kind": "sheet_connector"},
              {"id": "p3d:object:115", "kind": "pipe_segment"}, {"id": "p3d:drawing:901", "kind": "drawing"},
              {"id": "p3d:drawing:902", "kind": "drawing"}],
    "edges": [{"kind": "FLOW", "source": "p3d:object:108", "target": "p3d:object:109"},
              {"kind": "CROSS_SHEET_REFERENCE", "source": "p3d:object:108", "target": "p3d:object:109"},
              {"kind": "FLOW", "source": "p3d:object:109", "target": "p3d:object:115"},
              {"kind": "ON_SHEET", "source": "p3d:object:108", "target": "p3d:drawing:901"},
              {"kind": "ON_SHEET", "source": "p3d:object:109", "target": "p3d:drawing:902"},
              {"kind": "ON_SHEET", "source": "p3d:object:115", "target": "p3d:drawing:902"}],
}


def accepted(graph: dict) -> dict:
    return {"outcome": "accepted", "graph": graph}


class CompareTest(unittest.TestCase):
    def test_an_exact_graph_matches(self):
        report = cmp.compare(accepted(GRAPH), KEY, "R0")
        self.assertEqual((report["match"], report["nodes"], report["edges"], report["differences"]), (True, 5, 6, []))

    def test_every_kind_of_difference_is_named(self):
        graph = copy.deepcopy(GRAPH)
        graph["edges"] = [e for e in graph["edges"] if e["kind"] != "CROSS_SHEET_REFERENCE"]
        graph["edges"].append({"kind": "FLOW", "source": "p3d:object:115", "target": "p3d:object:108"})
        graph["nodes"] = [n for n in graph["nodes"] if n["id"] != "p3d:drawing:901"]
        graph["edges"] = [e for e in graph["edges"] if e["target"] != "p3d:drawing:901"]
        self.assertEqual(cmp.compare(accepted(graph), KEY, "R0")["differences"], [
            "missing node S1", "missing edge CROSS_SHEET_REFERENCE X1 X2", "missing edge ON_SHEET X1 S1",
            "extra edge FLOW P5 X1"])

    def test_a_reversed_edge_is_a_difference(self):
        graph = copy.deepcopy(GRAPH)
        graph["edges"][2] = {"kind": "FLOW", "source": "p3d:object:115", "target": "p3d:object:109"}
        self.assertEqual(cmp.compare(accepted(graph), KEY, "R0")["differences"],
                         ["missing edge FLOW X2 P5", "extra edge FLOW P5 X2"])

    def test_a_repeated_edge_is_a_difference(self):
        graph = copy.deepcopy(GRAPH)
        graph["edges"].append(dict(graph["edges"][0]))
        self.assertEqual(cmp.compare(accepted(graph), KEY, "R0")["differences"], ["the graph repeats an edge"])

    def test_a_repeated_node_is_a_difference(self):
        graph = copy.deepcopy(GRAPH)
        graph["nodes"].append(dict(graph["nodes"][0]))
        report = cmp.compare(accepted(graph), KEY, "R0")
        self.assertEqual((report["match"], report["differences"]), (False, ["the graph repeats a node"]))

    def test_an_unknown_source_key_is_a_difference(self):
        graph = copy.deepcopy(GRAPH)
        graph["nodes"].append({"id": "p3d:object:999", "kind": "valve"})
        report = cmp.compare(accepted(graph), KEY, "R0")
        self.assertEqual((report["match"], report["differences"]), (False, ["p3d:object:999 is not a key in the answer key"]))
        rejected = {"outcome": "rejected", "reason": "FLOW p3d:object:115->p3d:object:777 has missing endpoint p3d:object:777"}
        self.assertEqual(cmp.compare(rejected, KEY, "Rbad")["differences"], ["p3d:object:777 is not a key in the answer key"])

    def test_the_wrong_outcome_fails_both_ways(self):
        self.assertEqual(cmp.compare(accepted(GRAPH), KEY, "Rbad")["differences"],
                         ["outcome is accepted, expected rejected"])
        self.assertIn("outcome is rejected, expected accepted",
                      cmp.compare({"outcome": "rejected", "reason": "x"}, KEY, "R0")["differences"])

    def test_rbad_rejection_reads_as_the_real_keys_reason(self):
        result = {"outcome": "rejected",
                  "reason": "FLOW p3d:object:114->p3d:object:104 has missing endpoint p3d:object:104"}
        report = cmp.compare(result, REAL_KEY, "Rbad")
        self.assertEqual((report["match"], report["reason"]), (True, "FLOW P6->VB has missing endpoint VB"))

    def test_a_different_rejection_reason_fails(self):
        result = {"outcome": "rejected", "reason": "FLOW p3d:object:115->p3d:object:109 has missing endpoint p3d:object:109"}
        self.assertEqual(cmp.compare(result, KEY, "Rbad")["differences"],
                         ["reason is 'FLOW P5->X2 has missing endpoint X2', expected 'FLOW X2->P5 has missing endpoint P5'"])

    def test_reports_are_written(self):
        with tempfile.TemporaryDirectory() as folder:
            cmp.write(cmp.compare(accepted(GRAPH), KEY, "R0"), Path(folder))
            self.assertEqual(json.loads((Path(folder) / "report.json").read_text())["match"], True)
            self.assertEqual((Path(folder) / "report.md").read_text(), (
                "# Answer-key comparison, revision R0\n\nResult: exact match.\n\n"
                "Outcome: accepted (expected accepted).\nNodes: 5 (expected 5). Edges: 6 (expected 6).\n"))


if __name__ == "__main__":
    unittest.main()
