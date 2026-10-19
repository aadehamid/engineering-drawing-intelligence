#!/usr/bin/env python3
"""Tests for scripts/extract_sps.py.

The expected tags, attributes and edges are typed by hand from worlds/W-SP.yaml and
DEC-085, not computed by the extractor. The main test builds a graph from the records
and scores it with scripts/compare_answer_key.py against W-SP's answer key, which must
match exactly. The database tests need a server: set LIONG_SQLSERVER to
"host,port,user,password"; CI sets it.
"""
from __future__ import annotations

import builtins
import copy
import io
import json
import os
from pathlib import Path
import sys
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_answer_key  # noqa: E402
import dexpi_generate  # noqa: E402
import extract_sps as extract  # noqa: E402
import load_sps as loader  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "fixtures" / "sps-wsp" / "W0"
AT = "2026-10-19T00:00:00+00:00"
RELATIONS = {"starts_at", "ends_at", "continues_to", "owned_by"}


def from_snapshot(rows: dict | None = None) -> dict:
    revision, found = extract.rows_from_snapshot(SNAPSHOT)
    return extract.extract(revision, rows or found, "snapshot:W0", AT)


def snapshot_rows() -> dict:
    return copy.deepcopy(extract.rows_from_snapshot(SNAPSHOT)[1])


def graph(records: dict) -> dict:
    """The graph the records state, in graph_publish.py's shape.

    Relationship predicates become edges as dexpi_generate.edge_of maps them, a
    continuation also becomes a cross-sheet reference, as dexpi_parse.py does, and each
    appearance becomes an ON_SHEET edge.
    """
    nodes = [{"id": o["object_id"], "kind": o["object_kind"]} for o in records["objects"]]
    nodes += [{"id": d["artifact_id"], "kind": "drawing"} for d in records["drawings"]]
    edges = []
    for a in records["assertions"]:
        if a["predicate"] in RELATIONS:
            kind, source, target = dexpi_generate.edge_of(a["predicate"], a["subject_id"], a["value_or_target"])
            edges.append({"kind": kind, "source": source, "target": target})
            if a["predicate"] == "continues_to":
                edges.append({"kind": "CROSS_SHEET_REFERENCE", "source": source, "target": target})
    edges += [{"kind": "ON_SHEET", "source": a["object_id"], "target": a["artifact_id"]} for a in records["appearances"]]
    return {"nodes": nodes, "edges": edges}


def score(records: dict) -> dict:
    key = json.loads((ROOT / "fixtures" / "answer-keys" / "sps-wsp.json").read_text(encoding="utf-8"))
    return compare_answer_key.compare({"outcome": "accepted", "graph": graph(records)}, key, "W0")


def by_tag(records: dict) -> dict[str, str]:
    """Object ID to tag, with sheet links named by their label."""
    names = {t["object_id"]: t["tag_value"] for t in records["tag_assignments"]}
    names |= {a["subject_id"]: a["value_or_target"] for a in records["assertions"] if a["predicate"] == "label"}
    names |= {d["artifact_id"]: d["name"] for d in records["drawings"]}
    return names


# The flow path from W-SP's world file, written by tag, with the cross-sheet pair.
EXPECTED_EDGES = {
    ("FLOW", "TK-301", "L-301-1"), ("FLOW", "L-301-1", "HV-301"), ("FLOW", "HV-301", "L-301-2"),
    ("FLOW", "L-301-2", "HV-302"), ("FLOW", "HV-302", "L-301-3"), ("FLOW", "L-301-3", "TO-S2/B"),
    ("FLOW", "TO-S2/B", "FROM-S1/B"), ("CROSS_SHEET_REFERENCE", "TO-S2/B", "FROM-S1/B"),
    ("FLOW", "FROM-S1/B", "L-301-4"), ("FLOW", "L-301-4", "HV-303"), ("FLOW", "HV-303", "L-301-5"),
    ("FLOW", "L-301-5", "TK-302"), ("INSTRUMENT_PARENT", "LT-302", "TK-302"),
}
SEGMENT = {"line_prefix": "L", "line_number": "301", "nominal_size_mm": 80, "pipeline": "L-301"}


