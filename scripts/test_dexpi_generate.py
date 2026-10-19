#!/usr/bin/env python3
"""Tests for scripts/dexpi_generate.py.

The records come from the R0 snapshot through extract_p3d.py. The expected classes, IDs,
ends and values are typed by hand from LIONG-006's R0 and DEC-077's mapping: TK-101 feeds
L-101-1 to the first junction, the bypass valve XV-102 bolts straight onto the second
junction, and L-101-4 leaves sheet 1 through the off-page connector TO-S2/A.

The W-SP records come from its W0 snapshot through extract_sps.py. Their expected values
are typed by hand from worlds/W-SP.yaml, the GUIDs in fixtures/sps-wsp/W0 and DEC-086:
TK-301 feeds run A through HV-301 and HV-302 to TO-S2/B on DEMO-PID-101, and run B
carries FROM-S1/B through HV-303 to TK-302, whose level LT-302 measures.
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
import extract_sps  # noqa: E402

SNAPSHOTS = Path(__file__).resolve().parent.parent / "fixtures" / "p3d-r0"
WSP = Path(__file__).resolve().parent.parent / "fixtures" / "sps-wsp" / "W0"
AT = "2026-10-14T00:00:00+00:00"


def records(revision: str) -> dict:
    """The records of an R0 revision, or of W-SP's W0."""
    if revision == "W0":
        stated, rows = extract_sps.rows_from_snapshot(WSP)
        return extract_sps.extract(stated, rows, "snapshot:fixtures/sps-wsp/W0", AT)
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



# W-SP's GUIDs, from fixtures/sps-wsp/W0, by tag.
GUID = {
    "TK-301": "4E781C49-8383-541C-A3BB-A881AA4E3A40", "TK-302": "3BDC3007-A1CA-5FD4-9A4B-C12B14E4605A",
    "HV-301": "E5531D47-5180-598A-B6F8-63EF2DC29531", "HV-302": "AA396C4B-92E2-57AC-9B8F-AF12BD9C4EBD",
    "HV-303": "C41295BE-6C23-50BE-925A-3506CFBE5051", "LT-302": "89DF1AA8-BF4A-5B88-A93E-87705C43B9C4",
    "TO-S2/B": "18B2755C-0314-5534-B40B-B27928211F1E", "FROM-S1/B": "967CF11A-9D5D-5468-A3B2-14A3FB0EC305",
    "L-301-1": "A80BEDD0-89BE-54F9-831D-DA6574D126FC", "L-301-2": "D410EBE1-247A-5511-A67B-CB063802D015",
    "L-301-3": "87F2AF9E-A408-5639-99A4-1D34ED0936B3", "L-301-4": "E29B63F7-B8D4-5B2A-9AFB-624797FDFA54",
    "L-301-5": "4F28FEA3-45E7-574F-B0BE-294867898C20",
    "DEMO-PID-101": "440AD0B4-53C2-5AE6-BBDC-A935FBB33D38", "DEMO-PID-102": "DBA9DC82-994D-55A7-8A9C-777B288D8A1A",
}
TABLE_OF = {"TK": "Vessel", "HV": "PipingFitting", "LT": "Instrument", "TO": "SheetLink", "FR": "SheetLink",
            "L-": "LineDepiction"}


def xml_id(tag: str) -> str:
    """The file-local id DEC-086 gives a W-SP object: its sps table and GUID, hyphens made underscores."""
    return f"{TABLE_OF[tag[:2]]}_{GUID[tag].replace('-', '_')}"


