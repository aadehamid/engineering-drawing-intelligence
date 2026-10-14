#!/usr/bin/env python3
"""Tests for scripts/extract_p3d.py.

The expected records are typed by hand from LIONG-006's R0 (TK-101 feeds L-101-1 to the
first junction, and so on), not computed by the extractor. The database tests need a
server: set LIONG_SQLSERVER to "host,port,user,password"; CI sets it.
"""
from __future__ import annotations

import builtins
import io
import os
from pathlib import Path
import sys
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_p3d as extract  # noqa: E402
import load_p3d as loader  # noqa: E402

SNAPSHOTS = loader.ROOT / "fixtures" / "p3d-r0"
AT = "2026-10-14T00:00:00+00:00"

R0_KINDS = {
    101: "equipment", 102: "equipment", 103: "valve", 104: "valve", 105: "instrument",
    106: "junction", 107: "junction", 108: "sheet_connector", 109: "sheet_connector",
    110: "pipe_segment", 111: "pipe_segment", 112: "pipe_segment", 113: "pipe_segment",
    114: "pipe_segment", 115: "pipe_segment",
}
R0_TAGS = {
    101: "TK-101", 102: "TK-102", 103: "XV-101", 104: "XV-102", 105: "PI-102",
    110: "L-101-1", 111: "L-101-2", 112: "L-101-3", 113: "L-101-4", 114: "L-101-B", 115: "L-101-5",
}
# (subject key, predicate, target key) for every relationship row in R0.
R0_RELATIONS = {
    (110, "starts_at", 101), (110, "ends_at", 106),
    (111, "starts_at", 106), (111, "ends_at", 103),
    (112, "starts_at", 103), (112, "ends_at", 107),
    (113, "starts_at", 107), (113, "ends_at", 108),
    (114, "starts_at", 106), (114, "ends_at", 104),
    (115, "starts_at", 109), (115, "ends_at", 102),
    (104, "connects_to", 107),
    (108, "continues_to", 109),
    (105, "owned_by", 102),
}
# Each relationship row's assertion ID, as (table/RowId): (subject key, predicate, target key).
R0_RELATION_ROWS = {
    "SegmentStart/1": (110, "starts_at", 101), "SegmentStart/2": (111, "starts_at", 106),
    "SegmentStart/3": (114, "starts_at", 106), "SegmentStart/4": (113, "starts_at", 107),
    "SegmentStart/5": (112, "starts_at", 103), "SegmentStart/6": (115, "starts_at", 109),
    "SegmentEnd/1": (110, "ends_at", 106), "SegmentEnd/2": (111, "ends_at", 103),
    "SegmentEnd/3": (112, "ends_at", 107), "SegmentEnd/4": (113, "ends_at", 108),
    "SegmentEnd/5": (115, "ends_at", 102), "SegmentEnd/6": (114, "ends_at", 104),
    "ConnectorPair/1": (104, "connects_to", 107),
    "SheetConnectorLink/1": (108, "continues_to", 109),
    "Ownership/1": (105, "owned_by", 102),
}
# Every attribute R0's class rows state; XV-101's description is null and so absent.
R0_ATTRIBUTES = {
    (101, "tag_type"): "TK", (101, "tag_number"): "101", (101, "description"): "supply vessel",
    (102, "tag_type"): "TK", (102, "tag_number"): "102", (102, "description"): "receiving vessel",
    (103, "tag_type"): "XV", (103, "tag_number"): "101",
    (104, "tag_type"): "XV", (104, "tag_number"): "102", (104, "description"): "bypass branch",
    (105, "tag_type"): "PI", (105, "loop_number"): "102", (105, "unit"): "bar",
    (105, "description"): "pressure indication",
    (106, "description"): "branch junction", (107, "description"): "branch junction",
    (108, "label"): "TO-S2/A", (108, "direction"): "Out",
    (109, "label"): "FROM-S1/A", (109, "direction"): "In",
    **{(segment, "line_prefix"): "L" for segment in range(110, 116)},
    **{(segment, "line_number"): "101" for segment in range(110, 116)},
    **{(segment, "nominal_size_mm"): 50 for segment in range(110, 116)},
    (110, "segment_suffix"): "1", (111, "segment_suffix"): "2", (112, "segment_suffix"): "3",
    (113, "segment_suffix"): "4", (114, "segment_suffix"): "B", (115, "segment_suffix"): "5",
}
SHEET_2 = {102, 105, 109, 115}
R0_APPEARANCES = {key: (902 if key in SHEET_2 else 901) for key in R0_KINDS}


