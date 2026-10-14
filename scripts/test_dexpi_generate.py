#!/usr/bin/env python3
"""Tests for scripts/dexpi_generate.py.

The records come from the R0 snapshot through extract_p3d.py. The expected classes, IDs,
ends and values are typed by hand from LIONG-006's R0 and DEC-077's mapping: TK-101 feeds
L-101-1 to the first junction, the bypass valve XV-102 bolts straight onto the second
junction, and L-101-4 leaves sheet 1 through the off-page connector TO-S2/A.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dexpi_generate as gen  # noqa: E402
import extract_p3d as extract  # noqa: E402

SNAPSHOTS = Path(__file__).resolve().parent.parent / "fixtures" / "p3d-r0"
AT = "2026-10-14T00:00:00+00:00"


def records(revision: str) -> dict:
    stated, rows = extract.rows_from_snapshot(SNAPSHOTS / revision)
    return extract.extract(stated, rows, f"snapshot:fixtures/p3d-r0/{revision}", AT)


def objects(xml: bytes) -> dict[str, etree._Element]:
    return {o.get("id"): o for o in etree.fromstring(xml).iter("Object") if o.get("id")}


def ref(o: etree._Element, prop: str) -> str:
    return o.find(f"References[@property='{prop}']").get("objects")


def text(o: etree._Element, prop: str) -> str | None:
    return o.findtext(f"Data[@property='{prop}']/String")


S1_CLASSES = {
    "Equipment_101": "Plant/ProcessEquipment.Tank", "Valve_103": "Plant/Piping.OperatedValve",
    "Valve_104": "Plant/Piping.OperatedValve", "Junction_106": "Plant/Piping.PipeTee",
    "Junction_107": "Plant/Piping.PipeTee", "SheetConnector_108": "Plant/Piping.FlowOutPipeOffPageConnector",
    "LineSegment_110": "Plant/Piping.PipingNetworkSegment", "LineSegment_111": "Plant/Piping.PipingNetworkSegment",
    "LineSegment_112": "Plant/Piping.PipingNetworkSegment", "LineSegment_113": "Plant/Piping.PipingNetworkSegment",
    "LineSegment_114": "Plant/Piping.PipingNetworkSegment",
}
S2_CLASSES = {
    "Equipment_102": "Plant/ProcessEquipment.Tank",
    "Instrument_105": "Plant/Instrumentation.ProcessInstrumentationFunction",
    "SheetConnector_109": "Plant/Piping.FlowInPipeOffPageConnector",
    "LineSegment_115": "Plant/Piping.PipingNetworkSegment",
}
# Each segment's (SourceItem, TargetItem); equipment ends are nozzles named for the segment.
ENDS = {
    "LineSegment_110": ("#Equipment_101_Nozzle_LineSegment_110", "#Junction_106"),
    "LineSegment_111": ("#Junction_106", "#Valve_103"),
    "LineSegment_112": ("#Valve_103", "#Junction_107"),
    "LineSegment_113": ("#Junction_107", "#SheetConnector_108"),
    "LineSegment_114": ("#Junction_106", "#Valve_104"),
    "Connection_Valve_104_Junction_107": ("#Valve_104", "#Junction_107"),
    "LineSegment_115": ("#SheetConnector_109", "#Equipment_102_Nozzle_LineSegment_115"),
}


def written(revision: str) -> Path:
    folder = Path(tempfile.mkdtemp())
    gen.write(gen.generate(records(revision)), folder)
    return folder


class R0Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = gen.generate(records("R0"))
        cls.s1, cls.s2 = objects(cls.files["DEMO-PID-001.xml"]), objects(cls.files["DEMO-PID-002.xml"])

    def test_one_file_per_drawing_and_a_sidecar(self):
        self.assertEqual(set(self.files), {"DEMO-PID-001.xml", "DEMO-PID-002.xml", "sidecar.json"})

    def test_each_plant_object_has_its_class_on_its_drawing(self):
        for sheet, expected in ((self.s1, S1_CLASSES), (self.s2, S2_CLASSES)):
            for xid, cls in expected.items():
                with self.subTest(xid=xid):
                    self.assertEqual(sheet[xid].get("type"), cls)
        self.assertNotIn("Equipment_102", self.s1)
        self.assertNotIn("Valve_103", self.s2)

    def test_each_plant_object_carries_its_object_id(self):
        for sheet in (self.s1, self.s2):
            for xid, o in sheet.items():
                if xid.split("_")[0] in ("Equipment", "Valve", "Instrument", "Junction", "SheetConnector", "LineSegment") \
                        and xid.count("_") == 1:
                    pid = o.find("Components[@property='PersistentIdentifiers']/Object")
                    with self.subTest(xid=xid):
                        self.assertEqual(text(pid, "Context"), "p3d/PlantObject.ObjectId")
                        self.assertEqual(text(pid, "Value"), xid.split("_")[1])

    def test_tags_and_attributes_sit_in_their_dexpi_properties(self):
        tank = self.s1["Equipment_101"]
        self.assertEqual((text(tank, "TagName"), text(tank, "TagNamePrefix"), text(tank, "TagNameSequenceNumber")),
                         ("TK-101", "TK", "101"))
        self.assertEqual(tank.findtext(".//Data[@property='Value']/String"), "supply vessel")
        self.assertEqual(text(self.s1["Valve_104"], "PipingComponentNumber"), "XV-102")
        pi = self.s2["Instrument_105"]
        self.assertEqual([text(pi, p) for p in ("ProcessInstrumentationFunctionCategory", "ProcessInstrumentationFunctions",
                                                "ProcessInstrumentationFunctionNumber")], ["P", "I", "102"])
        segment = self.s1["LineSegment_114"]
        self.assertEqual([text(segment, p) for p in ("SegmentNumber", "NominalDiameterNumericalValueRepresentation",
                                                     "NominalDiameterRepresentation", "NominalDiameterTypeRepresentation")],
                         ["L-101-B", "50", "DN 50", "DN"])
        self.assertEqual(text(self.s1["PipingNetworkSystem_L_101"], "LineNumber"), "101")
        self.assertEqual(text(self.s1["SheetConnector_108"], "PipeConnectorNumber"), "TO-S2/A")

    def test_segments_and_their_one_connection_name_the_same_ends(self):
        for xid, (source, target) in ENDS.items():
            sheet = self.s2 if xid == "LineSegment_115" else self.s1
            segment = sheet[xid]
            (connection,) = segment.findall("Components[@property='Connections']/Object")
            with self.subTest(xid=xid):
                self.assertEqual((ref(segment, "SourceItem"), ref(segment, "TargetItem")), (source, target))
                self.assertEqual((ref(connection, "SourceItem"), ref(connection, "TargetItem")), (source, target))
                expected = "Plant/Piping.DirectPipingConnection" if xid.startswith("Connection") else "Plant/Piping.Pipe"
                self.assertEqual(connection.get("type"), expected)

    def test_the_off_page_connectors_refer_to_each_other_by_drawing_and_number(self):
        for sheet, xid, drawing, number in ((self.s1, "SheetConnector_108", "DEMO-PID-002", "FROM-S1/A"),
                                            (self.s2, "SheetConnector_109", "DEMO-PID-001", "TO-S2/A")):
            reference = sheet[f"{xid}_Reference"]
            with self.subTest(xid=xid):
                self.assertEqual(reference.get("type"), "Plant/Piping.PipeOffPageConnectorReferenceByNumber")
                self.assertEqual((text(reference, "ReferencedDrawingNumber"), text(reference, "ReferencedConnectorNumber")),
                                 (drawing, number))

    def test_the_instrument_senses_at_an_instrument_nozzle_of_its_owner(self):
        sensing = self.s2["Instrument_105_Sensing"]
        self.assertEqual(ref(sensing, "SensingLocation"), "#Equipment_102_Nozzle_Instrument_105")
        self.assertEqual(self.s2["Equipment_102_Nozzle_Instrument_105"].get("type"), "Plant/ProcessEquipment.InstrumentNozzle")

    def test_each_diagram_represents_the_objects_on_its_drawing(self):
        for name, expected in (("DEMO-PID-001.xml", ["#Equipment_101", "#Valve_103", "#Valve_104", "#Junction_106",
                                                     "#Junction_107", "#SheetConnector_108", "#LineSegment_110",
                                                     "#LineSegment_111", "#LineSegment_112", "#LineSegment_113",
                                                     "#LineSegment_114"]),
                               ("DEMO-PID-002.xml", ["#Equipment_102", "#Instrument_105", "#SheetConnector_109",
                                                     "#LineSegment_115"])):
            root = etree.fromstring(self.files[name])
            groups = root.findall(".//Object[@type='Core/Diagram.Diagram']/Components[@property='Groups']/Object")
            with self.subTest(name=name):
                self.assertEqual([ref(g, "Represents") for g in groups], expected)

    def test_the_header_carries_the_source_time_and_the_drawing(self):
        root = etree.fromstring(self.files["DEMO-PID-002.xml"])
        self.assertEqual(root.findtext("Object/Data[@property='ExportDateTime']/DateTime"), "2030-01-01T08:00:00")
        meta = objects(self.files["DEMO-PID-002.xml"])["Drawing_902"]
        self.assertEqual([text(meta, p) for p in ("DrawingNumber", "FileName", "RevisionNumber")],
                         ["DEMO-PID-002", "DEMO-PID-002", "R0"])
        self.assertEqual(root.findtext(".//Object[@type='Core/Diagram.Diagram']/Data[@property='Name']/String"), "DEMO-PID-002")

    def test_the_sidecar_holds_what_dexpi_cannot_carry(self):
        sidecar = json.loads(self.files["sidecar.json"])
        self.assertEqual(sidecar["format"], "liong-dexpi-sidecar/1")
        self.assertEqual(sidecar["assertions"]["p3d:object:105/unit"]["value_or_target"], "bar")
        self.assertEqual(sidecar["assertions"]["p3d:object:104/description"]["value_or_target"], "bypass branch")
        self.assertEqual(sidecar["assertions"]["p3d:object:110/line_prefix"]["value_or_target"], "L")
        self.assertNotIn("value_or_target", sidecar["assertions"]["p3d:object:101/tag_type"])
        self.assertEqual(sidecar["drawings"]["p3d:drawing:901"], {"status": "Approved",
                                                                  "source_locator": {"table": "Drawing", "DrawingId": 901}})
        self.assertEqual(sidecar["appearances"]["p3d:object:108"],
                         {"appearance_id": "p3d:appearance:8", "region": "30C", "coordinate_system": "p3d_drawing_handle",
                          "source_locator": {"table": "DrawingAppearance", "RowId": 8}})
        self.assertEqual(sidecar["assertions"]["ConnectorPair/1"]["source_locator"], {"table": "ConnectorPair", "RowId": 1})
        for name in ("DEMO-PID-001.xml", "DEMO-PID-002.xml"):
            self.assertEqual(sidecar["files"][name], hashlib.sha256(self.files[name]).hexdigest())

    def test_output_does_not_depend_on_record_order(self):
        shuffled = records("R0")
        for key in ("objects", "tag_assignments", "assertions", "drawings", "appearances"):
            shuffled[key].reverse()
        self.assertEqual(gen.generate(shuffled), self.files)


class RevisionTest(unittest.TestCase):
    def test_r1_changes_the_receiving_tank_tag(self):
        tank = objects(gen.generate(records("R1"))["DEMO-PID-002.xml"])["Equipment_102"]
        self.assertEqual((text(tank, "TagName"), text(tank, "TagNameSequenceNumber")), ("TK-202", "202"))

    def test_r2_drops_the_bypass(self):
        s1 = objects(gen.generate(records("R2"))["DEMO-PID-001.xml"])
        for xid in ("Valve_104", "LineSegment_114", "Connection_Valve_104_Junction_107"):
            self.assertNotIn(xid, s1)

    def test_rbad_is_refused_with_the_missing_endpoint(self):
        with self.assertRaises(gen.Rejection) as caught:
            gen.generate(records("Rbad"))
        self.assertEqual(caught.exception, gen.Rejection(edge_kind="FLOW", source="p3d:object:114",
                                                         target="p3d:object:104", missing="p3d:object:104"))
        self.assertEqual(str(caught.exception), "FLOW p3d:object:114->p3d:object:104 has missing endpoint p3d:object:104")


class UnsupportedTest(unittest.TestCase):
    def test_an_equipment_tag_type_outside_the_tables_is_refused(self):
        changed = records("R0")
        next(a for a in changed["assertions"] if a["assertion_id"] == "p3d:object:101/tag_type")["value_or_target"] = "PU"
        with self.assertRaisesRegex(gen.Unsupported, "^p3d:object:101 is equipment of tag type 'PU'"):
            gen.generate(changed)

    def test_a_segment_on_another_drawing_than_its_start_is_refused(self):
        changed = records("R0")
        next(a for a in changed["appearances"] if a["object_id"] == "p3d:object:115")["artifact_id"] = "p3d:drawing:901"
        with self.assertRaisesRegex(gen.Unsupported, "^p3d:object:115 starts_at p3d:object:109 crosses drawings without an off-page connector$"):
            gen.generate(changed)

    def test_an_instrument_owned_across_drawings_is_refused(self):
        changed = records("R0")
        next(a for a in changed["appearances"] if a["object_id"] == "p3d:object:105")["artifact_id"] = "p3d:drawing:901"
        with self.assertRaisesRegex(gen.Unsupported, "^p3d:object:105 owned_by p3d:object:102 crosses drawings$"):
            gen.generate(changed)



class DuplicateRecordsTest(unittest.TestCase):
    """Records that would collapse onto each other are refused, not merged."""

    def test_each_kind_of_duplicate_is_refused(self):
        def doubled(group, index=0, **change):
            src = records("R0")
            src[group].append(dict(src[group][index], **change))
            return src

        cases = {
            "objects holds p3d:object:101 more than once": doubled("objects"),
            "drawings holds p3d:drawing:901 more than once": doubled("drawings"),
            "drawings holds DEMO-PID-001 more than once": doubled("drawings", artifact_id="p3d:drawing:999"),
            "tag_assignments holds p3d:object:101 more than once": doubled("tag_assignments"),
        }
        attribute = next(a for a in records("R0")["assertions"] if a["assertion_id"] == "p3d:object:101/tag_type")
        cases["assertions holds ('p3d:object:101', 'tag_type') more than once"] = doubled(
            "assertions", records("R0")["assertions"].index(attribute), assertion_id="p3d:object:101/tag_type#2",
            value_or_target="PU")
        by_id = {a["assertion_id"]: i for i, a in enumerate(records("R0")["assertions"])}
        cases["assertions holds SegmentStart/1 more than once"] = doubled("assertions", by_id["SegmentStart/1"])
        cases["assertions holds ('p3d:object:110', 'starts_at') more than once"] = doubled(
            "assertions", by_id["SegmentStart/1"], assertion_id="SegmentStart/7", value_or_target="p3d:object:103")
        cases["assertions holds ('p3d:object:110', 'ends_at') more than once"] = doubled(
            "assertions", by_id["SegmentEnd/1"], assertion_id="SegmentEnd/7", value_or_target="p3d:object:103")
        cases["assertions holds ('p3d:object:105', 'owned_by') more than once"] = doubled(
            "assertions", by_id["Ownership/1"], assertion_id="Ownership/2", value_or_target="p3d:object:101")
        cases["assertions holds ('p3d:object:108', 'continues_to') more than once"] = doubled(
            "assertions", by_id["SheetConnectorLink/1"], assertion_id="SheetConnectorLink/2")
        cases["assertions holds ('p3d:object:109', 'continued_from') more than once"] = doubled(
            "assertions", by_id["SheetConnectorLink/1"], assertion_id="SheetConnectorLink/2",
            subject_id="p3d:object:113")
        cases["assertions holds ('p3d:object:104', 'connects_to', 'p3d:object:107') more than once"] = doubled(
            "assertions", by_id["ConnectorPair/1"], assertion_id="ConnectorPair/2")
        for message, src in cases.items():
            with self.subTest(message=message), self.assertRaises(gen.Unsupported) as caught:
                gen.generate(src)
            self.assertEqual(str(caught.exception), message)


if __name__ == "__main__":
    unittest.main()