class WspTest(unittest.TestCase):
    """W-SP's W0 through the SmartPlant-style extraction, with the classes R0 lacks (DEC-086)."""

    @classmethod
    def setUpClass(cls):
        cls.files = gen.generate(records("W0"))
        cls.s1, cls.s2 = objects(cls.files["DEMO-PID-101.xml"]), objects(cls.files["DEMO-PID-102.xml"])

    def sheet(self, tag: str) -> dict:
        return self.s1 if tag in ("TK-301", "HV-301", "HV-302", "TO-S2/B", "L-301-1", "L-301-2", "L-301-3") else self.s2

    def test_one_file_per_drawing_and_a_sidecar(self):
        self.assertEqual(set(self.files), {"DEMO-PID-101.xml", "DEMO-PID-102.xml", "sidecar.json"})

    def test_each_object_has_its_class_and_its_sps_identifier(self):
        classes = {"TK": "Plant/ProcessEquipment.Tank", "HV": "Plant/Piping.OperatedValve",
                   "LT": "Plant/Instrumentation.ProcessInstrumentationFunction",
                   "TO": "Plant/Piping.FlowOutPipeOffPageConnector", "FR": "Plant/Piping.FlowInPipeOffPageConnector",
                   "L-": "Plant/Piping.PipingNetworkSegment"}
        for tag in GUID:
            if tag.startswith("DEMO"):
                continue
            o = self.sheet(tag)[xml_id(tag)]
            pid = o.find("Components[@property='PersistentIdentifiers']/Object")
            context = "sps/LineDepiction.DepictionGuid" if tag.startswith("L-") else "sps/DesignItem.ItemGuid"
            with self.subTest(tag=tag):
                self.assertEqual(o.get("type"), classes[tag[:2]])
                self.assertEqual((text(pid, "Context"), text(pid, "Value")), (context, GUID[tag]))

    def test_hand_valves_carry_their_tags(self):
        for tag in ("HV-301", "HV-302", "HV-303"):
            valve = self.sheet(tag)[xml_id(tag)]
            with self.subTest(tag=tag):
                self.assertEqual(text(valve, "PipingComponentNumber"), tag)
                self.assertIsNone(valve.find("Components[@property='ActuatingSystem']"))

    def test_the_level_transmitter_is_category_l_function_t(self):
        lt = self.s2[xml_id("LT-302")]
        self.assertEqual([text(lt, p) for p in ("ProcessInstrumentationFunctionCategory", "ProcessInstrumentationFunctions",
                                                "ProcessInstrumentationFunctionNumber")], ["L", "T", "302"])
        sensing = self.s2[f"{xml_id('LT-302')}_Sensing"]
        self.assertEqual(ref(sensing, "SensingLocation"), f"#{xml_id('TK-302')}_Nozzle_{xml_id('LT-302')}")

    def test_both_runs_of_line_301_sit_in_its_system_on_each_drawing(self):
        for sheet, tags in ((self.s1, ["L-301-1", "L-301-2", "L-301-3"]), (self.s2, ["L-301-4", "L-301-5"])):
            system = sheet["PipingNetworkSystem_L_301"]
            members = [o.get("id") for o in system.findall("Components[@property='Segments']/Object")]
            with self.subTest(tags=tags):
                self.assertEqual(text(system, "LineNumber"), "301")
                self.assertEqual(sorted(members), sorted(xml_id(t) for t in tags))
            systems = [x for x in sheet if x.startswith("PipingNetworkSystem")]
            self.assertEqual(systems, ["PipingNetworkSystem_L_301"])

    def test_segments_run_with_the_flow(self):
        ends = {"L-301-1": ("TK-301", "HV-301"), "L-301-2": ("HV-301", "HV-302"), "L-301-3": ("HV-302", "TO-S2/B"),
                "L-301-4": ("FROM-S1/B", "HV-303"), "L-301-5": ("HV-303", "TK-302")}
        for segment, (source, target) in ends.items():
            o = self.sheet(segment)[xml_id(segment)]
            expected = [f"#{xml_id(source)}" + (f"_Nozzle_{xml_id(segment)}" if source.startswith("TK") else ""),
                        f"#{xml_id(target)}" + (f"_Nozzle_{xml_id(segment)}" if target.startswith("TK") else "")]
            with self.subTest(segment=segment):
                self.assertEqual([ref(o, "SourceItem"), ref(o, "TargetItem")], expected)
                self.assertEqual(text(o, "SegmentNumber"), segment)
                self.assertEqual(text(o, "NominalDiameterRepresentation"), "DN 80")

    def test_the_sheet_links_refer_to_each_other_by_drawing_and_number(self):
        for sheet, tag, drawing, number in ((self.s1, "TO-S2/B", "DEMO-PID-102", "FROM-S1/B"),
                                            (self.s2, "FROM-S1/B", "DEMO-PID-101", "TO-S2/B")):
            reference = sheet[f"{xml_id(tag)}_Reference"]
            with self.subTest(tag=tag):
                self.assertEqual(text(sheet[xml_id(tag)], "PipeConnectorNumber"), tag)
                self.assertEqual((text(reference, "ReferencedDrawingNumber"), text(reference, "ReferencedConnectorNumber")),
                                 (drawing, number))

    def test_each_drawing_carries_its_sheet_guid(self):
        for name, sheet in (("DEMO-PID-101", self.s1), ("DEMO-PID-102", self.s2)):
            meta = sheet[f"Sheet_{GUID[name].replace('-', '_')}"]
            pid = meta.find("Components[@property='PersistentIdentifiers']/Object")
            with self.subTest(name=name):
                self.assertEqual((text(pid, "Context"), text(pid, "Value")), ("sps/Sheet.SheetGuid", GUID[name]))
                self.assertEqual([text(meta, p) for p in ("DrawingNumber", "RevisionNumber")], [name, "W0.0"])
        root = etree.fromstring(self.files["DEMO-PID-101.xml"])
        self.assertEqual(root.findtext("Object/Data[@property='ExportDateTime']/DateTime"), "2030-02-01T08:00:00")
        self.assertEqual(root.findtext("Object/Data[@property='OriginatingSystemName']/String"), "LIONG sps-to-DEXPI mapper")

    def test_the_sidecar_keeps_runs_pipeline_and_derived_status(self):
        sidecar = json.loads(self.files["sidecar.json"])
        segment = f"sps:line:{GUID['L-301-4']}"
        self.assertEqual(sidecar["assertions"][f"{segment}/pipeline"]["value_or_target"], "L-301")
        self.assertEqual(sidecar["assertions"][f"{segment}/pipeline"]["evidence_status"], "derived")
        self.assertTrue(sidecar["assertions"][f"{segment}/run"]["value_or_target"].startswith("sps:item:"))
        self.assertNotIn("value_or_target", sidecar["assertions"][f"sps:item:{GUID['LT-302']}/tag_lead"])
        self.assertEqual(sidecar["assertions"][f"sps:item:{GUID['LT-302']}/unit"]["value_or_target"], "%")
        self.assertEqual(sidecar["drawings"][f"sps:sheet:{GUID['DEMO-PID-102']}"]["status"], "Approved")

    def test_output_does_not_depend_on_record_order(self):
        shuffled = records("W0")
        for key in ("objects", "tag_assignments", "assertions", "drawings", "appearances"):
            shuffled[key].reverse()
        self.assertEqual(gen.generate(shuffled), self.files)


