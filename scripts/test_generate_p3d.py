#!/usr/bin/env python3
"""Tests for the Plant 3D-style generator: fresh files, a faithful round trip, and no leaked truth."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_p3d as gen  # noqa: E402
from world import load, state  # noqa: E402


FRESH = gen.outputs()  # a generation in memory; test_committed_files_are_fresh ties it to the files


def read(revision: str) -> dict[str, list[dict]]:
    return {table: json.loads(FRESH[gen.OUT / revision / f"{table}.json"]) for table in gen.TABLES}


# Written out by hand from DEC-050, so these checks do not trust the generator under test.
EXPECTED_KEYS = {
    "E1": 101, "E2": 102, "V1": 103, "VB": 104, "I1": 105, "J1": 106, "J2": 107, "X1": 108, "X2": 109,
    "P1": 110, "P2": 111, "P3": 112, "P4": 113, "P6": 114, "P5": 115, "S1": 901, "S2": 902,
}
R0_ROWS = {  # each relationship table's rows in R0, as (first column, second column) aliases
    "SegmentStart": {("P1", "E1"), ("P2", "J1"), ("P3", "V1"), ("P4", "J2"), ("P5", "X2"), ("P6", "J1")},
    "SegmentEnd": {("P1", "J1"), ("P2", "V1"), ("P3", "J2"), ("P4", "X1"), ("P5", "E2"), ("P6", "VB")},
    "ConnectorPair": {("VB", "J2")},
    "SheetConnectorLink": {("X1", "X2")},
    "Ownership": {("E2", "I1")},
}
# Every object row of R0, written from LIONG-006's "Exact baseline R0" table and DEC-049's tag subparts.
R0_OBJECT_ROWS = {
    "Equipment": [
        {"ObjectId": 101, "Tag": "TK-101", "TagType": "TK", "TagNumber": "101", "Description": "supply vessel"},
        {"ObjectId": 102, "Tag": "TK-102", "TagType": "TK", "TagNumber": "102", "Description": "receiving vessel"},
    ],
    "Valve": [
        {"ObjectId": 103, "Tag": "XV-101", "TagType": "XV", "TagNumber": "101", "Description": None},
        {"ObjectId": 104, "Tag": "XV-102", "TagType": "XV", "TagNumber": "102", "Description": "bypass branch"},
    ],
    "Instrument": [
        {"ObjectId": 105, "Tag": "PI-102", "TagType": "PI", "LoopNumber": "102", "Description": "pressure indication",
         "Unit": "bar"},
    ],
    "Junction": [{"ObjectId": 106, "Description": "branch junction"}, {"ObjectId": 107, "Description": "branch junction"}],
    "SheetConnector": [{"ObjectId": 108, "Label": "TO-S2/A", "Direction": "Out"},
                       {"ObjectId": 109, "Label": "FROM-S1/A", "Direction": "In"}],
    "LineSegment": [
        {"ObjectId": key, "Tag": f"L-101-{suffix}", "LinePrefix": "L", "LineNumber": "101", "SegmentSuffix": suffix,
         "NominalSizeMm": 50}
        for key, suffix in ((110, "1"), (111, "2"), (112, "3"), (113, "4"), (114, "B"), (115, "5"))
    ],
    "Drawing": [{"DrawingId": 901, "FileName": "DEMO-PID-001", "Revision": "R0", "Status": "Approved"},
                {"DrawingId": 902, "FileName": "DEMO-PID-002", "Revision": "R0", "Status": "Approved"}],
}
PAIR_COLUMNS = {"SegmentStart": ("SegmentId", "ObjectId"), "SegmentEnd": ("SegmentId", "ObjectId"),
                "ConnectorPair": ("Connector1", "Connector2"), "SheetConnectorLink": ("OutConnector", "InConnector"),
                "Ownership": ("OwnerId", "OwnedId")}


def committed(revision: str) -> dict[str, list[dict]]:
    """A revision's rows as the repository holds them, not as the generator would write them."""
    return {table: json.loads((gen.OUT / revision / f"{table}.json").read_text(encoding="utf-8")) for table in gen.TABLES}


def pairs(rows: dict[str, list[dict]], table: str) -> set[tuple[str, str]]:
    alias = {key: name for name, key in EXPECTED_KEYS.items()}
    first, second = PAIR_COLUMNS[table]
    return {(alias[r[first]], alias[r[second]]) for r in rows[table]}


