#!/usr/bin/env python3
"""Tests for the SmartPlant-style generator: fresh files, W-SP stored as DEC-081 says, no leaked truth.

The expected rows are written by hand from worlds/W-SP.yaml, DEC-081 and DEC-083. GUIDs
cannot be typed by hand, so the tests follow them through the rows to the tags and
labels they lead to, and compare those with the hand-written values.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_sps as gen  # noqa: E402
from world import load  # noqa: E402

FRESH = gen.outputs()  # a generation in memory; test_committed_files_are_fresh ties it to the files
GUID = re.compile(r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}")


def read(revision: str = "W0") -> dict[str, list[dict]]:
    return {table: json.loads(FRESH[gen.OUT / revision / f"{table}.json"]) for table in gen.TABLES}


ROWS = read()


def names() -> dict[str, str]:
    """A readable name for every item, depiction and sheet GUID, found through the rows.

    Vessels, fittings and instruments are named by tag, sheet links by label, runs by
    their segments' labels, nozzles as VESSEL/NOZZLE, sheets by number, marks and lines
    by what they depict.
    """
    found = {}
    for table in ("Vessel", "PipingFitting", "Instrument"):
        found |= {r["ItemGuid"]: r["ItemTag"] for r in ROWS[table]}
    found |= {r["ItemGuid"]: r["LinkLabel"] for r in ROWS["SheetLink"]}
    found |= {r["SheetGuid"]: r["SheetNo"] for r in ROWS["Sheet"]}
    found |= {r["ItemGuid"]: f"{found[r['ParentItem']]}/{r['ItemTag']}" for r in ROWS["Nozzle"]}
    found |= {r["ItemGuid"]: "process connection" for r in ROWS["ProcessConnection"]}
    labels = {r["LabelledDepiction"]: r["LabelText"] for r in ROWS["LabelDepiction"]}
    depicted = {d["DepictionGuid"]: d["ItemGuid"] for d in ROWS["Depiction"]}
    for run in ROWS["PipeRun"]:
        pieces = sorted(labels[d] for d, item in depicted.items() if item == run["ItemGuid"] and d in labels)
        found[run["ItemGuid"]] = "run " + ",".join(pieces)
    for d in ROWS["Depiction"]:
        if d["DepictionKind"] == "Mark":
            found[d["DepictionGuid"]] = "mark " + found[d["ItemGuid"]]
        elif d["DepictionKind"] == "Line":
            found[d["DepictionGuid"]] = labels.get(d["DepictionGuid"], "line " + found[d["ItemGuid"]])
    return found


NAME = names()
RUN_A, RUN_B = "run L-301-1,L-301-2,L-301-3", "run L-301-4,L-301-5"


class SnapshotRowsTest(unittest.TestCase):
    def test_row_counts(self):
        # 14 items: 2 vessels, 3 fittings, 1 instrument, 2 sheet links, 2 runs, 3 nozzles and
        # 1 process connection. 22 depictions: 11 marks, 6 lines and 5 labels. 10 port points:
        # 2 on each fitting and 1 on the instrument and on each nozzle.
        self.assertEqual({table: len(rows) for table, rows in ROWS.items()}, {
            "DesignItem": 14, "Vessel": 2, "Instrument": 1, "PipeRun": 2, "PipingFitting": 3, "Nozzle": 3,
            "ProcessConnection": 1, "SheetLink": 2, "LineGroup": 1, "Depiction": 22, "LineDepiction": 6, "LabelDepiction": 5,
            "InlinePlacement": 3, "PortPoint": 10, "Sheet": 2, "SheetRevision": 2})

    def test_every_key_is_an_upper_case_guid_and_unique_in_its_table(self):
        for table, rows in ROWS.items():
            keys = [r[next(iter(r))] for r in rows]
            self.assertTrue(all(GUID.fullmatch(k) for k in keys), table)
            self.assertEqual(len(keys), len(set(keys)), table)

    def test_class_rows_share_their_base_rows_keys(self):
        classes = ("Vessel", "Instrument", "PipeRun", "PipingFitting", "Nozzle", "ProcessConnection", "SheetLink")
        self.assertEqual(sorted(r["ItemGuid"] for t in classes for r in ROWS[t]),
                         sorted(r["ItemGuid"] for r in ROWS["DesignItem"]))
        kinds = {r["DepictionGuid"]: r["DepictionKind"] for r in ROWS["Depiction"]}
        self.assertEqual({kinds[r["DepictionGuid"]] for r in ROWS["LineDepiction"]}, {"Line"})
        self.assertEqual({kinds[r["DepictionGuid"]] for r in ROWS["LabelDepiction"]}, {"Label"})

    def test_items_and_their_kinds(self):
        kinds = sorted((NAME[r["ItemGuid"]], r["ItemKind"], r["ItemState"]) for r in ROWS["DesignItem"])
        self.assertEqual(kinds, sorted([
            ("TK-301", "Vessel", "Active"), ("TK-302", "Vessel", "Active"),
            ("HV-301", "PipingFitting", "Active"), ("HV-302", "PipingFitting", "Active"),
            ("HV-303", "PipingFitting", "Active"), ("LT-302", "Instrument", "Active"),
            ("TO-S2/B", "SheetLink", "Active"), ("FROM-S1/B", "SheetLink", "Active"),
            (RUN_A, "PipeRun", "Active"), (RUN_B, "PipeRun", "Active"),
            ("TK-301/N1", "Nozzle", "Active"), ("TK-302/N1", "Nozzle", "Active"), ("TK-302/N2", "Nozzle", "Active"),
            ("process connection", "ProcessConnection", "Active")]))

    def test_tagged_rows(self):
        strip = lambda rows: [{k: v for k, v in r.items() if k != "ItemGuid"} for r in rows]  # noqa: E731
        self.assertEqual(strip(ROWS["Vessel"]), [
            {"ItemTag": "TK-301", "TagLead": "TK", "TagNumber": "301", "TagTail": None, "Description": "supply vessel"},
            {"ItemTag": "TK-302", "TagLead": "TK", "TagNumber": "302", "TagTail": None, "Description": "receiving vessel"}])
        self.assertEqual(strip(ROWS["Instrument"]), [
            {"ItemTag": "LT-302", "TagLead": "LT", "TagNumber": "302", "TagTail": None, "Unit": "%",
             "Description": "level transmission"}])
        self.assertEqual(strip(ROWS["PipingFitting"]), [
            {"ItemTag": f"HV-30{n}", "Description": "inline isolation"} for n in (1, 2, 3)])

    def test_both_runs_carry_line_301_and_one_is_drawn_against_its_flow(self):
        runs = {NAME[r["ItemGuid"]]: {k: v for k, v in r.items() if k != "ItemGuid"} for r in ROWS["PipeRun"]}
        line = {"ItemTag": "L-301", "TagLead": "L", "TagNumber": "301", "TagTail": None, "NominalSizeMm": 80}
        self.assertEqual(runs, {RUN_A: line | {"FlowSense": "End1Upstream"},
                                RUN_B: line | {"FlowSense": "End2Upstream"}})

    def test_line_depictions_split_at_each_fitting(self):
        # (run, sheet, end 1, end 2) for each line, in drawing order. Run B is drawn from
        # its downstream end, so its end 2 is upstream.
        found = {}
        depiction = {d["DepictionGuid"]: d for d in ROWS["Depiction"]}
        for line in ROWS["LineDepiction"]:
            d = depiction[line["DepictionGuid"]]
            found[NAME[line["DepictionGuid"]]] = (NAME[d["ItemGuid"]], NAME[d["SheetGuid"]],
                                                  NAME.get(line["End1Item"]), NAME.get(line["End2Item"]))
        self.assertEqual(found, {
            "L-301-1": (RUN_A, "DEMO-PID-101", "TK-301/N1", "HV-301"),
            "L-301-2": (RUN_A, "DEMO-PID-101", "HV-301", "HV-302"),
            "L-301-3": (RUN_A, "DEMO-PID-101", "HV-302", "TO-S2/B"),
            "L-301-4": (RUN_B, "DEMO-PID-102", "HV-303", "FROM-S1/B"),
            "L-301-5": (RUN_B, "DEMO-PID-102", "TK-302/N1", "HV-303"),
            "line process connection": ("process connection", "DEMO-PID-102", "LT-302", "TK-302/N2"),
        })

    def test_marks_and_labels_sit_on_their_sheets(self):
        sheets = {NAME[d["DepictionGuid"]]: NAME[d["SheetGuid"]] for d in ROWS["Depiction"] if d["DepictionKind"] == "Mark"}
        on_101 = {"TK-301", "HV-301", "HV-302", "TO-S2/B", "TK-301/N1"}
        on_102 = {"TK-302", "HV-303", "LT-302", "FROM-S1/B", "TK-302/N1", "TK-302/N2"}
        self.assertEqual(sheets, {f"mark {n}": "DEMO-PID-101" for n in on_101} | {f"mark {n}": "DEMO-PID-102" for n in on_102})
        labels = [d for d in ROWS["Depiction"] if d["DepictionKind"] == "Label"]
        self.assertTrue(all(d["ItemGuid"] is None for d in labels))
        self.assertEqual(sorted(r["LabelText"] for r in ROWS["LabelDepiction"]), [f"L-301-{n}" for n in range(1, 6)])

    def test_inline_placements_name_each_fittings_run(self):
        self.assertEqual({NAME[r["ItemGuid"]]: NAME[r["RunGuid"]] for r in ROWS["InlinePlacement"]},
                         {"HV-301": RUN_A, "HV-302": RUN_A, "HV-303": RUN_B})

    def test_port_points(self):
        points = sorted((NAME[r["OwnerItem"]], r["PointNo"]) for r in ROWS["PortPoint"])
        self.assertEqual(points, sorted([("HV-301", 1), ("HV-301", 2), ("HV-302", 1), ("HV-302", 2), ("HV-303", 1),
                                         ("HV-303", 2), ("LT-302", 1), ("TK-301/N1", 1), ("TK-302/N1", 1),
                                         ("TK-302/N2", 1)]))

    def test_sheet_links_point_at_each_other(self):
        links = {r["LinkLabel"]: (r["LinkSense"], NAME[r["MateItem"]], NAME[r["MateSheet"]]) for r in ROWS["SheetLink"]}
        self.assertEqual(links, {"TO-S2/B": ("To", "FROM-S1/B", "DEMO-PID-102"),
                                 "FROM-S1/B": ("From", "TO-S2/B", "DEMO-PID-101")})

    def test_one_line_group_holds_line_301s_key_and_nothing_points_to_it(self):
        self.assertEqual([{k: v for k, v in r.items() if k != "GroupGuid"} for r in ROWS["LineGroup"]],
                         [{"TagLead": "L", "TagNumber": "301"}])
        group = ROWS["LineGroup"][0]["GroupGuid"]
        text = "".join(FRESH[gen.OUT / "W0" / f"{table}.json"].decode() for table in gen.TABLES if table != "LineGroup")
        self.assertNotIn(group, text)

    def test_no_row_records_the_flow_between_sheets(self):
        text = "".join(FRESH[gen.OUT / "W0" / f"{table}.json"].decode() for table in gen.TABLES).lower()
        self.assertNotIn("flow", text.replace("flowsense", ""))

    def test_sheets_and_revisions(self):
        self.assertEqual(sorted(r["SheetNo"] for r in ROWS["Sheet"]), ["DEMO-PID-101", "DEMO-PID-102"])
        revisions = [(NAME[r["SheetGuid"]], r["MajorRev"], r["MinorRev"], r["RevisedOn"], r["Approver"], r["ApprovedOn"])
                     for r in ROWS["SheetRevision"]]
        # DEC-039: the approval is the revision's approver and approval date (DEC-083)
        self.assertEqual(revisions, [("DEMO-PID-101", "W0", "0", "2030-02-01T08:00:00", "DEMO-APPROVER", "2030-02-01T08:00:00"),
                                     ("DEMO-PID-102", "W0", "0", "2030-02-01T08:00:00", "DEMO-APPROVER", "2030-02-01T08:00:00")])

    def test_every_row_has_exactly_its_schema_columns(self):
        ddl = gen.SCHEMA.read_text(encoding="utf-8")
        for table, rows in ROWS.items():
            body = re.search(rf"CREATE TABLE sps\.{table} \((.*?)\n\);", ddl, re.DOTALL).group(1)
            columns = re.findall(r"^\s+(\w+)\s+(?:INT|NVARCHAR|UNIQUEIDENTIFIER|DATETIME2)", body, re.MULTILINE)
            for row in rows:
                self.assertEqual(list(row), columns, table)


# The answer key's view of W0, written out by hand from worlds/W-SP.yaml.
W0_NODES = ["E1", "E2", "I1", "P1", "P2", "P3", "P4", "P5", "S1", "S2", "V1", "V2", "V3", "X1", "X2"]
W0_EDGES = sorted(
    [["FLOW", a, b] for a, b in (("E1", "P1"), ("P1", "V1"), ("V1", "P2"), ("P2", "V2"), ("V2", "P3"), ("P3", "X1"),
                                 ("X1", "X2"), ("X2", "P4"), ("P4", "V3"), ("V3", "P5"), ("P5", "E2"))]
    + [["INSTRUMENT_PARENT", "I1", "E2"], ["CROSS_SHEET_REFERENCE", "X1", "X2"]]
    + [["ON_SHEET", a, "S1"] for a in ("E1", "V1", "V2", "X1", "P1", "P2", "P3")]
    + [["ON_SHEET", a, "S2"] for a in ("E2", "V3", "I1", "X2", "P4", "P5")])


class AnswerKeyTest(unittest.TestCase):
    key = json.loads(FRESH[gen.ANSWER_KEY])

    def test_view_of_w0(self):
        self.assertEqual(self.key["revisions"], {"W0": {"expected": "accepted", "reason": None,
                                                         "nodes": W0_NODES, "edges": W0_EDGES}})
        self.assertEqual((self.key["world"], self.key["backend"]), ("W-SP", "sps"))

    def test_keys_lead_to_the_right_rows(self):
        found = {alias: NAME[key] for alias, key in self.key["keys"].items()}
        self.assertEqual(found, {
            "E1": "TK-301", "E2": "TK-302", "V1": "HV-301", "V2": "HV-302", "V3": "HV-303", "I1": "LT-302",
            "X1": "TO-S2/B", "X2": "FROM-S1/B", "P1": "L-301-1", "P2": "L-301-2", "P3": "L-301-3",
            "P4": "L-301-4", "P5": "L-301-5", "S1": "DEMO-PID-101", "S2": "DEMO-PID-102"})

    def test_no_snapshot_file_holds_an_alias_or_the_key(self):
        aliases = re.compile(r'"(?:E[12]|V[123]|I1|X[12]|P[1-5]|S[12]|W-SP)"')
        for path, data in FRESH.items():
            if path.is_relative_to(gen.OUT / "W0"):
                self.assertIsNone(aliases.search(data.decode()), path.name)
        self.assertFalse(gen.ANSWER_KEY.is_relative_to(gen.OUT))


class GeneratorTest(unittest.TestCase):
    def test_committed_files_are_fresh(self):
        self.assertEqual(gen.main(["--check"]), 0)
        self.assertEqual(sorted(p for p in gen.OUT.rglob("*") if p.is_file()),
                         sorted(p for p in FRESH if p.is_relative_to(gen.OUT)))

    def test_the_answer_key_folder_holds_only_the_two_generators_keys(self):
        # Each generator's --check sweeps only its own snapshot folder, so this test owns
        # fixtures/answer-keys/: a stray or leftover key there fails here.
        import generate_p3d

        self.assertEqual(sorted(p for p in gen.ANSWER_KEY.parent.rglob("*") if p.is_file()),
                         sorted([gen.ANSWER_KEY, generate_p3d.ANSWER_KEY]))

    def test_generation_is_deterministic(self):
        self.assertEqual(gen.outputs(), FRESH)

    def test_manifest_lists_every_snapshot_file_and_the_inputs(self):
        manifest = json.loads(FRESH[gen.OUT / "manifest.json"])
        self.assertEqual(sorted(manifest["files"]), sorted(f"W0/{t}.json" for t in gen.TABLES))
        self.assertEqual(sorted(manifest["inputs"]), ["schemas/smartplant-style.sql", "scripts/generate_sps.py",
                                                      "uv.lock", "worlds/W-SP.yaml"])
        self.assertEqual(manifest["revisions"], {"W0": {"base": None, "moc": None, "recorded_at": "2030-02-01T08:00:00"}})
        self.assertEqual((manifest["backend"], manifest["world"], manifest["seed"]), ("sps", "W-SP", None))

    def refuses(self, change) -> None:
        world = copy.deepcopy(load(gen.WORLD))
        change(world)
        with self.assertRaises(gen.GenerationError):
            gen.snapshot(world, "W0")

    def test_refuses_a_run_whose_segments_disagree(self):
        self.refuses(lambda w: w["nodes"]["P2"]["attributes"].update(nominal_diameter_mm=100))

    def test_refuses_a_fitting_between_two_runs(self):
        self.refuses(lambda w: w["nodes"]["P2"]["attributes"].update(run="B"))

    def test_refuses_a_sheet_pair_without_its_flow(self):
        self.refuses(lambda w: w["edges"]["FLOW"].remove(["X1", "X2"]))


if __name__ == "__main__":
    unittest.main()
