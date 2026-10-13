#!/usr/bin/env python3
"""Tests for scripts/world.py, worlds/R0.yaml and worlds/W-SP.yaml.

`fidelity_errors` compares R0.yaml with the facts its parsers read from LIONG-006:
every node's class, role, tag or drawing name, sheet, diameter and unit (and nothing
more), the tag context, every edge, and each revision's base, MOC and changes. The
parsers read only those facts. So the R0 text of LIONG-006 is also pinned by hash:
any edit to it fails `test_liong006_r0_text_is_the_reviewed_text` until someone
reviews R0.yaml against the new text and updates REVIEWED_SOURCE_SHA256.
"""
from __future__ import annotations

import copy
import hashlib
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import liong_facts  # noqa: E402
import world  # noqa: E402

R0 = world.ROOT / "worlds" / "R0.yaml"
# SHA-256 of r0_source() when R0.yaml was last reviewed against it.
REVIEWED_SOURCE_SHA256 = "032eb9c44aaadd1a66d7882ff5c115de2b86180beac4160466fccea937e1bf78"
CLASSES = {
    "Equipment": "equipment", "Valve": "valve", "Instrument": "instrument",
    "Connection point": "connection_point", "Pipe segment": "pipe_segment", "Drawing document": "drawing",
}


def r0_source(fixtures: str) -> str:
    """The LIONG-006 text R0.yaml encodes: the baseline section and the R1, R2 and Rbad rows."""
    rows = "".join(liong_facts.table_row(fixtures, r) + "\n" for r in ("R1", "R2", "Rbad"))
    return liong_facts.section(fixtures, "## Exact baseline R0") + rows


def documented_nodes(text: str) -> dict[str, dict]:
    """Each node of LIONG-006's R0 table as R0.yaml must write it, attributes included."""
    nodes = {}
    lines = text[text.index("| Alias | Type |"):].splitlines()[2:]
    for line in lines:
        if not line.startswith("|"):
            break
        alias_cell, type_cell, tag_cell, sheet_cell = (c.strip() for c in line.strip("|").split("|"))
        kind, _, role = type_cell.partition(", ")
        aliases = re.split(r"\s*,\s*", alias_cell)
        tags = re.split(r"\s*,\s*", tag_cell) if len(aliases) > 1 else [tag_cell]
        for alias, tag in zip(aliases, tags if len(tags) == len(aliases) else [tag_cell] * len(aliases)):
            node = {"class": CLASSES[kind]}
            if node["class"] == "drawing":
                node["name"] = tag
            else:
                if role:
                    node["role"] = role
                if tag != "No display tag":
                    node["tag"] = tag
                node["sheet"] = sheet_cell
            nodes[alias] = node
    diameter = int(re.search(r"Pipe segments have nominal diameter `(\d+) mm`", text).group(1))
    for alias, unit in re.findall(r"(\w+) has measurement unit `(\w+)`", text):
        nodes[alias]["attributes"] = {"unit": unit}
    for node in nodes.values():
        if node["class"] == "pipe_segment":
            node["attributes"] = {"nominal_diameter_mm": diameter}
    return nodes


def documented_revisions(fixtures: str) -> dict[str, dict]:
    """Each revision of LIONG-006's revision table as R0.yaml must write it."""
    r1 = re.search(r"Rename (\w+) from [\w-]+ to ([\w-]+); record synthetic (MOC-\w+)",
                   liong_facts.table_row(fixtures, "R1"))
    r2 = re.search(r"From (\w+), delete (\w+) and (\w+); remove (.*?), and their .*record (MOC-\w+)",
                   liong_facts.table_row(fixtures, "R2"))
    bad = re.search(r"From (\w+), delete (\w+) but leave .*; record (MOC-\w+)",
                    liong_facts.table_row(fixtures, "Rbad"))
    removed = [{"delete_edge": ["FLOW", a, b]} for a, b in re.findall(r"`(\w+)→(\w+)`", r2.group(4))]
    return {
        "R0": {"base": None, "moc": None},
        "R1": {"base": "R0", "moc": r1.group(3), "changes": [{"set_tag": {"node": r1.group(1), "tag": r1.group(2)}}]},
        "R2": {"base": r2.group(1), "moc": r2.group(5),
               "changes": removed + [{"delete_node": r2.group(2)}, {"delete_node": r2.group(3)}]},
        "Rbad": {"base": bad.group(1), "moc": bad.group(3), "expected": "rejected",
                 "changes": [{"delete_node": bad.group(2)}]},
    }