def project(rows: dict[str, list[dict]]) -> tuple[set[int], set[tuple[str, int, int]]]:
    """A snapshot read back as keys and (kind, source key, target key) edges, the way a mapping would.

    Written from the schema's comments, not from the generator's code.
    """
    nodes = {r["ObjectId"] for r in rows["PlantObject"]} | {r["DrawingId"] for r in rows["Drawing"]}
    edges = set()
    edges |= {("FLOW", r["ObjectId"], r["SegmentId"]) for r in rows["SegmentStart"]}
    edges |= {("FLOW", r["SegmentId"], r["ObjectId"]) for r in rows["SegmentEnd"]}
    edges |= {("FLOW", r["Connector1"], r["Connector2"]) for r in rows["ConnectorPair"]}
    for r in rows["SheetConnectorLink"]:
        edges |= {("FLOW", r["OutConnector"], r["InConnector"]),
                  ("CROSS_SHEET_REFERENCE", r["OutConnector"], r["InConnector"])}
    edges |= {("INSTRUMENT_PARENT", r["OwnedId"], r["OwnerId"]) for r in rows["Ownership"]}
    edges |= {("ON_SHEET", r["ObjectId"], r["DrawingId"]) for r in rows["DrawingAppearance"]}
    return nodes, edges


class CommittedFixtureTests(unittest.TestCase):
    """The committed files against hand-written expectations."""

    def test_answer_key_pins_every_key(self):
        self.assertEqual(json.loads(gen.ANSWER_KEY.read_text(encoding="utf-8"))["keys"], EXPECTED_KEYS)

    def test_r0_object_rows_hold_liong006s_values(self):
        rows = committed("R0")
        for table, expected in R0_OBJECT_ROWS.items():
            with self.subTest(table=table):
                self.assertEqual(sorted(rows[table], key=str), sorted(expected, key=str))

    # Written from R0.yaml's revisions: each revision's changes, with LIONG-006's and DEC-050's times
    CHANGE_ROWS = {
        "R0": [],
        "R1": [(102, None, "R1", "Modified", "Tag TK-102 -> TK-202", "2030-01-02T08:00:00")],
        "R2": [(102, None, "R1", "Modified", "Tag TK-102 -> TK-202", "2030-01-02T08:00:00"),
               (None, None, "R2", "Deleted", "FLOW 106 -> 114", "2030-01-03T08:00:00"),
               (None, None, "R2", "Deleted", "FLOW 114 -> 104", "2030-01-03T08:00:00"),
               (None, None, "R2", "Deleted", "FLOW 104 -> 107", "2030-01-03T08:00:00"),
               (104, None, "R2", "Deleted", None, "2030-01-03T08:00:00"),
               (114, None, "R2", "Deleted", None, "2030-01-03T08:00:00")],
        "Rbad": [(104, None, "Rbad", "Deleted", None, "2030-01-01T12:00:00")],
    }
    CLASS_OF = {"E": "Equipment", "V": "Valve", "I": "Instrument", "J": "Junction", "X": "SheetConnector",
                "P": "LineSegment"}

    def test_every_history_row_of_every_revision(self):
        created = [(None if a[0] == "S" else k, k if a[0] == "S" else None, "R0", "Created", None, "2030-01-01T08:00:00")
                   for a, k in EXPECTED_KEYS.items()]
        for revision, changes in self.CHANGE_ROWS.items():
            with self.subTest(revision=revision):
                rows = committed(revision)["WorkHistory"]
                found = [(r["ObjectId"], r["DrawingId"], r["Revision"], r["ChangeKind"], r["Detail"], r["RecordedAt"])
                         for r in rows]
                self.assertEqual(sorted(found, key=str), sorted(created + changes, key=str))
                self.assertEqual([r["HistoryId"] for r in rows], list(range(1, len(rows) + 1)))

    def test_every_plant_object_row_of_every_revision(self):
        # Every column but the GUID and row stamp: key, class, last revision to touch it, status
        world = load(gen.WORLD)
        for revision in ("R0", "R1", "R2", "Rbad"):
            with self.subTest(revision=revision):
                present = state(world, revision).nodes
                expected = {(k, self.CLASS_OF[a[0]], "R1" if a == "E2" and revision in ("R1", "R2") else "R0", "Approved")
                            for a, k in EXPECTED_KEYS.items() if a[0] != "S" and a in present}
                found = {(r["ObjectId"], r["ClassName"], r["Revision"], r["Status"]) for r in committed(revision)["PlantObject"]}
                self.assertEqual(found, expected)

    def test_r0_history_creates_each_object_and_drawing_once(self):
        rows = committed("R0")["WorkHistory"]
        found = sorted((r["ObjectId"] or r["DrawingId"], r["Revision"], r["ChangeKind"], r["Detail"], r["RecordedAt"])
                       for r in rows)
        self.assertEqual(found, sorted((key, "R0", "Created", None, "2030-01-01T08:00:00")
                                       for key in EXPECTED_KEYS.values()))

    def test_plant_object_revision_and_status_follow_the_change(self):
        # Only E2 changes in R1, so only its row moves to R1; every row is approved (DEC-039)
        for revision, moved in (("R0", set()), ("R1", {102})):
            rows = committed(revision)["PlantObject"]
            self.assertEqual({r["ObjectId"] for r in rows if r["Revision"] != "R0"}, moved, revision)
            self.assertEqual({r["Status"] for r in rows}, {"Approved"})
            classes = {r["ObjectId"]: r["ClassName"] for r in rows}
            self.assertEqual({classes[101], classes[103], classes[105], classes[106], classes[108], classes[110]},
                             {"Equipment", "Valve", "Instrument", "Junction", "SheetConnector", "LineSegment"})

    def test_r0_puts_each_connection_in_its_table(self):
        rows = committed("R0")
        self.assertEqual({t: pairs(rows, t) for t in R0_ROWS}, R0_ROWS)

    def test_r2_drops_only_the_bypass_rows(self):
        rows = committed("R2")
        bypass = {"P6", "VB"}
        expected = {t: {p for p in v if not set(p) & bypass} for t, v in R0_ROWS.items()}
        self.assertEqual({t: pairs(rows, t) for t in R0_ROWS}, expected)

    def test_rbad_keeps_every_r0_connection_row_in_its_table(self):
        # Rbad deletes VB but none of its connections, so each table still holds R0's rows
        rows = committed("Rbad")
        self.assertEqual({t: pairs(rows, t) for t in R0_ROWS}, R0_ROWS)
        self.assertNotIn(EXPECTED_KEYS["VB"], {r["ObjectId"] for r in rows["PlantObject"]})

    def test_every_object_keeps_its_key_and_class_in_every_snapshot(self):
        tables = {"E": "Equipment", "V": "Valve", "I": "Instrument", "J": "Junction", "X": "SheetConnector",
                  "P": "LineSegment"}
        for revision in ("R0", "R1", "R2", "Rbad"):
            rows = committed(revision)
            for alias, key in EXPECTED_KEYS.items():
                if alias[0] == "S":
                    continue
                with self.subTest(revision=revision, alias=alias):
                    present = state(load(gen.WORLD), revision).nodes.get(alias) is not None
                    found = [r for r in rows[tables[alias[0]]] if r["ObjectId"] == key]
                    self.assertEqual(len(found), 1 if present else 0)

    def test_r2_history_records_every_change(self):
        rows = [(r["Revision"], r["ChangeKind"], r["ObjectId"], r["Detail"])
                for r in committed("R2")["WorkHistory"] if r["ChangeKind"] != "Created"]
        self.assertEqual(rows, [
            ("R1", "Modified", 102, "Tag TK-102 -> TK-202"),
            ("R2", "Deleted", None, "FLOW 106 -> 114"),
            ("R2", "Deleted", None, "FLOW 114 -> 104"),
            ("R2", "Deleted", None, "FLOW 104 -> 107"),
            ("R2", "Deleted", 104, None),
            ("R2", "Deleted", 114, None),
        ])