PREDICATES = {"starts_at", "ends_at", "connects_to", "continues_to", "owned_by"}


def key(identifier: str) -> int:
    return int(identifier.rsplit(":", 1)[1])


def relations(records: dict) -> set[tuple[int, str, int]]:
    return {(key(a["subject_id"]), a["predicate"], key(a["value_or_target"]))
            for a in records["assertions"] if a["predicate"] in {"starts_at", "ends_at", "connects_to",
                                                                  "continues_to", "owned_by"}}


def from_snapshot(revision: str) -> dict:
    name, rows = extract.rows_from_snapshot(SNAPSHOTS / revision)
    return extract.extract(name, rows, f"snapshot:{revision}", AT)


class SnapshotExtractionTest(unittest.TestCase):
    def test_r0_objects_and_kinds(self):
        records = from_snapshot("R0")
        self.assertEqual({key(o["object_id"]): o["object_kind"] for o in records["objects"]}, R0_KINDS)

    def test_r0_tags(self):
        records = from_snapshot("R0")
        self.assertEqual({key(t["object_id"]): t["tag_value"] for t in records["tag_assignments"]}, R0_TAGS)

    def test_r0_relationships(self):
        self.assertEqual(relations(from_snapshot("R0")), R0_RELATIONS)

    def test_r0_drawings_and_appearances(self):
        records = from_snapshot("R0")
        self.assertEqual([(d["artifact_id"], d["name"]) for d in records["drawings"]],
                         [("p3d:drawing:901", "DEMO-PID-001"), ("p3d:drawing:902", "DEMO-PID-002")])
        self.assertEqual({key(a["object_id"]): key(a["artifact_id"]) for a in records["appearances"]}, R0_APPEARANCES)

    def test_r0_attributes(self):
        values = {(key(a["subject_id"]), a["predicate"]): a["value_or_target"]
                  for a in from_snapshot("R0")["assertions"] if a["predicate"] not in PREDICATES}
        self.assertEqual(values, R0_ATTRIBUTES)

    def test_each_relationship_names_its_row(self):
        found = {a["assertion_id"]: ((key(a["subject_id"]), a["predicate"], key(a["value_or_target"])),
                                     a["source_locator"])
                 for a in from_snapshot("R0")["assertions"] if a["predicate"] in PREDICATES}
        expected = {aid: (relation, {"table": aid.split("/")[0], "RowId": int(aid.split("/")[1])})
                    for aid, relation in R0_RELATION_ROWS.items()}
        self.assertEqual(found, expected)

    def test_each_attribute_names_its_class_row(self):
        tables = {"equipment": "Equipment", "valve": "Valve", "instrument": "Instrument", "junction": "Junction",
                  "sheet_connector": "SheetConnector", "pipe_segment": "LineSegment"}
        for a in from_snapshot("R0")["assertions"]:
            if a["predicate"] not in PREDICATES:
                subject = key(a["subject_id"])
                self.assertEqual(a["source_locator"], {"table": tables[R0_KINDS[subject]], "ObjectId": subject})

    def test_each_fact_is_one_record(self):
        records = from_snapshot("R0")
        counts = {group: len(records[group]) for group in ("objects", "tag_assignments", "assertions",
                                                            "drawings", "appearances")}
        # 15 objects, 11 tags, 45 attributes plus 15 relationship rows, 2 drawings, 15 appearances.
        self.assertEqual(counts, {"objects": 15, "tag_assignments": 11, "assertions": 60,
                                  "drawings": 2, "appearances": 15})
        for group, field in (("objects", "object_id"), ("assertions", "assertion_id"),
                             ("appearances", "appearance_id"), ("drawings", "artifact_id")):
            identifiers = [record[field] for record in records[group]]
            self.assertEqual(len(identifiers), len(set(identifiers)), group)

    def test_record_shapes_and_identifiers(self):
        records = from_snapshot("R0")
        self.assertEqual(records["source_revision"], {
            "revision_id": "p3d:revision:R0", "source_id": "p3d", "snapshot": "complete",
            "recorded_at": "2030-01-01T08:00:00", "approval_ref": "baseline_import"})
        self.assertEqual(records["objects"][0], {
            "object_id": "p3d:object:101", "object_kind": "equipment", "source_object_key": 101,
            "source_locator": {"table": "PlantObject", "ObjectId": 101}})
        self.assertEqual(records["tag_assignments"][0], {
            "object_id": "p3d:object:101", "namespace": "p3d", "tag_value": "TK-101",
            "revision_id": "p3d:revision:R0", "source_locator": {"table": "Equipment", "ObjectId": 101}})
        self.assertEqual(records["appearances"][0], {
            "appearance_id": "p3d:appearance:1", "object_id": "p3d:object:101", "artifact_id": "p3d:drawing:901",
            "region": "305", "coordinate_system": "p3d_drawing_handle",
            "source_locator": {"table": "DrawingAppearance", "RowId": 1}})
        self.assertEqual(records["drawings"][0], {
            "artifact_id": "p3d:drawing:901", "name": "DEMO-PID-001", "revision": "R0", "status": "Approved",
            "source_locator": {"table": "Drawing", "DrawingId": 901}})
        self.assertEqual({a["evidence_status"] for a in records["assertions"]}, {"source_stated"})
        self.assertEqual(records["source_manifest"]["captured_at"], AT)

    def test_rbad_keeps_the_dangling_rows_for_validation(self):
        records = from_snapshot("Rbad")
        self.assertNotIn(104, {key(o["object_id"]) for o in records["objects"]})
        self.assertIn((114, "ends_at", 104), relations(records))
        self.assertIn((104, "connects_to", 107), relations(records))

    def test_extraction_is_repeatable_and_order_free(self):
        name, rows = extract.rows_from_snapshot(SNAPSHOTS / "R1")
        shuffled = {table: list(reversed(table_rows)) for table, table_rows in rows.items()}
        self.assertEqual(extract.extract(name, rows, "x", AT), extract.extract(name, shuffled, "x", AT))

    def test_baseline_has_no_change_approval(self):
        self.assertEqual(from_snapshot("R0")["source_revision"]["approval_ref"], "baseline_import")
        self.assertIsNone(from_snapshot("R1")["source_revision"]["approval_ref"])

    def test_extraction_never_opens_an_answer_key(self):
        opened: list[str] = []
        real_open, real_io_open = builtins.open, io.open

        def spy(file, *args, **kwargs):
            opened.append(str(file))
            return real_open(file, *args, **kwargs)

        builtins.open = io.open = spy
        try:
            for revision in ("R0", "R1", "R2", "Rbad"):
                from_snapshot(revision)
        finally:
            builtins.open, io.open = real_open, real_io_open
        self.assertTrue(opened, "the spy saw no file opened, so it proves nothing")
        self.assertFalse([path for path in opened if "answer-keys" in path])


