#!/usr/bin/env python3
"""Tests for scripts/dexpi_pins.py and the pinned files in standards/dexpi/2.0.1."""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dexpi_pins  # noqa: E402

# Hashes written by hand from the files retrieved on 2026-10-14, not read from the manifest.
EXPECTED_SHA256 = {
    "DEXPI_XML_Schema.xsd": "0bd6568b7c52fd59ac4ef6d8547ab2b2aa890c009a3a1bfbc5d7cc18c53b36e6",
    "Core.xml": "7136f8440c08c8bf7759c4e9eb614b046cc3196f2f45695122629a2020e61e4a",
    "Plant.xml": "0a5175535c1263464fee653c7b99f38eb810c15824f84155748eac165f50edbf",
    "reference_pid.xml": "acd39c74292aef3f6f00581fc78b05814acf2318815abd28c14ebefba12fdd94",
}
CORE = "https://data.dexpi.org/models/2.0.1/Core.xml"
PLANT = "https://data.dexpi.org/models/2.0.1/Plant.xml"
METADATA = "https://data.dexpi.org/models/2.0.1/MetaData.xml"
IMPORT = re.compile(r'<Import prefix="[^"]+" source="([^"]+)"/>')


class PinnedFilesTest(unittest.TestCase):
    def test_pins_match_their_manifest(self):
        self.assertEqual(dexpi_pins.errors(), [])

    def test_manifest_holds_the_reviewed_hashes(self):
        files = dexpi_pins.manifest()["files"]
        self.assertEqual({name: entry["sha256"] for name, entry in files.items()}, EXPECTED_SHA256)

    def test_manifest_names_the_release_and_license(self):
        pins = dexpi_pins.manifest()
        self.assertEqual((pins["release"], pins["tag"], pins["license"]), ("2.0.1", "V2.0.1", "CC BY 4.0"))

    def test_import_table_maps_core_and_plant_only(self):
        table = dexpi_pins.import_table()
        self.assertEqual(table, {CORE: dexpi_pins.PIN_DIR / "Core.xml", PLANT: dexpi_pins.PIN_DIR / "Plant.xml"})

    def test_every_import_in_the_pinned_files_is_pinned_or_recorded_as_unpublished(self):
        unpublished = set(dexpi_pins.manifest()["not_published"])
        for name in EXPECTED_SHA256:
            text = (dexpi_pins.PIN_DIR / name).read_text(encoding="utf-8")
            for uri in IMPORT.findall(text):
                with self.subTest(file=name, uri=uri):
                    self.assertTrue(uri in dexpi_pins.import_table() or uri in unpublished)

    def test_reference_pid_imports_only_pinned_models(self):
        text = (dexpi_pins.PIN_DIR / "reference_pid.xml").read_text(encoding="utf-8")
        self.assertEqual(IMPORT.findall(text), [CORE, PLANT])

    def test_unpinned_uris_raise(self):
        with self.assertRaisesRegex(dexpi_pins.UnpinnedImport, "DEXPI publishes no such file"):
            dexpi_pins.local_path(METADATA)
        with self.assertRaisesRegex(dexpi_pins.UnpinnedImport, "not in MANIFEST.json"):
            dexpi_pins.local_path("https://data.dexpi.org/models/2.0.0/Core.xml")


class CheckFailsTest(unittest.TestCase):
    """Each way a pinned folder can drift from its manifest makes `errors` report it."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()) / "2.0.1"
        shutil.copytree(dexpi_pins.PIN_DIR, self.dir)
        self.addCleanup(shutil.rmtree, self.dir.parent)

    def test_a_changed_byte_fails(self):
        path = self.dir / "Plant.xml"
        data = bytearray(path.read_bytes())
        data[-2] ^= 1
        path.write_bytes(bytes(data))
        self.assertEqual(len(dexpi_pins.errors(self.dir)), 1)
        self.assertIn("Plant.xml: SHA-256", dexpi_pins.errors(self.dir)[0])

    def test_a_missing_file_fails(self):
        (self.dir / "Core.xml").unlink()
        self.assertEqual(dexpi_pins.errors(self.dir), ["Core.xml: listed in MANIFEST.json but missing"])

    def test_an_extra_file_fails(self):
        (self.dir / "Process.xml").write_text("<Model/>")
        self.assertEqual(dexpi_pins.errors(self.dir), ["Process.xml: not listed in MANIFEST.json"])


if __name__ == "__main__":
    unittest.main()