class GenerationErrorTests(unittest.TestCase):
    def world(self) -> dict:
        return copy.deepcopy(load(gen.WORLD))

    def test_tag_that_does_not_fit_its_format_stops_generation(self):
        w = self.world()
        w["nodes"]["I1"]["tag"] = "PI-10-2"
        with self.assertRaisesRegex(gen.GenerationError, "does not fit the Instrument tag format"):
            gen.snapshot(w, "R0")

    def test_sheet_connector_flow_without_its_reference_stops_generation(self):
        w = self.world()
        w["edges"]["CROSS_SHEET_REFERENCE"] = []
        with self.assertRaisesRegex(gen.GenerationError, "without a cross-sheet reference"):
            gen.snapshot(w, "R0")

    def test_reference_without_a_flow_stops_generation(self):
        w = self.world()
        w["edges"]["CROSS_SHEET_REFERENCE"].append(["X2", "X1"])
        with self.assertRaisesRegex(gen.GenerationError, "has no flow"):
            gen.snapshot(w, "R0")

    def test_change_the_backend_cannot_record_stops_generation(self):
        w = self.world()
        w["revisions"]["R1"]["changes"].append({"move_node": "E2"})
        with self.assertRaisesRegex(gen.GenerationError, "cannot record"):
            gen.history(w, ["R0", "R1"], EXPECTED_KEYS)

    def test_main_reports_a_generation_error(self):
        original = gen.outputs

        def broken():
            raise gen.GenerationError("broken world")

        gen.outputs = broken
        try:
            self.assertEqual(gen.main([]), 1)
        finally:
            gen.outputs = original


