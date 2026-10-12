"""Regression tests for documentation utilities; no engineering tests run here."""

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

import bundle_docs
import check_docs


class DocumentationToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in check_docs.BASELINE:
            shutil.copyfile(check_docs.ROOT / name, self.root / name)
        shutil.copytree(check_docs.ROOT / "docs", self.root / "docs")
        shutil.copytree(check_docs.ROOT / "scripts", self.root / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__"))

    def test_current_package_passes(self):
        self.assertEqual(check_docs.check(self.root), [])

    def test_missing_document_is_reported(self):
        (self.root / "docs/LIONG-001-charter.md").unlink()
        self.assertTrue(any("LIONG-001" in error for error in check_docs.check(self.root)))

    def test_unknown_requirement_is_reported(self):
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\nREQ-999\n", encoding="utf-8")
        self.assertTrue(any("REQ-999" in error for error in check_docs.check(self.root)))

    def test_unregistered_source_is_reported(self):
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\nREF-STD-999\n", encoding="utf-8")
        self.assertTrue(any("REF-STD-999" in error for error in check_docs.check(self.root)))

    def test_missing_scenario_definition_is_reported_despite_mentions(self):
        path = self.root / "docs/LIONG-006-synthetic-data.md"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(line for line in lines if not line.startswith("| SCN-014 |")),
                        encoding="utf-8")
        self.assertTrue(any("LIONG-006 must define" in error for error in check_docs.check(self.root)))

    def test_missing_acceptance_row_is_reported(self):
        path = self.root / "docs/LIONG-010-evaluation.md"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(line for line in lines if not line.startswith("| REQ-017 ")),
                        encoding="utf-8")
        self.assertTrue(any("acceptance matrix" in error for error in check_docs.check(self.root)))

    def test_missing_heading_is_reported(self):
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n[Bad](GLOSSARY.md#absent-heading)\n",
                        encoding="utf-8")
        self.assertTrue(any("missing heading" in error for error in check_docs.check(self.root)))

    def test_merge_marker_is_reported(self):
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n<<<<<<< conflict\n", encoding="utf-8")
        self.assertTrue(any("merge-conflict" in error for error in check_docs.check(self.root)))

    def test_archive_is_reproducible_and_manifest_verifies(self):
        contents = bundle_docs.payload(self.root)
        first = bundle_docs.archive_bytes(contents)
        self.assertEqual(first, bundle_docs.archive_bytes(contents))
        output = self.root / "test.zip"
        output.write_bytes(first)
        self.assertTrue(bundle_docs.matches(output, contents))
        with zipfile.ZipFile(output) as archive:
            manifest = json.loads(archive.read("MANIFEST.json"))
            for name, digest in manifest["sha256"].items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), digest)
            self.assertNotIn(bundle_docs.OUTPUT.as_posix(), archive.namelist())

    def test_archive_links_resolve_inside_the_archive(self):
        self.assertEqual(bundle_docs.broken_links(bundle_docs.payload(self.root)), [])

    def test_link_to_a_file_outside_the_archive_is_reported(self):
        path = self.root / "docs/LIONG-REG-001-decisions.md"
        path.write_text(path.read_text() + "\n[World](../scripts/world.py)\n", encoding="utf-8")
        self.assertEqual(bundle_docs.broken_links(bundle_docs.payload(self.root)),
                         ["docs/LIONG-REG-001-decisions.md: links to ../scripts/world.py, which is not in the archive"])

    def test_register_links_need_the_decision_records_in_the_archive(self):
        contents = bundle_docs.payload(self.root)
        without = {name: data for name, data in contents.items() if not name.startswith("docs/decisions/")}
        self.assertTrue(any("decisions/DEC-014-" in e for e in bundle_docs.broken_links(without)))

    def test_stale_and_corrupt_archive_rejected(self):
        contents = bundle_docs.payload(self.root)
        output = self.root / "test.zip"
        output.write_bytes(bundle_docs.archive_bytes(contents))
        contents["README.md"] += b"\nChanged\n"
        self.assertFalse(bundle_docs.matches(output, contents))
        output.write_bytes(b"not a zip")
        self.assertFalse(bundle_docs.matches(output, contents))


if __name__ == "__main__":
    unittest.main()