def server() -> str | None:
    return os.environ.get("LIONG_SQLSERVER")


@unittest.skipUnless(server(), "LIONG_SQLSERVER is not set; CI runs these against SQL Server")
class DatabaseExtractionTest(unittest.TestCase):
    def setUp(self):
        import pytds

        host, port, user, password = server().split(",", 3)
        for attempt in range(60):  # a fresh SQL Server container takes several seconds to accept logins
            try:
                self.admin = pytds.connect(dsn=host, port=int(port), user=user, password=password, autocommit=True)
                break
            except (pytds.Error, OSError):
                if attempt == 59:
                    raise
                time.sleep(2)
        self.database = f"liong_extract_{uuid.uuid4().hex[:8]}"
        self.admin.cursor().execute(f"CREATE DATABASE {self.database}")
        self.conn = loader.connect(f"{host},{port},{user},{password},{self.database}")
        loader.create(self.conn)

    def tearDown(self):
        self.conn.close()
        self.admin.cursor().execute(f"ALTER DATABASE {self.database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.admin.cursor().execute(f"DROP DATABASE {self.database}")
        self.admin.close()

    def from_database(self) -> dict:
        name, rows = extract.rows_from_database(self.conn)
        self.conn.commit()
        return extract.extract(name, rows, "x", AT)

    def test_an_empty_backend_has_nothing_to_extract(self):
        with self.assertRaises(loader.LoadError):
            extract.rows_from_database(self.conn)

    def test_database_and_snapshot_give_the_same_records(self):
        for revision in ("R0", "R1", "R2"):
            with self.subTest(revision=revision):
                loader.load(self.conn, SNAPSHOTS / revision)
                name, rows = extract.rows_from_snapshot(SNAPSHOTS / revision)
                self.assertEqual(self.from_database(), extract.extract(name, rows, "x", AT))

    def test_r0_from_the_database_matches_the_hand_written_records(self):
        loader.load(self.conn, SNAPSHOTS / "R0")
        records = self.from_database()
        self.assertEqual(relations(records), R0_RELATIONS)
        self.assertEqual({key(t["object_id"]): t["tag_value"] for t in records["tag_assignments"]}, R0_TAGS)


if __name__ == "__main__":
    unittest.main()