class GeneratorTests(unittest.TestCase):
    world = load(gen.WORLD)
    key = json.loads(FRESH[gen.ANSWER_KEY])["keys"]

    def expected(self, revision: str) -> tuple[set[int], set[tuple[str, int, int]]]:
        s = state(self.world, revision)
        return ({self.key[a] for a in s.nodes},
                {(e.kind, self.key[e.source], self.key[e.target]) for e in s.all_edges()})

    def test_committed_files_are_fresh(self):
        self.assertEqual(gen.main(["--check"]), 0)

    def test_generation_is_deterministic(self):
        self.assertEqual(gen.outputs(), gen.outputs())

    def test_valid_revisions_round_trip_to_the_world(self):
        for revision in ("R0", "R1", "R2"):
            with self.subTest(revision=revision):
                self.assertEqual(project(read(revision)), self.expected(revision))

    def test_r0_and_r2_have_the_published_counts(self):
        # LIONG-006: R0 is 17 nodes and 31 edges; R2 is 15 and 26
        for revision, counts in (("R0", (17, 31)), ("R2", (15, 26))):
            nodes, edges = project(read(revision))
            self.assertEqual((len(nodes), len(edges)), counts, revision)

    def test_rbad_keeps_rows_that_name_a_deleted_object(self):
        nodes, edges = project(read("Rbad"))
        dangling = {(k, s, t) for k, s, t in edges if s not in nodes or t not in nodes}
        vb = self.key["VB"]
        self.assertNotIn(vb, nodes)
        self.assertEqual(dangling, {("FLOW", self.key["P6"], vb), ("FLOW", vb, self.key["J2"])})

    def test_keys_stay_the_same_across_snapshots(self):
        # DEC-044: E2 keeps its row when R1 renames it
        tags = {rev: {r["ObjectId"]: r["Tag"] for r in read(rev)["Equipment"]} for rev in ("R0", "R1")}
        e2 = self.key["E2"]
        self.assertEqual((tags["R0"][e2], tags["R1"][e2]), ("TK-102", "TK-202"))

    def test_rename_is_in_the_work_history(self):
        rows = [r for r in read("R1")["WorkHistory"] if r["ChangeKind"] == "Modified"]
        self.assertEqual([(r["ObjectId"], r["Revision"], r["RecordedAt"]) for r in rows],
                         [(self.key["E2"], "R1", "2030-01-02T08:00:00")])

    def test_tag_subparts_compose_the_tag(self):
        for table, parts in (("Equipment", ("TagType", "TagNumber")), ("Valve", ("TagType", "TagNumber")),
                             ("Instrument", ("TagType", "LoopNumber")),
                             ("LineSegment", ("LinePrefix", "LineNumber", "SegmentSuffix"))):
            for row in read("R0")[table]:
                self.assertEqual("-".join(row[p] for p in parts), row["Tag"], row)

    def test_every_row_is_approved(self):
        # DEC-039: the source approval is the vendor's own status field
        rows = read("R0")
        self.assertEqual({r["Status"] for r in rows["PlantObject"] + rows["Drawing"]}, {"Approved"})

    def test_snapshots_hold_no_alias_or_answer_key(self):
        aliases = set(self.world["nodes"])
        for path, data in FRESH.items():
            if not path.is_relative_to(gen.OUT):
                continue
            values = set()

            def walk(value):
                if isinstance(value, dict):
                    values.update(value)  # keys too: an alias must not appear as a key either
                    for v in value.values():
                        walk(v)
                elif isinstance(value, list):
                    for v in value:
                        walk(v)
                elif isinstance(value, str):
                    values.add(value)

            walk(json.loads(data))
            self.assertFalse(values & aliases, f"{path.name} holds aliases {values & aliases}")
        self.assertFalse(gen.ANSWER_KEY.is_relative_to(gen.OUT))

    def test_manifest_hashes_every_snapshot_file(self):
        manifest = json.loads(FRESH[gen.OUT / "manifest.json"])
        files = {str(p.relative_to(gen.OUT)) for p in FRESH if p.is_relative_to(gen.OUT)} - {"manifest.json"}
        self.assertEqual(set(manifest["files"]), files)
        for name, digest in manifest["files"].items():
            self.assertEqual(hashlib.sha256(FRESH[gen.OUT / name]).hexdigest(), digest, name)
        self.assertIsNone(manifest["seed"])


if __name__ == "__main__":
    unittest.main()
