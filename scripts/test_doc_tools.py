"""Regression tests for documentation utilities; no engineering tests run here."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
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

    def test_reference_and_multiline_links_are_checked(self):
        path = self.root / "docs/LIONG-REG-001-decisions.md"
        for link in ("[missing][ref]\n\n[ref]: ../absent-1.md\n", "[bad](\n../absent-2.md\n)\n",
                     "[angle](<../absent-3.md>)\n", "[q][r4]\n\n> [r4]: ../absent-4.md\n",
                     "[l][r5]\n\n- [r5]: ../absent-5.md\n", "[e][r6\\]]\n\n[r6\\]]: ../absent-6.md\n",
                     "[n][r7]\n\n> [r7]:\n> ../absent-7.md\n", "> [m](\n> ../absent-8.md)\n"):
            path.write_text(path.read_text() + "\n" + link, encoding="utf-8")
        errors = bundle_docs.broken_links(bundle_docs.payload(self.root))
        for name in [f"absent-{n}.md" for n in range(1, 9)]:
            self.assertTrue(any(f"../{name}, which is not in the archive" in e for e in errors), name)

    def test_destination_is_read_as_written(self):
        # "README.md>" and "README.md<no-break space>x.md" name files that are not README.md
        path = self.root / "docs/LIONG-REG-001-decisions.md"
        path.write_bytes(path.read_bytes() + "\n[a](../README.md>)\n\n[b](../README.md\u00a0x.md)\n".encode()
                         + b"\r\n[c](\r\n../scripts/world.py)\r\n\n[d](../README.md\x00y.md)\n")
        errors = bundle_docs.broken_links(bundle_docs.payload(self.root))
        for target in ("../README.md>", "../README.md\u00a0x.md", "../scripts/world.py", "../README.md\ufffdy.md"):
            self.assertTrue(any(f"{target}, which is not in the archive" in e for e in errors), target)

    def test_fence_outside_the_first_column_is_refused(self):
        path = self.root / "docs/LIONG-000-index.md"
        path.write_text(path.read_text() + "\n  ```text\n> code\n  ```\n", encoding="utf-8")
        self.assertTrue(any("a code fence must start in the first column" in e
                            for e in bundle_docs.broken_links(bundle_docs.payload(self.root))))

    def test_link_naming_a_directory_is_refused(self):
        path = self.root / "docs/LIONG-REG-001-decisions.md"
        path.write_text(path.read_text() + "\n[a](../README.md/)\n\n[b](../README.md/.)\n", encoding="utf-8")
        errors = bundle_docs.broken_links(bundle_docs.payload(self.root))
        for target in ("../README.md/", "../README.md/."):
            self.assertTrue(any(f"links to {target}, which" in e for e in errors), target)

    def test_line_break_other_than_lf_or_cr_is_refused(self):
        path = self.root / "docs/LIONG-000-index.md"
        path.write_text(path.read_text() + "\ntext\u2028more\n", encoding="utf-8")
        self.assertTrue(any("only LF and CR may end a line" in e
                            for e in bundle_docs.broken_links(bundle_docs.payload(self.root))))

    def test_link_target_with_a_space_or_control_character_is_refused(self):
        # URL parsing drops the leading space and the tab, so "./README.md" would pass
        path = self.root / "README.md"
        path.write_text(path.read_text() + "\n[a](< ./README.md>)\n\n[b](<./READ\tME.md>)\n", encoding="utf-8")
        errors = bundle_docs.broken_links(bundle_docs.payload(self.root))
        for target in (" ./README.md", "./READ\tME.md"):
            self.assertTrue(any(f"space or control character: {target!r}" in e for e in errors), target)

    def test_raw_html_in_archived_markdown_is_refused(self):
        path = self.root / "docs/LIONG-000-index.md"
        html = ('<a href="\n../scripts/world.py">world</a>', '<img srcset="../scripts/world.py 1x">',
                '<video poster="../scripts/world.py"></video>', '<object data="../scripts/world.py"></object>',
                '<form action="../scripts/world.py"></form>', '<!-- hidden -->')
        path.write_text(path.read_text() + "\n" + "\n\n".join(html) + "\n", encoding="utf-8")
        errors = bundle_docs.broken_links(bundle_docs.payload(self.root))
        for tag in html:
            first_line = tag.splitlines()[0]
            self.assertTrue(any(e.startswith("docs/LIONG-000-index.md: raw HTML") and first_line[:20] in e
                                for e in errors), tag)

    def test_html_in_code_and_around_false_code_is_refused(self):
        for html in ('Use `<a href="x">` here.', '```\n<img src="y">\n```', '\\`<a href="../scripts/world.py">W</a>\\`',
                     '```<a href="../scripts/world.py">W</a>``'):
            with self.subTest(html=html):
                self.setUp()
                path = self.root / "docs/LIONG-000-index.md"
                path.write_text(path.read_text() + "\n" + html + "\n", encoding="utf-8")
                self.assertTrue(any("raw HTML is not allowed, even in code" in e
                                    for e in bundle_docs.broken_links(bundle_docs.payload(self.root))))

    def test_bundler_refuses_a_broken_link_and_writes_nothing(self):
        archive = self.root / bundle_docs.OUTPUT
        before = archive.read_bytes()
        path = self.root / "docs/LIONG-REG-001-decisions.md"
        path.write_text(path.read_text() + "\n[World](../scripts/world.py)\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.root / "scripts/bundle_docs.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("../scripts/world.py, which is not in the archive", result.stdout)
        self.assertEqual(archive.read_bytes(), before)

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
