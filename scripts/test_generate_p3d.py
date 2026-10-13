#!/usr/bin/env python3
"""Tests for the Plant 3D-style generator: fresh files, a faithful round trip, and no leaked truth."""
from __future__ import annotations

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