class SnapshotExtractionTest(unittest.TestCase):
    records = from_snapshot()

    def test_the_graph_matches_w_sps_answer_key_exactly(self):
        report = score(self.records)
        self.assertEqual((report["match"], report["differences"]), (True, []))
        self.assertEqual((report["nodes"], report["edges"]), (15, 26))

    def test_edges_by_tag(self):
        names = by_tag(self.records)
        found = {(e["kind"], names[e["source"]], names[e["target"]]) for e in graph(self.records)["edges"]
                 if e["kind"] != "ON_SHEET"}
        self.assertEqual(found, EXPECTED_EDGES)

    def test_objects_and_tags(self):
        kinds = {by_tag(self.records)[o["object_id"]]: o["object_kind"] for o in self.records["objects"]}
        self.assertEqual(kinds, {
            "TK-301": "equipment", "TK-302": "equipment", "HV-301": "valve", "HV-302": "valve", "HV-303": "valve",
            "LT-302": "instrument", "TO-S2/B": "sheet_connector", "FROM-S1/B": "sheet_connector",
            **{f"L-301-{n}": "pipe_segment" for n in range(1, 6)}})

    def test_nozzles_runs_and_process_connections_are_not_objects(self):
        rows = snapshot_rows()
        hidden = {r["ItemGuid"] for t in ("Nozzle", "PipeRun", "ProcessConnection") for r in rows[t]}
        ids = {o["object_id"] for o in self.records["objects"]}
        self.assertFalse({extract.item_id(g) for g in hidden} & ids)

    def test_attributes(self):
        names = by_tag(self.records)
        found: dict[str, dict] = {}
        for a in self.records["assertions"]:
            if a["predicate"] not in RELATIONS | {"run", "label"}:
                found.setdefault(names[a["subject_id"]], {})[a["predicate"]] = a["value_or_target"]
        self.assertEqual(found, {
            "TK-301": {"tag_lead": "TK", "tag_number": "301", "description": "supply vessel"},
            "TK-302": {"tag_lead": "TK", "tag_number": "302", "description": "receiving vessel"},
            "LT-302": {"tag_lead": "LT", "tag_number": "302", "unit": "%", "description": "level transmission"},
            "HV-301": {"description": "inline isolation"}, "HV-302": {"description": "inline isolation"},
            "HV-303": {"description": "inline isolation"},
            "TO-S2/B": {"link_sense": "To"}, "FROM-S1/B": {"link_sense": "From"},
            **{f"L-301-{n}": SEGMENT for n in range(1, 6)}})

    def test_segments_and_fittings_name_their_run(self):
        names = by_tag(self.records)
        runs = {names[a["subject_id"]]: a["value_or_target"] for a in self.records["assertions"] if a["predicate"] == "run"}
        self.assertEqual(set(runs), {"L-301-1", "L-301-2", "L-301-3", "L-301-4", "L-301-5", "HV-301", "HV-302", "HV-303"})
        run_a = {runs[n] for n in ("L-301-1", "L-301-2", "L-301-3", "HV-301", "HV-302")}
        run_b = {runs[n] for n in ("L-301-4", "L-301-5", "HV-303")}
        self.assertEqual((len(run_a), len(run_b)), (1, 1))
        self.assertNotEqual(run_a, run_b)

    def test_drawings_and_appearances(self):
        self.assertEqual(sorted((d["name"], d["revision"], d["status"]) for d in self.records["drawings"]),
                         [("DEMO-PID-101", "W0.0", "Approved"), ("DEMO-PID-102", "W0.0", "Approved")])
        names = by_tag(self.records)
        sheets = {names[a["object_id"]]: names[a["artifact_id"]] for a in self.records["appearances"]}
        on_101 = {"TK-301", "HV-301", "HV-302", "TO-S2/B", "L-301-1", "L-301-2", "L-301-3"}
        self.assertEqual(sheets, {n: "DEMO-PID-101" if n in on_101 else "DEMO-PID-102"
                                  for n in on_101 | {"TK-302", "HV-303", "LT-302", "FROM-S1/B", "L-301-4", "L-301-5"}})

    def test_evidence_status_and_locators(self):
        derived = {a["predicate"] for a in self.records["assertions"] if a["evidence_status"] == "derived"}
        self.assertEqual(derived, RELATIONS | {"line_prefix", "line_number", "nominal_size_mm", "pipeline"})
        names = by_tag(self.records)
        parent = next(a for a in self.records["assertions"] if a["predicate"] == "owned_by")
        self.assertEqual([step["table"] for step in parent["source_locator"]["via"]], ["ProcessConnection", "Nozzle"])
        first = next(a for a in self.records["assertions"]
                     if a["predicate"] == "starts_at" and names[a["subject_id"]] == "L-301-1")
        self.assertEqual([step["table"] for step in first["source_locator"]["via"]], ["PipeRun", "Nozzle"])

    def test_identifiers(self):
        self.assertEqual(self.records["source_revision"], {
            "revision_id": "sps:revision:W0", "source_id": "sps", "snapshot": "complete",
            "recorded_at": "2030-02-01T08:00:00", "approval_ref": "baseline_import"})
        prefixes = {o["object_id"].rsplit(":", 1)[0] for o in self.records["objects"]}
        self.assertEqual(prefixes, {"sps:item", "sps:line"})
        self.assertEqual({d["artifact_id"].rsplit(":", 1)[0] for d in self.records["drawings"]}, {"sps:sheet"})
        for group, field in (("objects", "object_id"), ("assertions", "assertion_id"),
                             ("appearances", "appearance_id"), ("drawings", "artifact_id")):
            identifiers = [record[field] for record in self.records[group]]
            self.assertEqual(len(identifiers), len(set(identifiers)), group)

    def test_extraction_is_repeatable_and_order_free(self):
        rows = snapshot_rows()
        shuffled = {table: list(reversed(table_rows)) for table, table_rows in rows.items()}
        self.assertEqual(from_snapshot(rows), from_snapshot(shuffled))

    def test_extraction_never_opens_an_answer_key(self):
        opened: list[str] = []
        real_open, real_io_open = builtins.open, io.open

        def spy(file, *args, **kwargs):
            opened.append(str(file))
            return real_open(file, *args, **kwargs)

        builtins.open = io.open = spy
        try:
            from_snapshot()
        finally:
            builtins.open, io.open = real_open, real_io_open
        self.assertTrue(opened, "the spy saw no file opened, so it proves nothing")
        self.assertFalse([path for path in opened if "answer-keys" in path])


