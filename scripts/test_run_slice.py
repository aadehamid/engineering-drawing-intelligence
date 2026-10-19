#!/usr/bin/env python3
"""Tests for scripts/run_slice.py: MILESTONE-001's slice end to end.

Expected counts are LIONG-006's (R0 17 nodes and 31 edges, R2 15 and 26), typed by hand.
W-SP's W0 is typed by hand from worlds/W-SP.yaml: 13 objects and 2 drawings, and 11 FLOW,
1 INSTRUMENT_PARENT, 1 CROSS_SHEET_REFERENCE and 13 ON_SHEET edges, so 15 nodes and 26
edges. The Neo4j and database tests need servers: LIONG_NEO4J and LIONG_SQLSERVER; CI
sets both.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import answer_key_guard  # noqa: E402
import compare_answer_key  # noqa: E402
import run_slice  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KEY = json.loads((ROOT / "fixtures" / "answer-keys" / "p3d-r0.json").read_text(encoding="utf-8"))
WSP_KEY = json.loads((ROOT / "fixtures" / "answer-keys" / "sps-wsp.json").read_text(encoding="utf-8"))
WSP_COUNTS = (15, 26)
AT = "2026-10-14T00:00:00+00:00"
COUNTS = {"R0": (17, 31), "R1": (17, 31), "R2": (15, 26)}
RECORDS = ["exchange-manifest.json", "graph-manifest.json", "publication-receipt.json", "source-manifest.json"]


def without_neo4j():
    """Run with LIONG_NEO4J unset, whatever the environment holds."""
    saved = os.environ.pop("LIONG_NEO4J", None)
    return lambda: saved is not None and os.environ.__setitem__("LIONG_NEO4J", saved)


class SliceTest(unittest.TestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.out)
        self.addCleanup(without_neo4j())

    def test_accepted_revisions_match_the_answer_key_exactly(self):
        for revision, (nodes, edges) in COUNTS.items():
            result = run_slice.run(revision, self.out / revision, now=AT)
            report = compare_answer_key.compare(result, KEY, revision)
            with self.subTest(revision=revision):
                self.assertEqual((report["match"], report["nodes"], report["edges"]), (True, nodes, edges))

    def test_w_sp_matches_its_answer_key_exactly(self):
        result = run_slice.run("W0", self.out, now=AT, backend="sps")
        report = compare_answer_key.compare(result, WSP_KEY, "W0")
        self.assertEqual((report["match"], report["differences"], report["nodes"], report["edges"]),
                         (True, [], *WSP_COUNTS))
        exchange = json.loads((self.out / "exchange-manifest.json").read_text())
        self.assertEqual(exchange["validation"]["passed"], ["schema", "references", "model", "liong_rules"])
        self.assertEqual(exchange["validation"]["round_trip"], [])
        self.assertEqual(sorted(exchange["files"]), ["DEMO-PID-101.xml", "DEMO-PID-102.xml", "sidecar.json"])
        source = json.loads((self.out / "source-manifest.json").read_text())
        self.assertEqual((source["source_id"], source["origin_uri"]), ("sps", "snapshot:fixtures/sps-wsp/W0"))

    def test_the_command_takes_the_backend(self):
        self.assertEqual(run_slice.main(["W0", str(self.out), "--backend", "sps", "--answer-key",
                                         str(ROOT / "fixtures" / "answer-keys" / "sps-wsp.json")]), 0)
        self.assertEqual(json.loads((self.out / "comparison" / "report.json").read_text())["match"], True)
        self.assertEqual(run_slice.main(["W0", str(self.out), "--backend", "xyz"]), 2)
        self.assertEqual(run_slice.main(["W0", str(self.out), "--backend"]), 2)

    def test_a_run_writes_the_four_records(self):
        run_slice.run("R0", self.out, now=AT)
        for name in RECORDS:
            self.assertTrue((self.out / name).is_file(), name)
        exchange = json.loads((self.out / "exchange-manifest.json").read_text())
        self.assertEqual(exchange["validation"]["passed"], ["schema", "references", "model", "liong_rules"])
        self.assertEqual(sorted(exchange["files"]), ["DEMO-PID-001.xml", "DEMO-PID-002.xml", "sidecar.json"])
        receipt = json.loads((self.out / "publication-receipt.json").read_text())
        self.assertEqual(receipt, {"outcome": "not published", "reason": "LIONG_NEO4J is not set"})
        manifest = json.loads((self.out / "graph-manifest.json").read_text())
        self.assertEqual((manifest["nodes"], manifest["edges"]), (17, 31))

    def test_rbad_is_rejected_before_anything_is_published(self):
        result = run_slice.run("Rbad", self.out, now=AT)
        self.assertEqual(result, {"outcome": "rejected",
                                  "reason": "FLOW p3d:object:114->p3d:object:104 has missing endpoint p3d:object:104"})
        self.assertEqual(compare_answer_key.compare(result, KEY, "Rbad")["reason"], "FLOW P6->VB has missing endpoint VB")
        self.assertFalse((self.out / "dexpi").exists())
        self.assertFalse((self.out / "graph.json").exists())
        self.assertFalse((self.out / "publication-receipt.json").exists())

    def test_a_rejected_run_leaves_no_earlier_run_beside_it(self):
        run_slice.run("R0", self.out, now=AT)
        run_slice.run("Rbad", self.out, now=AT)
        self.assertEqual(sorted(p.name for p in self.out.iterdir()),
                         ["exchange-manifest.json", "result.json", "source-manifest.json", "source-records.json"])

    def test_steps_two_to_five_never_open_an_answer_key(self):
        # Watched from before run_slice's import, in a fresh process, so a read at import
        # time counts as well as one during the run
        opened = answer_key_guard.files_opened(
            "import run_slice\nfrom pathlib import Path\n"
            f"for revision in ('R0', 'Rbad'):\n    run_slice.run(revision, Path({str(self.out)!r}) / revision, now={AT!r})\n")
        self.assertTrue(opened, "the guard saw no file opened, so it proves nothing")
        self.assertFalse([path for path in opened if "answer-keys" in path])

    def test_the_command_compares_and_exits_by_the_result(self):
        self.assertEqual(run_slice.main(["R0", str(self.out), "--answer-key",
                                         str(ROOT / "fixtures" / "answer-keys" / "p3d-r0.json")]), 0)
        self.assertEqual(json.loads((self.out / "comparison" / "report.json").read_text())["match"], True)


@unittest.skipUnless(os.environ.get("LIONG_NEO4J"), "LIONG_NEO4J is not set; CI runs these against Neo4j")
class PublishedSliceTest(unittest.TestCase):
    def test_every_accepted_revision_is_published_and_matches_when_read_back(self):
        for revision, (nodes, edges) in COUNTS.items():
            out = Path(tempfile.mkdtemp())
            self.addCleanup(shutil.rmtree, out)
            result = run_slice.run(revision, out, now=AT)
            receipt = json.loads((out / "publication-receipt.json").read_text())
            with self.subTest(revision=revision):
                self.assertIn(receipt["outcome"], ("published", "unchanged"))
                self.assertEqual((receipt["node_count"], receipt["edge_count"]), (nodes, edges))
                self.assertTrue(compare_answer_key.compare(result, KEY, revision)["match"])

    def test_r0_is_published_read_back_and_queried(self):
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out)
        result = run_slice.run("R0", out, now=AT)
        self.assertTrue(compare_answer_key.compare(result, KEY, "R0")["match"])
        receipt = json.loads((out / "publication-receipt.json").read_text())
        self.assertIn(receipt["outcome"], ("published", "unchanged"))
        self.assertEqual((receipt["node_count"], receipt["edge_count"]), (17, 31))
        query = json.loads((out / "query.json").read_text())
        self.assertEqual([(q["from_label"], q["from_sheet"], q["to_label"], q["to_sheet"]) for q in query],
                         [("TO-S2/A", "DEMO-PID-001", "FROM-S1/A", "DEMO-PID-002")])
        self.assertEqual(query[0]["evidence"], [{"RowId": 1, "table": "SheetConnectorLink"}])
        run_slice.run("Rbad", out, now=AT)
        self.assertFalse((out / "query.json").exists())

    def test_w_sp_is_published_read_back_and_queried(self):
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out)
        result = run_slice.run("W0", out, now=AT, backend="sps")
        self.assertTrue(compare_answer_key.compare(result, WSP_KEY, "W0")["match"])
        receipt = json.loads((out / "publication-receipt.json").read_text())
        self.assertIn(receipt["outcome"], ("published", "unchanged"))
        self.assertEqual((receipt["source_revision"], receipt["node_count"], receipt["edge_count"]),
                         ("sps:revision:W0", *WSP_COUNTS))
        query = json.loads((out / "query.json").read_text())
        to_link, from_link = WSP_KEY["keys"]["X1"], WSP_KEY["keys"]["X2"]
        self.assertEqual([(q["from_id"], q["from_label"], q["from_sheet"], q["to_id"], q["to_label"], q["to_sheet"])
                          for q in query],
                         [(f"sps:item:{to_link}", "TO-S2/B", "DEMO-PID-101", f"sps:item:{from_link}", "FROM-S1/B",
                           "DEMO-PID-102")])
        self.assertEqual(query[0]["evidence"], [{"table": "SheetLink", "ItemGuid": to_link,
                                                 "via": [{"table": "SheetLink", "ItemGuid": from_link}]}])
        self.assertEqual(query[0]["from_evidence"][0], {"table": "DesignItem", "ItemGuid": to_link})


class CiServicesTest(unittest.TestCase):
    """CI cannot run the checks without both servers, so their tests cannot silently skip there."""

    def run_guard(self, **env) -> subprocess.CompletedProcess:
        base = {k: v for k, v in os.environ.items() if k not in ("CI", "LIONG_SQLSERVER", "LIONG_NEO4J")}
        return subprocess.run(["bash", str(ROOT / "scripts" / "require_ci_services.sh")], env=base | env,
                              capture_output=True, text=True)

    def test_ci_without_a_server_setting_fails(self):
        for env, missing in (({"CI": "true", "LIONG_NEO4J": "x"}, "LIONG_SQLSERVER"),
                             ({"CI": "true", "LIONG_SQLSERVER": "x"}, "LIONG_NEO4J"),
                             ({"CI": "true", "LIONG_SQLSERVER": "x", "LIONG_NEO4J": ""}, "LIONG_NEO4J")):
            result = self.run_guard(**env)
            with self.subTest(missing=missing):
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"CI must set {missing}", result.stderr)

    def test_ci_with_both_settings_and_a_laptop_pass(self):
        self.assertEqual(self.run_guard(CI="true", LIONG_SQLSERVER="x", LIONG_NEO4J="y").returncode, 0)
        self.assertEqual(self.run_guard().returncode, 0)

    def test_the_check_script_runs_the_guard_before_any_check(self):
        lines = (ROOT / "scripts" / "check.sh").read_text(encoding="utf-8").splitlines()
        first_check = next(i for i, line in enumerate(lines) if line.startswith("uv run"))
        self.assertIn("scripts/require_ci_services.sh", lines[:first_check])


@unittest.skipUnless(os.environ.get("LIONG_SQLSERVER"), "LIONG_SQLSERVER is not set; CI runs these against SQL Server")
class DatabaseSliceTest(unittest.TestCase):
    def setUp(self):
        import pytds

        host, port, user, password = os.environ["LIONG_SQLSERVER"].split(",", 3)
        for attempt in range(60):  # a fresh SQL Server container takes several seconds to accept logins
            try:
                self.admin = pytds.connect(dsn=host, port=int(port), user=user, password=password, autocommit=True)
                break
            except (pytds.Error, OSError):
                if attempt == 59:
                    raise
                time.sleep(2)
        self.database = f"liong_slice_{uuid.uuid4().hex[:8]}"
        self.admin.cursor().execute(f"CREATE DATABASE {self.database}")
        self.setting = f"{host},{port},{user},{password},{self.database}"
        self.addCleanup(self.drop)
        self.addCleanup(without_neo4j())

    def drop(self):
        self.admin.cursor().execute(f"ALTER DATABASE {self.database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.admin.cursor().execute(f"DROP DATABASE {self.database}")
        self.admin.close()

    def test_the_slice_reads_the_loaded_backend(self):
        loader = run_slice.extract_p3d.loader
        with loader.connect(self.setting) as conn:
            loader.create(conn)
            loader.load(conn, run_slice.SNAPSHOTS / "R0")
        saved = os.environ["LIONG_SQLSERVER"]
        os.environ["LIONG_SQLSERVER"] = self.setting
        self.addCleanup(os.environ.__setitem__, "LIONG_SQLSERVER", saved)
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out)
        result = run_slice.run("R0", out, database=True, now=AT)
        self.assertTrue(compare_answer_key.compare(result, KEY, "R0")["match"])
        source = json.loads((out / "source-manifest.json").read_text())
        self.assertEqual(source["origin_uri"], f"sqlserver:{self.database}/p3d")

    def test_the_slice_reads_the_loaded_smartplant_style_backend(self):
        loader = run_slice.extract_sps.loader
        with loader.connect(self.setting) as conn:
            loader.create(conn)
            loader.load(conn, ROOT / "fixtures" / "sps-wsp" / "W0")
        saved = os.environ["LIONG_SQLSERVER"]
        os.environ["LIONG_SQLSERVER"] = self.setting
        self.addCleanup(os.environ.__setitem__, "LIONG_SQLSERVER", saved)
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out)
        result = run_slice.run("W0", out, database=True, now=AT, backend="sps")
        report = compare_answer_key.compare(result, WSP_KEY, "W0")
        self.assertEqual((report["match"], report["differences"]), (True, []))
        source = json.loads((out / "source-manifest.json").read_text())
        self.assertEqual(source["origin_uri"], f"sqlserver:{self.database}/sps")
        snapshot = json.loads((out / "source-records.json").read_text())
        self.assertEqual(snapshot, run_slice.extract_sps.extract(
            *run_slice.extract_sps.rows_from_snapshot(ROOT / "fixtures" / "sps-wsp" / "W0"),
            f"sqlserver:{self.database}/sps", AT))


if __name__ == "__main__":
    unittest.main()
