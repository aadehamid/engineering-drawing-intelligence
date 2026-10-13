#!/usr/bin/env python3
"""Load R0's Plant 3D-style snapshots into SQL Server and check what the database holds.

These tests need a server: set LIONG_SQLSERVER to "host,port,user,password"; CI sets it.
Each test gets a fresh database, so revisions never leak between scenarios.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_p3d as loader  # noqa: E402

SNAPSHOTS = loader.ROOT / "fixtures" / "p3d-r0"


def server() -> str | None:
    return os.environ.get("LIONG_SQLSERVER")


@unittest.skipUnless(server(), "LIONG_SQLSERVER is not set; CI runs these against SQL Server")
class LoaderTests(unittest.TestCase):
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
        self.database = f"liong_load_{uuid.uuid4().hex[:8]}"
        self.admin.cursor().execute(f"CREATE DATABASE {self.database}")
        self.conn = loader.connect(f"{host},{port},{user},{password},{self.database}")
        loader.create(self.conn)

    def tearDown(self):
        self.conn.close()
        self.admin.cursor().execute(f"ALTER DATABASE {self.database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.admin.cursor().execute(f"DROP DATABASE {self.database}")
        self.admin.close()

    def one(self, sql: str, *params):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        self.conn.commit()
        return row

    def count(self, table: str) -> int:
        return self.one(f"SELECT COUNT(*) FROM {table}")[0]

    def events(self) -> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT Revision, Status FROM outbox.PendingEvent ORDER BY LoadSequence")
        rows = cursor.fetchall()
        self.conn.commit()
        return [tuple(r) for r in rows]

    def test_r0_loads_with_its_pending_event(self):
        self.assertEqual(loader.load(self.conn, SNAPSHOTS / "R0"), "loaded")
        self.assertEqual((self.count("p3d.PlantObject"), self.count("p3d.Drawing")), (15, 2))
        self.assertEqual(self.events(), [("R0", "Pending")])

    def test_revisions_load_in_order_and_keep_keys(self):
        for revision in ("R0", "R1", "R2"):
            loader.load(self.conn, SNAPSHOTS / revision)
        self.assertEqual(self.one("SELECT Tag FROM p3d.Equipment WHERE ObjectId = 102")[0], "TK-202")
        self.assertEqual(self.count("p3d.PlantObject"), 13)
        self.assertEqual([r for r, _ in self.events()], ["R0", "R1", "R2"])

    def test_snapshot_needs_its_base(self):
        with self.assertRaisesRegex(loader.LoadError, "has base R1, but the backend holds nothing"):
            loader.load(self.conn, SNAPSHOTS / "R2")
        self.assertEqual((self.count("p3d.PlantObject"), self.events()), (0, []))

    def test_reloading_a_revision_changes_nothing(self):
        loader.load(self.conn, SNAPSHOTS / "R0")
        self.assertEqual(loader.load(self.conn, SNAPSHOTS / "R0"), "unchanged")
        self.assertEqual(self.events(), [("R0", "Pending")])

    def test_interrupted_load_leaves_no_revision_and_no_event(self):
        # LIONG-006, interruption before source commit: nothing committed, nothing deliverable
        loader.load(self.conn, SNAPSHOTS / "R0")

        def crash():
            raise RuntimeError("power cut")

        with self.assertRaises(RuntimeError):
            loader.load(self.conn, SNAPSHOTS / "R1", before_commit=crash)
        self.assertEqual(self.one("SELECT Tag FROM p3d.Equipment WHERE ObjectId = 102")[0], "TK-102")
        self.assertEqual(self.events(), [("R0", "Pending")])

    def test_file_that_differs_from_the_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "p3d-r0"
            shutil.copytree(SNAPSHOTS, copy)
            path = copy / "R0" / "Equipment.json"
            path.write_text(path.read_text(encoding="utf-8").replace("TK-101", "TK-999"), encoding="utf-8")
            with self.assertRaisesRegex(loader.LoadError, "R0/Equipment.json does not match the manifest"):
                loader.load(self.conn, copy / "R0")
        self.assertEqual((self.count("p3d.PlantObject"), self.events()), (0, []))

    def test_rbad_loads_with_its_dangling_rows(self):
        # The database keeps no foreign keys (DEC-043): rejecting Rbad is the pipeline's job
        loader.load(self.conn, SNAPSHOTS / "R0")
        loader.load(self.conn, SNAPSHOTS / "Rbad")
        dangling = self.one(
            "SELECT COUNT(*) FROM (SELECT ObjectId AS Id FROM p3d.SegmentEnd UNION ALL SELECT Connector1 FROM p3d.ConnectorPair) r "
            "WHERE r.Id NOT IN (SELECT ObjectId FROM p3d.PlantObject)")[0]
        self.assertEqual(dangling, 2)
        self.assertEqual([r for r, _ in self.events()], ["R0", "Rbad"])


if __name__ == "__main__":
    unittest.main()
