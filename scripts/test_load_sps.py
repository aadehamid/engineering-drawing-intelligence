#!/usr/bin/env python3
"""Load W-SP's SmartPlant-style snapshot into SQL Server and check what the database holds.

These tests need a server: set LIONG_SQLSERVER to "host,port,user,password"; CI sets it.
Each test gets a fresh database, so revisions never leak between tests.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_p3d  # noqa: E402
import load_sps as loader  # noqa: E402

SNAPSHOTS = load_p3d.ROOT / "fixtures" / "sps-wsp"
P3D_SNAPSHOTS = load_p3d.ROOT / "fixtures" / "p3d-r0"


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
        self.database = f"liong_load_sps_{uuid.uuid4().hex[:8]}"
        self.admin.cursor().execute(f"CREATE DATABASE {self.database}")
        self.conn = loader.connect(f"{host},{port},{user},{password},{self.database}")
        loader.create(self.conn)

    def tearDown(self):
        self.conn.close()
        self.admin.cursor().execute(f"ALTER DATABASE {self.database} SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.admin.cursor().execute(f"DROP DATABASE {self.database}")
        self.admin.close()

    def all(self, sql: str) -> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = [tuple(r) for r in cursor.fetchall()]
        self.conn.commit()
        return rows

    def count(self, table: str) -> int:
        return self.all(f"SELECT COUNT(*) FROM {table}")[0][0]

    def events(self) -> list[tuple]:
        return self.all("SELECT Backend, World, Revision, Status FROM outbox.PendingEvent ORDER BY LoadSequence")

    def test_w0_loads_with_its_pending_event(self):
        self.assertEqual(loader.load(self.conn, SNAPSHOTS / "W0"), "loaded")
        # 14 items, 22 depictions and 2 sheets, as test_generate_sps.py pins by hand
        self.assertEqual((self.count("sps.DesignItem"), self.count("sps.Depiction"), self.count("sps.Sheet")),
                         (14, 22, 2))
        self.assertEqual(self.events(), [("sps", "W-SP", "W0", "Pending")])
        self.assertEqual(self.all("SELECT RecordedAt FROM outbox.PendingEvent"), [(datetime(2030, 2, 1, 8, 0),)])

    def test_the_database_holds_exactly_the_snapshot_rows(self):
        loader.load(self.conn, SNAPSHOTS / "W0")
        _, _, rows = loader.read_snapshot(SNAPSHOTS / "W0")
        for table, columns in loader.COLUMNS.items():
            found = self.all(f"SELECT {', '.join(columns)} FROM sps.{table}")
            plain = [tuple(str(v).upper() if type(v).__name__ == "UUID" else
                           v.isoformat() if isinstance(v, datetime) else v for v in row) for row in found]
            self.assertEqual(sorted(plain, key=repr), sorted((tuple(r[c] for c in columns) for r in rows[table]), key=repr),
                             table)

    def test_reloading_a_revision_changes_nothing(self):
        loader.load(self.conn, SNAPSHOTS / "W0")
        self.assertEqual(loader.load(self.conn, SNAPSHOTS / "W0"), "unchanged")
        self.assertEqual(len(self.events()), 1)

    def test_interrupted_load_leaves_no_rows_and_no_event(self):
        def crash():
            raise RuntimeError("power cut")

        with self.assertRaises(RuntimeError):
            loader.load(self.conn, SNAPSHOTS / "W0", before_commit=crash)
        self.assertEqual((self.count("sps.DesignItem"), self.events()), (0, []))

    def copy_with(self, tmp: str, table: str, edit) -> Path:
        """A copy of the snapshot whose W0 table is edited and whose manifest is rehashed to match."""
        copy = Path(tmp) / "sps-wsp"
        shutil.copytree(SNAPSHOTS, copy)
        path = copy / "W0" / f"{table}.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        edit(rows)
        path.write_text(json.dumps(rows), encoding="utf-8")
        manifest = json.loads((copy / "manifest.json").read_text(encoding="utf-8"))
        manifest["files"][f"W0/{table}.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        (copy / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return copy

    def test_file_that_differs_from_the_manifest_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "sps-wsp"
            shutil.copytree(SNAPSHOTS, copy)
            path = copy / "W0" / "Vessel.json"
            path.write_text(path.read_text(encoding="utf-8").replace("TK-301", "TK-999"), encoding="utf-8")
            with self.assertRaisesRegex(loader.LoadError, "W0/Vessel.json does not match the manifest"):
                loader.load(self.conn, copy / "W0")
        self.assertEqual((self.count("sps.DesignItem"), self.events()), (0, []))

    def test_a_column_name_from_a_file_is_never_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = self.copy_with(tmp, "Vessel",
                                  lambda rows: rows[0].update({"ItemTag) VALUES (1); DROP TABLE sps.Nozzle; --": 1}))
            with self.assertRaisesRegex(loader.LoadError, "whose columns are not sps.Vessel's"):
                loader.load(self.conn, copy / "W0")
        self.assertEqual((self.count("sps.DesignItem"), self.count("sps.Nozzle"), self.events()), (0, 0, []))

    def test_a_snapshot_for_the_other_backend_is_refused(self):
        with self.assertRaisesRegex(loader.LoadError, "for backend p3d, not sps"):
            loader.load(self.conn, P3D_SNAPSHOTS / "R0")
        self.assertEqual(self.events(), [])

    def test_a_duplicate_vessel_tag_rolls_back_the_whole_load(self):
        import pytds

        with tempfile.TemporaryDirectory() as tmp:
            copy = self.copy_with(tmp, "Vessel", lambda rows: rows[1].update(ItemTag="TK-301"))
            with self.assertRaises(pytds.IntegrityError):
                loader.load(self.conn, copy / "W0")
        self.assertEqual((self.count("sps.DesignItem"), self.count("sps.Vessel"), self.events()), (0, 0, []))

    def test_both_backends_share_one_database_and_one_outbox(self):
        # DEC-028 and DEC-047: p3d and sps side by side, with one outbox created once
        load_p3d.create(self.conn)
        load_p3d.load(self.conn, P3D_SNAPSHOTS / "R0")
        loader.load(self.conn, SNAPSHOTS / "W0")
        self.assertEqual(self.events(), [("p3d", "R0", "R0", "Pending"), ("sps", "W-SP", "W0", "Pending")])
        self.assertEqual((self.count("p3d.PlantObject"), self.count("sps.DesignItem")), (15, 14))


class OfflineTests(unittest.TestCase):
    def test_columns_match_the_schema_file(self):
        import test_smartplant_schema as schema

        found = schema.tables(schema.DDL.read_text(encoding="utf-8"))
        self.assertEqual({t: tuple(found[t]) for t in loader.COLUMNS}, loader.COLUMNS)

    def test_the_loader_fills_every_table_the_generator_writes(self):
        import generate_sps

        self.assertEqual(tuple(loader.COLUMNS), generate_sps.TABLES)

    def test_the_snapshot_reads_without_a_server(self):
        record, payload, rows = loader.read_snapshot(SNAPSHOTS / "W0")
        self.assertEqual(record, {"base": None, "moc": None, "recorded_at": "2030-02-01T08:00:00",
                                  "world": "W-SP", "backend": "sps", "revision": "W0"})
        self.assertEqual(len(payload), 64)


if __name__ == "__main__":
    unittest.main()