class DerivationTest(unittest.TestCase):
    """Edit the rows and check each derivation follows them."""

    def test_the_flow_sense_sets_the_direction(self):
        rows = snapshot_rows()
        for run in rows["PipeRun"]:
            run["FlowSense"] = "End1Upstream"  # run B is drawn against its flow
        report = score(from_snapshot(rows))
        self.assertIn("missing edge FLOW P5 E2", report["differences"])
        self.assertIn("extra edge FLOW E2 P5", report["differences"])

    def pipelines(self, rows: dict) -> dict[str, str]:
        records = from_snapshot(rows)
        names = by_tag(records)
        return {names[a["subject_id"]]: a["value_or_target"] for a in records["assertions"] if a["predicate"] == "pipeline"}

    def test_membership_follows_the_line_parts_not_a_key(self):
        rows = snapshot_rows()
        rows["PipeRun"][1]["TagNumber"] = "302"  # run B leaves line 301 and matches no group
        self.assertEqual(self.pipelines(rows), {f"L-301-{n}": "L-301" for n in (1, 2, 3)})
        rows["LineGroup"].append({"GroupGuid": str(uuid.uuid4()).upper(), "TagLead": "L", "TagNumber": "302"})
        self.assertEqual(self.pipelines(rows), {**{f"L-301-{n}": "L-301" for n in (1, 2, 3)},
                                                "L-301-4": "L-302", "L-301-5": "L-302"})

    def test_a_run_with_a_null_key_part_is_in_no_group(self):
        rows = snapshot_rows()
        rows["PipeRun"][1]["TagLead"] = None
        self.assertEqual(set(self.pipelines(rows)), {"L-301-1", "L-301-2", "L-301-3"})

    def test_without_the_group_row_there_is_no_pipeline(self):
        rows = snapshot_rows()
        rows["LineGroup"] = []
        self.assertEqual(self.pipelines(rows), {})

    def test_the_pipeline_evidence_names_the_group_and_its_runs(self):
        records = from_snapshot()
        locators = [a["source_locator"] for a in records["assertions"] if a["predicate"] == "pipeline"]
        self.assertEqual(len(locators), 5)
        self.assertEqual({(loc["table"], len(loc["via"])) for loc in locators}, {("LineGroup", 2)})

    def test_sheet_links_that_disagree_stop_extraction(self):
        for column, value in (("MateItem", str(uuid.uuid4()).upper()), ("MateSheet", str(uuid.uuid4()).upper())):
            with self.subTest(column=column):
                rows = snapshot_rows()
                rows["SheetLink"][1][column] = value
                with self.assertRaises(extract.ExtractionError):
                    from_snapshot(rows)

    def test_a_deleted_item_is_not_an_object(self):
        rows = snapshot_rows()
        vessel = rows["Vessel"][0]["ItemGuid"]
        next(r for r in rows["DesignItem"] if r["ItemGuid"] == vessel)["ItemState"] = "Deleted"
        records = from_snapshot(rows)
        self.assertNotIn(extract.item_id(vessel), {o["object_id"] for o in records["objects"]})
        # The segment that reaches its nozzle still names it, for validation to reject
        self.assertIn(extract.item_id(vessel), {a["value_or_target"] for a in records["assertions"]})


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
        self.database = f"liong_extract_sps_{uuid.uuid4().hex[:8]}"
        self.admin.cursor().execute(f"CREATE DATABASE {self.database}")
        self.conn = loader.connect(f"{host},{port},{user},{password},{self.database}")
        loader.create(self.conn)

    def tearDown(self):
        self.conn.close()
        self.admin.cursor().execute(f"ALTER DATABASE {self.database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.admin.cursor().execute(f"DROP DATABASE {self.database}")
        self.admin.close()

    def test_an_empty_backend_has_nothing_to_extract(self):
        with self.assertRaises(loader.LoadError):
            extract.rows_from_database(self.conn)

    def test_database_and_snapshot_give_the_same_records(self):
        loader.load(self.conn, SNAPSHOT)
        revision, rows = extract.rows_from_database(self.conn)
        self.conn.commit()
        records = extract.extract(revision, rows, "x", AT)
        self.assertEqual(records, extract.extract(*extract.rows_from_snapshot(SNAPSHOT), "x", AT))
        self.assertTrue(score(records)["match"])


if __name__ == "__main__":
    unittest.main()
