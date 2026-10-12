#!/usr/bin/env python3
"""Tests for scripts/world.py and worlds/R0.yaml.

R0's states are compared, node for node and edge for edge, with the graph that
liong_facts.py parses from LIONG-006, so the world file and the document cannot drift.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import liong_facts  # noqa: E402
import world  # noqa: E402

R0 = world.ROOT / "worlds" / "R0.yaml"


class R0MatchesLiong006(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = world.load(R0)
        cls.doc = liong_facts.baseline(world.ROOT)

    def test_world_file_is_valid(self):
        errors, notes = world.check(self.data, "R0.yaml")
        self.assertEqual(errors, [])
        self.assertEqual(len(notes), 1)
        self.assertIn("Rbad is rejected as expected: FLOW P6->VB has missing endpoint VB", notes[0])

    def test_r0_is_the_documented_baseline(self):
        r0 = world.state(self.data, "R0")
        self.assertEqual(set(r0.nodes), self.doc.nodes)
        self.assertEqual({a for a, n in r0.nodes.items() if n["class"] == "drawing"}, self.doc.drawings)
        self.assertEqual(r0.all_edges(), set(self.doc.edges))

    def test_r1_renames_e2_and_keeps_every_identity_and_edge(self):
        r0, r1 = world.state(self.data, "R0"), world.state(self.data, "R1")
        self.assertEqual(r1.nodes["E2"]["tag"], "TK-202")
        self.assertEqual(r0.nodes["E2"]["tag"], "TK-102")
        self.assertEqual(set(r1.nodes), set(r0.nodes))
        self.assertEqual(r1.all_edges(), r0.all_edges())

    def test_r2_deletes_the_bypass_as_documented(self):
        r2 = world.state(self.data, "R2")
        deleted = self.doc.r2_deleted
        self.assertEqual(set(r2.nodes), self.doc.nodes - deleted)
        expected = {e for e in self.doc.edges if not liong_facts.touches(e, deleted)}
        self.assertEqual(r2.all_edges(), expected)
        self.assertEqual(r2.nodes["E2"]["tag"], "TK-202")

    def test_counts_match_the_figures_tool(self):
        figures = liong_facts.compute(world.ROOT)
        for revision, prefix in (("R0", "r0"), ("R2", "r2")):
            s = world.state(self.data, revision)
            self.assertEqual(len(s.nodes), figures[f"{prefix}.nodes"], revision)
            self.assertEqual(len(s.all_edges()), figures[f"{prefix}.edges"], revision)


class CheckFailsOnBrokenWorlds(unittest.TestCase):
    """Each case breaks R0 on purpose and asserts the reason the check gives."""

    def setUp(self):
        self.data = copy.deepcopy(world.load(R0))

    def errors(self):
        return world.check(self.data, "R0.yaml")[0]

    def assertError(self, text):
        found = self.errors()
        self.assertTrue(any(text in e for e in found), found)

    def test_rbad_marked_valid_fails(self):
        del self.data["revisions"]["Rbad"]["expected"]
        self.assertError("revision Rbad: FLOW P6->VB has missing endpoint VB")

    def test_rejected_revision_that_is_valid_fails(self):
        self.data["revisions"]["R2"]["expected"] = "rejected"
        self.assertError("revision R2 is marked expected: rejected but is valid")

    def test_dangling_edge_in_base_fails(self):
        self.data["edges"]["FLOW"].append(["P5", "ZZ"])
        self.assertError("revision R0: FLOW P5->ZZ has missing endpoint ZZ")

    def test_sheet_that_is_not_a_drawing_fails(self):
        self.data["nodes"]["E1"]["sheet"] = "E2"
        self.assertError("E1 is on sheet E2, which is not a drawing node")

    def test_unknown_base_fails(self):
        self.data["revisions"]["R2"]["base"] = "R9"
        self.assertError("revision R2: unknown base R9")

    def test_cycle_in_bases_fails(self):
        self.data["revisions"]["R0"]["base"] = "R1"
        self.assertError("cycle in its bases: R0 -> R1 -> R0")

    def test_change_to_a_missing_node_fails(self):
        self.data["revisions"]["R1"]["changes"] = [{"set_tag": {"node": "ZZ", "tag": "X"}}]
        self.assertError("set_tag names ZZ, which is not an engineering node in the base")

    def test_deleting_a_missing_edge_fails(self):
        self.data["revisions"]["R2"]["changes"][0] = {"delete_edge": ["FLOW", "J1", "P5"]}
        self.assertError("delete_edge names FLOW J1->P5, which is not in the base")

    def test_schema_rejects_an_unknown_class(self):
        self.data["nodes"]["E1"]["class"] = "pump"
        self.assertError("nodes/E1")

    def test_schema_rejects_an_unknown_key(self):
        self.data["nodes"]["E1"]["colour"] = "red"
        self.assertError("nodes/E1")

    def test_schema_rejects_an_unknown_edge_type(self):
        self.data["edges"]["ON_SHEET"] = [["E1", "S1"]]
        self.assertError("edges")

    def test_schema_rejects_a_lowercase_alias(self):
        self.data["nodes"]["e9"] = {"class": "valve", "sheet": "S1"}
        self.assertError("nodes")

    def test_schema_rejects_an_unknown_change(self):
        self.data["revisions"]["R1"]["changes"] = [{"rename_node": "E2"}]
        self.assertError("revisions/R1/changes/0")

    def test_schema_rejects_a_seed(self):
        self.data["seed"] = 2701006
        self.assertError("Additional properties are not allowed ('seed' was unexpected)")


if __name__ == "__main__":
    unittest.main()
