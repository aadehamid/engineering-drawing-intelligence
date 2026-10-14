#!/usr/bin/env python3
"""Tests for scripts/dexpi_parse.py.

The R0 graph is compared with the answer key, whose aliases map to ObjectIds through its
"keys". The node fields and evidence below are typed by hand from R0's rows. The
reference P&ID facts are typed by hand from standards/dexpi/2.0.1/reference_pid.xml:
one Tank, T4750, five PipeTees, four instrumentation functions, and TT4750.03 sensing at
the tank's instrument nozzle Nozzle17.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dexpi_parse as parse  # noqa: E402
import graph_publish  # noqa: E402
from test_dexpi_generate import records, written  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ANSWER_KEY = json.loads((ROOT / "fixtures" / "answer-keys" / "p3d-r0.json").read_text(encoding="utf-8"))
REFERENCE = ROOT / "standards" / "dexpi" / "2.0.1" / "reference_pid.xml"
REF = "dexpi:reference_pid.xml#"


def aliased(graph: dict) -> tuple[list[str], list[list[str]]]:
    """The graph's nodes and edges in the answer key's aliases."""
    alias = {}
    for name, key in ANSWER_KEY["keys"].items():
        alias[f"p3d:drawing:{key}" if name.startswith("S") else f"p3d:object:{key}"] = name
    nodes = sorted(alias[n["id"]] for n in graph["nodes"])
    edges = sorted([e["kind"], alias[e["source"]], alias[e["target"]]] for e in graph["edges"])
    return nodes, edges


class AnswerKeyTest(unittest.TestCase):
    def test_each_accepted_revision_parses_to_its_answer_key_graph(self):
        for revision in ("R0", "R1", "R2"):
            folder = written(revision)
            self.addCleanup(shutil.rmtree, folder)
            graph = graph_publish.canonical(parse.graph(parse.read(folder), parse.load_sidecar(folder)))
            expected = ANSWER_KEY["revisions"][revision]
            with self.subTest(revision=revision):
                self.assertEqual(aliased(graph), (expected["nodes"], expected["edges"]))
                self.assertEqual(graph["source_revision"], f"p3d:revision:{revision}")

    def test_parsing_gives_back_the_records_it_was_written_from(self):
        for revision in ("R0", "R1", "R2"):
            folder = written(revision)
            self.addCleanup(shutil.rmtree, folder)
            with self.subTest(revision=revision):
                self.assertEqual(parse.records(parse.read(folder), parse.load_sidecar(folder)), records(revision))


class R0Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = written("R0")
        cls.facts = parse.read(cls.folder)
        cls.graph = parse.graph(cls.facts, parse.load_sidecar(cls.folder))
        cls.nodes = {n["id"]: n for n in cls.graph["nodes"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.folder)

    def test_nodes_carry_kind_tag_and_name(self):
        expected = {
            "p3d:drawing:901": {"kind": "drawing", "name": "DEMO-PID-001"},
            "p3d:object:101": {"kind": "equipment", "tag": "TK-101"},
            "p3d:object:104": {"kind": "valve", "tag": "XV-102"},
            "p3d:object:105": {"kind": "instrument", "tag": "PI-102"},
            "p3d:object:106": {"kind": "junction"},
            "p3d:object:108": {"kind": "sheet_connector", "name": "TO-S2/A"},
            "p3d:object:114": {"kind": "pipe_segment", "tag": "L-101-B"},
        }
        for nid, fields in expected.items():
            with self.subTest(nid=nid):
                self.assertEqual({k: v for k, v in self.nodes[nid].items() if k in ("kind", "tag", "name")}, fields)

    def test_node_evidence_names_the_source_rows_and_the_appearance(self):
        self.assertEqual(self.nodes["p3d:object:108"]["evidence"], [
            {"table": "PlantObject", "ObjectId": 108},
            {"artifact_id": "p3d:drawing:901", "appearance_id": "p3d:appearance:8", "region": "30C",
             "coordinate_system": "p3d_drawing_handle", "source_locator": {"table": "DrawingAppearance", "RowId": 8}},
        ])
        self.assertEqual(self.nodes["p3d:object:101"]["evidence"][:2],
                         [{"table": "PlantObject", "ObjectId": 101}, {"table": "Equipment", "ObjectId": 101}])

    def test_edge_evidence_names_the_relationship_row(self):
        edges = {(e["kind"], e["source"], e["target"]): e["evidence"] for e in self.graph["edges"]}
        self.assertEqual(edges[("CROSS_SHEET_REFERENCE", "p3d:object:108", "p3d:object:109")],
                         [{"table": "SheetConnectorLink", "RowId": 1}])
        self.assertEqual(edges[("FLOW", "p3d:object:104", "p3d:object:107")], [{"table": "ConnectorPair", "RowId": 1}])
        self.assertEqual(edges[("FLOW", "p3d:object:101", "p3d:object:110")], [{"table": "SegmentStart", "RowId": 1}])
        self.assertEqual(edges[("INSTRUMENT_PARENT", "p3d:object:105", "p3d:object:102")], [{"table": "Ownership", "RowId": 1}])
        self.assertEqual(edges[("ON_SHEET", "p3d:object:105", "p3d:drawing:902")], [{"table": "DrawingAppearance", "RowId": 5}])

    def test_nothing_is_unsupported(self):
        self.assertEqual(parse.report(self.facts), {"unsupported_classes": {}, "problems": [], "gaps": []})

    def test_edges_come_from_the_dexpi_files_not_the_sidecar(self):
        copy = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, copy)
        shutil.copytree(self.folder, copy, dirs_exist_ok=True)
        tree = etree.parse(str(copy / "DEMO-PID-001.xml"))
        carrier = tree.find(".//Object[@id='Connection_Valve_104_Junction_107']")
        carrier.getparent().remove(carrier)
        tree.write(str(copy / "DEMO-PID-001.xml"))
        graph = parse.graph(parse.read(copy), parse.load_sidecar(copy))
        kinds = {(e["kind"], e["source"], e["target"]) for e in graph["edges"]}
        self.assertNotIn(("FLOW", "p3d:object:104", "p3d:object:107"), kinds)
        self.assertIn(("FLOW", "p3d:object:114", "p3d:object:104"), kinds)

    def test_one_drawing_alone_reports_its_connector_as_a_gap(self):
        alone = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, alone)
        shutil.copy(self.folder / "DEMO-PID-002.xml", alone)
        facts = parse.read(alone)
        self.assertEqual(facts["gaps"], ["nothing here continues to p3d:object:109"])
        self.assertNotIn("continues_to", [r[0] for r in facts["relations"]])


class ReferencePidTest(unittest.TestCase):
    """DEC-066: the parser reads DEXPI's own reference P&ID and reports what it does not support."""

    @classmethod
    def setUpClass(cls):
        cls.facts = parse.read(REFERENCE)
        cls.graph = parse.graph(cls.facts, None)
        cls.nodes = {n["id"]: n for n in cls.graph["nodes"]}

    def test_supported_classes_become_nodes(self):
        kinds = Counter(n["kind"] for n in self.graph["nodes"])
        self.assertEqual((kinds["equipment"], kinds["junction"], kinds["instrument"], kinds["sheet_connector"], kinds["drawing"]),
                         (1, 5, 4, 2, 1))
        self.assertEqual(self.nodes[REF + "Tank1"]["tag"], "T4750")
        self.assertEqual(self.nodes[REF + "ProcessInstrumentationFunction1"]["tag"], "PI-4712.01")
        self.assertEqual(self.nodes["dexpi:reference_pid.xml"]["name"], "DEXPI_example_PID.xml.")  # its PlantMetaData FileName
        graph_publish.canonical(self.graph)

    def test_the_temperature_function_is_parented_to_the_tank(self):
        parents = [(e["source"], e["target"]) for e in self.graph["edges"] if e["kind"] == "INSTRUMENT_PARENT"]
        self.assertEqual(parents, [(REF + "ProcessInstrumentationFunction4", REF + "Tank1")])

    def test_everything_else_is_reported_not_dropped(self):
        unsupported = parse.report(self.facts)["unsupported_classes"]
        self.assertEqual((unsupported["Plant/Piping.BallValve"], unsupported["Plant/Piping.GlobeValve"],
                          unsupported["Plant/ProcessEquipment.CentrifugalPump"]), (5, 3, 1))
        self.assertEqual(self.facts["gaps"], [
            f"{REF}FlowOutPipeOffPageConnector1 continues to nothing, which is not here",
            f"nothing here continues to {REF}FlowInPipeOffPageConnector1",
        ])


if __name__ == "__main__":
    unittest.main()