def fidelity_errors(data: dict) -> list[str]:
    """Every way R0.yaml differs from LIONG-006."""
    fixtures = (world.ROOT / liong_facts.FIXTURES).read_text(encoding="utf-8")
    text = liong_facts.section(fixtures, "## Exact baseline R0")
    errors = []
    context = re.search(r"All tags have context `([^`]+)`", text).group(1)
    if data["tag_context"] != context:
        errors.append(f"tag_context is {data['tag_context']}, LIONG-006 says {context}")
    expected = documented_nodes(text)
    for alias in sorted(set(expected) | set(data["nodes"])):
        if data["nodes"].get(alias) != expected.get(alias):
            errors.append(f"node {alias} is {data['nodes'].get(alias)}, LIONG-006 says {expected.get(alias)}")
    doc_edges = set(liong_facts.baseline(world.ROOT).edges)
    if world.state(data, "R0").all_edges() != doc_edges:
        errors.append("R0's edges differ from LIONG-006")
    for name, revision in documented_revisions(fixtures).items():
        if data["revisions"].get(name) != revision:
            errors.append(f"revision {name} is {data['revisions'].get(name)}, LIONG-006 says {revision}")
    if set(data["revisions"]) != {"R0", "R1", "R2", "Rbad"}:
        errors.append(f"revisions are {sorted(data['revisions'])}, LIONG-006 has R0, R1, R2, Rbad")
    return errors


