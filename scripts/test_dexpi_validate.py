#!/usr/bin/env python3
"""Tests for scripts/dexpi_validate.py.

fixtures/dexpi-negative/cases.json holds DEC-064's SCN-005 negatives. Each case plants
one fault, by hand, in R0's generated DEMO-PID-002.xml or sidecar, and is named for the
stage it must fail in. `negative` builds a case's folder; each edit must match exactly
once. NEGATIVES below gives each one's stage and first problem, typed by hand.
"""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dexpi_validate as validate  # noqa: E402
from test_dexpi_generate import records, written  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = {case["name"]: case for case in
         json.loads((ROOT / "fixtures" / "dexpi-negative" / "cases.json").read_text(encoding="utf-8"))["cases"]}
ALL_PASS = ("Valid against the DEXPI 2.0.1 XSD, its reference checks and the 2.0.1 Core and Plant models "
            "for the classes LIONG uses, and passes LIONG's rules. Generating it again gives identical bytes.")
NEGATIVES = {
    "schema-unknown-element": ("schema", "schema: DEMO-PID-002.xml line 136: Element 'Colour': This element is not expected."),
    "schema-document-type": ("schema", "schema: DEMO-PID-002.xml: has a document type declaration, which DEXPI files do not use"),
    "references-dangling-id": ("references", "references: DEMO-PID-002.xml line 129: #Equipment_102_Nozzle_Instrument_999 does not resolve"),
    "references-unpinned-import": ("references", "references: DEMO-PID-002.xml: import Plant: https://data.dexpi.org/models/2.0.1/MetaData.xml has no pinned copy"),
    "references-unknown-class": ("references", "references: DEMO-PID-002.xml line 135: type Plant/ProcessEquipment.Tankk is not in the pinned models"),
    "model-abstract-class": ("model", "model: DEMO-PID-002.xml line 135: Plant/ProcessEquipment.ProcessEquipment is not a concrete class"),
    "model-missing-required-property": ("model", "model: DEMO-PID-002.xml line 182: Core/Diagram.Diagram.Name has 0 values, allowed 1..1"),
    "model-undeclared-property": ("model", "model: DEMO-PID-002.xml line 135: Plant/ProcessEquipment.Tank declares no property TagPrefix"),
    "liong_rules-unsupported-class": ("liong_rules", "liong_rules: Plant/ProcessEquipment.Vessel: 1 objects outside the supported subset"),
    "liong_rules-duplicate-tag": ("liong_rules", "liong_rules: tag L-101-5 is on 2 nodes"),
    "liong_rules-missing-sidecar-entry": ("liong_rules", "liong_rules: p3d:object:105 has no sidecar entry"),
}


def negative(test: unittest.TestCase, name: str) -> Path:
    """A folder holding R0's DEMO-PID-002.xml and sidecar with the named case's one fault."""
    case = CASES[name]
    folder = written("R0")
    test.addCleanup(shutil.rmtree, folder)
    (folder / "DEMO-PID-001.xml").unlink()
    path = folder / case["file"]
    if "remove_key" in case:
        data = json.loads(path.read_text(encoding="utf-8"))
        section, key = case["remove_key"]
        del data[section][key]
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
        test.assertEqual(text.count(case["find"]), 1, f"{name}: the edit must match exactly once")
        path.write_text(text.replace(case["find"], case["replace"]), encoding="utf-8")
    return folder


class AcceptedTest(unittest.TestCase):
    def test_accepted_revisions_pass_every_stage_and_round_trip(self):
        for revision in ("R0", "R1", "R2"):
            folder = written(revision)
            self.addCleanup(shutil.rmtree, folder)
            result = validate.validate(folder)
            with self.subTest(revision=revision):
                self.assertEqual(result, {"passed": ["schema", "references", "model", "liong_rules"],
                                          "failed": None, "problems": [], "round_trip": []})
                self.assertEqual(validate.claim(result), ALL_PASS)

    def test_one_drawing_alone_passes_every_stage(self):
        # The negatives start from this folder, so each fails only through its planted fault.
        folder = written("R0")
        self.addCleanup(shutil.rmtree, folder)
        (folder / "DEMO-PID-001.xml").unlink()
        self.assertEqual(validate.validate(folder)["passed"], ["schema", "references", "model", "liong_rules"])

    def test_a_changed_byte_fails_the_round_trip(self):
        folder = written("R0")
        self.addCleanup(shutil.rmtree, folder)
        path = folder / "DEMO-PID-002.xml"
        path.write_bytes(path.read_bytes().replace(b"<String>en</String>", b"<String>fr</String>"))
        result = validate.validate(folder)
        self.assertIsNone(result["failed"])
        self.assertEqual(result["round_trip"], ["DEMO-PID-002.xml differs when generated again"])


class NegativeTest(unittest.TestCase):
    def test_every_negative_fixture_is_listed(self):
        self.assertEqual(sorted(CASES), sorted(NEGATIVES))
        self.assertEqual({name: case["stage"] for name, case in CASES.items()},
                         {name: stage for name, (stage, _) in NEGATIVES.items()})

    def test_each_negative_fails_in_the_stage_it_is_named_for(self):
        for name, (stage, first) in NEGATIVES.items():
            result = validate.validate(negative(self, name))
            with self.subTest(name=name):
                self.assertTrue(name.startswith(stage + "-"))
                self.assertEqual(result["failed"], stage)
                self.assertEqual(result["passed"], list(validate.STAGES[:validate.STAGES.index(stage)]))
                self.assertTrue(result["problems"][0].startswith(first), result["problems"][0])
                self.assertIsNone(result["round_trip"])


class ClaimTest(unittest.TestCase):
    def test_a_claim_names_only_the_stages_that_passed(self):
        self.assertEqual(validate.claim(validate.validate(negative(self, "schema-unknown-element"))),
                         "Fails the schema stage; no stage passed.")
        self.assertEqual(validate.claim(validate.validate(negative(self, "model-abstract-class"))),
                         "Valid against the DEXPI 2.0.1 XSD and its reference checks; fails the model stage.")
        self.assertEqual(validate.claim(validate.validate(negative(self, "liong_rules-duplicate-tag"))),
                         "Valid against the DEXPI 2.0.1 XSD, its reference checks and the 2.0.1 Core and Plant models "
                         "for the classes LIONG uses; fails the liong_rules stage.")

    def test_no_claim_says_conformant_or_certified(self):
        for name in NEGATIVES:
            claim = validate.claim(validate.validate(negative(self, name))).lower()
            with self.subTest(name=name):
                self.assertNotIn("conform", claim)
                self.assertNotIn("certif", claim)


class ReferencePidTest(unittest.TestCase):
    def test_the_reference_pid_passes_the_dexpi_stages_and_fails_liong_rules(self):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        shutil.copy(ROOT / "standards" / "dexpi" / "2.0.1" / "reference_pid.xml", folder)
        result = validate.validate(folder)
        self.assertEqual((result["passed"], result["failed"]), (["schema", "references", "model"], "liong_rules"))
        self.assertIn("liong_rules: Plant/Piping.BallValve: 5 objects outside the supported subset", result["problems"])


if __name__ == "__main__":
    unittest.main()