class WspUnsupportedTest(unittest.TestCase):
    """What W-SP's new mapping refuses rather than writes wrongly."""

    def test_a_valve_whose_tag_letters_are_outside_the_table_is_refused(self):
        changed = records("W0")
        next(t for t in changed["tag_assignments"] if t["tag_value"] == "HV-303")["tag_value"] = "QV-303"
        with self.assertRaisesRegex(gen.Unsupported, f"^sps:item:{GUID['HV-303']} is a valve of tag type 'QV'"):
            gen.generate(changed)

    def test_an_instrument_whose_letters_are_outside_the_table_is_refused(self):
        changed = records("W0")
        next(a for a in changed["assertions"] if a["predicate"] == "tag_lead"
             and a["subject_id"] == f"sps:item:{GUID['LT-302']}")["value_or_target"] = "LX"
        with self.assertRaisesRegex(gen.Unsupported, f"^sps:item:{GUID['LT-302']} is an instrument of tag type 'LX'"):
            gen.generate(changed)

    def test_a_sheet_link_of_unknown_sense_is_refused(self):
        changed = records("W0")
        next(a for a in changed["assertions"] if a["predicate"] == "link_sense"
             and a["value_or_target"] == "From")["value_or_target"] = "Both"
        with self.assertRaisesRegex(gen.Unsupported, "does not pair an Out with an In connector$"):
            gen.generate(changed)

    def test_a_source_without_a_mapping_is_refused(self):
        changed = records("W0")
        changed["source_revision"]["source_id"] = "xyz"
        with self.assertRaisesRegex(gen.Unsupported, "^source 'xyz' has no DEXPI mapping$"):
            gen.generate(changed)

    def test_an_object_whose_key_is_not_its_id_is_refused(self):
        changed = records("W0")
        changed["objects"][0]["source_object_key"] = "0"
        with self.assertRaisesRegex(gen.Unsupported, "is not an object ID of source sps with its own key$"):
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