class R0MatchesLiong006(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = world.load(R0)

    def test_world_file_is_valid(self):
        errors, notes = world.check(self.data, "R0.yaml")
        self.assertEqual(errors, [])
        self.assertEqual(len(notes), 1)
        self.assertIn("Rbad is rejected as expected: FLOW P6->VB has missing endpoint VB", notes[0])

    def test_liong006_r0_text_is_the_reviewed_text(self):
        fixtures = (world.ROOT / liong_facts.FIXTURES).read_text(encoding="utf-8")
        digest = hashlib.sha256(r0_source(fixtures).encode("utf-8")).hexdigest()
        self.assertEqual(digest, REVIEWED_SOURCE_SHA256,
                         "LIONG-006's R0 text changed: review worlds/R0.yaml against it, "
                         "then set REVIEWED_SOURCE_SHA256 in scripts/test_world.py")

    def test_any_edit_to_the_r0_text_changes_the_digest(self):
        fixtures = (world.ROOT / liong_facts.FIXTURES).read_text(encoding="utf-8")
        before = hashlib.sha256(r0_source(fixtures).encode("utf-8")).hexdigest()
        for old, new in (("record synthetic MOC-1", "record synthetic MOC-1-amended"),
                         ("Pipe lengths, roughness", "Pipe segments have length `20 m`. Roughness")):
            edited = fixtures.replace(old, new, 1)
            self.assertNotEqual(edited, fixtures, old)
            self.assertNotEqual(hashlib.sha256(r0_source(edited).encode("utf-8")).hexdigest(), before, old)

    def test_every_fact_matches_liong006(self):
        self.assertEqual(fidelity_errors(self.data), [])

    def test_revision_states(self):
        r0, r1, r2, bad = (world.state(self.data, r) for r in ("R0", "R1", "R2", "Rbad"))
        renamed = copy.deepcopy(r0.nodes)
        renamed["E2"]["tag"] = "TK-202"
        self.assertEqual(r1.nodes, renamed)
        self.assertEqual(r1.all_edges(), r0.all_edges())
        deleted = liong_facts.baseline(world.ROOT).r2_deleted
        self.assertEqual(r2.nodes, {a: n for a, n in renamed.items() if a not in deleted})
        self.assertEqual(r2.all_edges(), {e for e in r0.all_edges() if not liong_facts.touches(e, deleted)})
        self.assertEqual(bad.nodes, {a: n for a, n in r0.nodes.items() if a != "VB"})
        self.assertEqual(bad.edges, r0.edges)

    def test_counts_match_the_figures_tool(self):
        figures = liong_facts.compute(world.ROOT)
        for revision, prefix in (("R0", "r0"), ("R2", "r2")):
            s = world.state(self.data, revision)
            self.assertEqual(len(s.nodes), figures[f"{prefix}.nodes"], revision)
            self.assertEqual(len(s.all_edges()), figures[f"{prefix}.edges"], revision)


class WspHasWhatSmartPlantStoresDifferently(unittest.TestCase):
    """W-SP holds DEC-036's four features, at about R0's size, with only its baseline (DEC-042)."""

    w = world.load(world.ROOT / "worlds" / "W-SP.yaml")
    base = world.state(w, "W0")

    def flows(self) -> set[tuple[str, str]]:
        return {(e.source, e.target) for e in self.base.edges if e.kind == "FLOW"}

    def test_only_the_baseline(self):
        self.assertEqual(list(self.w["revisions"]), ["W0"])
        self.assertEqual(world.problems(self.base), [])

    def test_one_pipeline_of_several_runs_sharing_a_line_number(self):
        runs = {}
        for alias, node in self.base.nodes.items():
            if node["class"] == "pipe_segment":
                runs.setdefault(node["attributes"]["line_number"], set()).add(node["attributes"]["run"])
        self.assertEqual(runs, {"301": {"A", "B"}})

    def test_one_run_carries_several_inline_components(self):
        on_run = {}
        for alias, node in self.base.nodes.items():
            if node["class"] == "valve":
                ends = {s for s, t in self.flows() if t == alias} | {t for s, t in self.flows() if s == alias}
                runs = {self.base.nodes[e]["attributes"]["run"] for e in ends}
                self.assertEqual(len(runs), 1, f"{alias} sits between two runs")
                on_run.setdefault(runs.pop(), []).append(alias)
        self.assertGreaterEqual(max(len(v) for v in on_run.values()), 2)

    def test_one_cross_sheet_pair_and_one_instrument_with_a_parent(self):
        kinds = [e.kind for e in self.base.edges]
        self.assertEqual((kinds.count("CROSS_SHEET_REFERENCE"), kinds.count("INSTRUMENT_PARENT")), (1, 1))

    def test_about_r0_size(self):
        self.assertEqual((len(self.base.nodes), len(self.base.all_edges())), (15, 26))

    def test_flow_is_one_path_from_supply_to_receiving_vessel(self):
        nexts = dict(self.flows())
        self.assertEqual(len(nexts), len(self.flows()), "a node has two outgoing flows")
        path, node = ["E1"], "E1"
        while node in nexts:
            node = nexts[node]
            self.assertNotIn(node, path, f"flow returns to {node}")  # a cycle fails instead of hanging
            path.append(node)
        self.assertEqual((path[-1], len(path) - 1), ("E2", len(self.flows())))

    def test_facility_and_drawings(self):
        self.assertEqual(self.w["tag_context"], "DEMO-LEKKI/UNIT-B")
        drawings = {a: n["name"] for a, n in self.base.nodes.items() if n["class"] == "drawing"}
        self.assertEqual(drawings, {"S1": "DEMO-PID-101", "S2": "DEMO-PID-102"})

    def test_each_run_sits_on_one_sheet_with_its_valves(self):
        # Run A on the first sheet with two valves, run B on the second with one (DEC-052)
        sheets, valves = {}, {}
        for alias, node in self.base.nodes.items():
            if node["class"] == "pipe_segment":
                sheets.setdefault(node["attributes"]["run"], set()).add(node["sheet"])
        for alias, node in self.base.nodes.items():
            if node["class"] == "valve":
                ends = {s for s, t in self.flows() if t == alias} | {t for s, t in self.flows() if s == alias}
                run = {self.base.nodes[e]["attributes"]["run"] for e in ends}.pop()
                valves[run] = valves.get(run, 0) + 1
                self.assertEqual({node["sheet"]}, sheets[run], f"{alias} is not on its run's sheet")
        self.assertEqual((sheets, valves), ({"A": {"S1"}, "B": {"S2"}}, {"A": 2, "B": 1}))

    def test_cross_sheet_pair_joins_two_sheets_and_the_parent_is_equipment(self):
        n = self.base.nodes
        (source, target), = [(e.source, e.target) for e in self.base.edges if e.kind == "CROSS_SHEET_REFERENCE"]
        self.assertEqual(({n[source]["class"], n[target]["class"]}, n[source]["sheet"] != n[target]["sheet"]),
                         ({"connection_point"}, True))
        self.assertIn((source, target), self.flows())
        (child, parent), = [(e.source, e.target) for e in self.base.edges if e.kind == "INSTRUMENT_PARENT"]
        self.assertEqual((n[child]["class"], n[parent]["class"]), ("instrument", "equipment"))


class FidelityFailsOnWrongFacts(unittest.TestCase):
    """Each case changes one fact of R0.yaml and asserts the fidelity error names it."""

    def setUp(self):
        self.data = copy.deepcopy(world.load(R0))

    def assertFidelityError(self, text):
        found = fidelity_errors(self.data)
        self.assertTrue(any(text in e for e in found), found)

    def test_wrong_class(self):
        self.data["nodes"]["E1"]["class"] = "valve"
        self.assertFidelityError("node E1 is")

    def test_wrong_role(self):
        self.data["nodes"]["E1"]["role"] = "pump"
        self.assertFidelityError("node E1 is")

    def test_wrong_tag(self):
        self.data["nodes"]["V1"]["tag"] = "WRONG"
        self.assertFidelityError("node V1 is")

    def test_wrong_drawing_name(self):
        self.data["nodes"]["S1"]["name"] = "WRONG"
        self.assertFidelityError("node S1 is")

    def test_wrong_tag_context(self):
        self.data["tag_context"] = "WRONG"
        self.assertFidelityError("tag_context is WRONG")

    def test_wrong_diameter(self):
        self.data["nodes"]["P1"]["attributes"]["nominal_diameter_mm"] = 500
        self.assertFidelityError("node P1 is")

    def test_missing_unit(self):
        del self.data["nodes"]["I1"]["attributes"]
        self.assertFidelityError("node I1 is")

    def test_invented_value(self):
        self.data["nodes"]["V1"]["attributes"] = {"operating_pressure_bar": 10}
        self.assertFidelityError("node V1 is")

    def test_tag_on_an_untagged_junction(self):
        self.data["nodes"]["J1"]["tag"] = "J-1"
        self.assertFidelityError("node J1 is")

    def test_wrong_moc(self):
        self.data["revisions"]["R1"]["moc"] = "MOC-WRONG"
        self.assertFidelityError("revision R1 is")

    def test_extra_change(self):
        self.data["revisions"]["R1"]["changes"].append({"set_tag": {"node": "E1", "tag": "TK-999"}})
        self.assertFidelityError("revision R1 is")

    def test_extra_rbad_deletion(self):
        self.data["revisions"]["Rbad"]["changes"].append({"delete_node": "S1"})
        self.assertFidelityError("revision Rbad is")

    def test_extra_revision(self):
        self.data["revisions"]["R3"] = {"base": "R2", "moc": "MOC-3"}
        self.assertFidelityError("revisions are")

    def test_wrong_edge(self):
        self.data["edges"]["FLOW"][-1] = ["VB", "P3"]
        self.data["revisions"]["R2"]["changes"][2] = {"delete_edge": ["FLOW", "VB", "P3"]}
        self.assertFidelityError("R0's edges differ from LIONG-006")


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
