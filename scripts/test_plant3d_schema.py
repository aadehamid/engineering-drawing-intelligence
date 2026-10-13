#!/usr/bin/env python3
"""Check the Plant 3D-style schema file, and apply it to SQL Server when one is reachable.

The static tests read schemas/plant3d-style.sql. The live tests run when LIONG_SQLSERVER
is set to "host,port,user,password"; CI sets it for its SQL Server service container.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "schemas" / "plant3d-style.sql"
CLASS_TABLES = ("Equipment", "Valve", "Instrument", "LineSegment", "Junction", "SheetConnector")
# Every table DEC-040's patterns and DEC-049 call for, written out so that dropping one fails.
EXPECTED_TABLES = {
    "PlantObject", *CLASS_TABLES,
    "SegmentStart", "SegmentEnd", "ConnectorPair", "Ownership",  # pattern 2 and the ownership row
    "SheetConnectorLink",                                         # pattern 4
    "Drawing", "DrawingAppearance",                               # pattern 3
    "WorkHistory",                                                # DEC-037
    "ClassDefinition", "PropertyDefinition",                      # pattern 6
}


def batches(text: str) -> list[str]:
    """The batches a SQL Server client sends: the text between lines that hold only GO."""
    return [b.strip() for b in re.split(r"^\s*GO\s*$", text, flags=re.MULTILINE | re.IGNORECASE) if b.strip()]


def tables(text: str) -> dict[str, list[str]]:
    """Each p3d table's column names, read from its CREATE TABLE statement."""
    found = {}
    for name, body in re.findall(r"CREATE TABLE p3d\.(\w+) \((.*?)\n\);", text, re.DOTALL):
        found[name] = [m for m in re.findall(r"^\s+(\w+)\s+(?:INT|BIGINT|NVARCHAR|UNIQUEIDENTIFIER|DATETIME2)", body, re.MULTILINE)]
    return found


def dictionary_rows(text: str, table: str) -> list[tuple[str, ...]]:
    """The value tuples of the INSERT into p3d.<table>, one row per line, NULL kept as "NULL"."""
    block = re.search(rf"INSERT INTO p3d\.{table} \(.*?\) VALUES\n(.*?);", text, re.DOTALL)
    assert block, table
    return [tuple(quoted or bare for quoted, bare in re.findall(r"N'([^']*)'|\b(NULL|\d+)\b", line))
            for line in re.findall(r"^\s*\((.*)\),?$", block.group(1), re.MULTILINE)]


class StaticSchemaTests(unittest.TestCase):
    text = DDL.read_text(encoding="utf-8")

    def test_the_file_creates_exactly_the_expected_tables(self):
        self.assertEqual(set(tables(self.text)), EXPECTED_TABLES)

    def test_no_foreign_keys(self):
        # DEC-043: the product keeps integrity in the application, not the database
        sql = re.sub(r"--[^\n]*", "", self.text).upper()
        self.assertIsNone(re.search(r"FOREIGN\s+KEY|REFERENCES", sql))

    def test_every_class_table_shares_the_project_wide_key(self):
        cols = tables(self.text)
        for name in CLASS_TABLES:
            self.assertIn(name, cols)
            self.assertEqual(cols[name][0], "ObjectId", name)

    def test_base_table_has_key_guid_class_revision_and_status(self):
        self.assertEqual(tables(self.text)["PlantObject"],
                         ["ObjectId", "ObjectGuid", "ClassName", "Revision", "Status", "RowStamp"])

    def test_objects_carry_no_drawing_id(self):
        # Pattern 3: only DrawingAppearance and WorkHistory name a drawing
        for name, cols in tables(self.text).items():
            if name not in ("Drawing", "DrawingAppearance", "WorkHistory"):
                self.assertNotIn("DrawingId", cols, name)

    def test_composed_tags_are_unique_in_each_tagged_class(self):
        for name in ("Equipment", "Valve", "Instrument", "LineSegment"):
            self.assertIn(f"CREATE UNIQUE INDEX UX_{name}_Tag ON p3d.{name} (Tag) WHERE Tag IS NOT NULL", self.text)

    def test_dictionary_describes_every_class_table_and_column(self):
        cols = tables(self.text)
        classes = dictionary_rows(self.text, "ClassDefinition")
        self.assertEqual({row[2] for row in classes}, {"PlantObject", *CLASS_TABLES})
        for class_name, prop, *_ in dictionary_rows(self.text, "PropertyDefinition"):
            self.assertIn(prop, cols[class_name], f"{class_name}.{prop}")
        described = {(c, p) for c, p, *_ in dictionary_rows(self.text, "PropertyDefinition")}
        for name in CLASS_TABLES:
            for col in cols[name][1:]:
                self.assertIn((name, col), described, f"{name}.{col} has no PropertyDefinition row")

    def test_tag_subparts_are_numbered_from_one(self):
        rows = dictionary_rows(self.text, "PropertyDefinition")
        for name in ("Equipment", "Valve", "Instrument", "LineSegment"):
            parts = sorted(int(r[4]) for r in rows if r[0] == name and r[4] != "NULL")
            self.assertEqual(parts, list(range(1, len(parts) + 1)), name)


def server() -> tuple[str, int, str, str] | None:
    value = os.environ.get("LIONG_SQLSERVER")
    if not value:
        return None
    host, port, user, password = value.split(",", 3)
    return host, int(port), user, password


@unittest.skipUnless(server(), "LIONG_SQLSERVER is not set; CI runs these against SQL Server")
class LiveSchemaTests(unittest.TestCase):
    """Apply the schema to a fresh database and read it back from SQL Server's catalog."""

    @classmethod
    def setUpClass(cls):
        import pytds

        host, port, user, password = server()
        cls.database = f"liong_test_{uuid.uuid4().hex[:8]}"
        # A fresh SQL Server container takes several seconds to accept logins
        for attempt in range(60):
            try:
                cls.admin = pytds.connect(dsn=host, port=port, user=user, password=password, autocommit=True)
                break
            except (pytds.Error, OSError):
                if attempt == 59:
                    raise
                time.sleep(2)
        cls.admin.cursor().execute(f"CREATE DATABASE {cls.database}")
        cls.conn = pytds.connect(dsn=host, port=port, user=user, password=password,
                                 database=cls.database, autocommit=True)
        for batch in batches(DDL.read_text(encoding="utf-8")):
            cls.conn.cursor().execute(batch)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.admin.cursor().execute(f"DROP DATABASE {cls.database}")
        cls.admin.close()

    def query(self, sql: str) -> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def test_tables_match_the_file(self):
        found = {row[0] for row in self.query(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'p3d'")}
        self.assertEqual(found, EXPECTED_TABLES)

    def test_server_holds_no_foreign_keys(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM sys.foreign_keys")[0][0], 0)

    def test_duplicate_composed_tag_is_rejected(self):
        import pytds

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO p3d.Equipment (ObjectId, Tag, TagType, TagNumber) VALUES (1, N'TK-101', N'TK', N'101')")
        with self.assertRaises(pytds.IntegrityError):
            cursor.execute("INSERT INTO p3d.Equipment (ObjectId, Tag, TagType, TagNumber) VALUES (2, N'TK-101', N'TK', N'101')")
        cursor.execute("DELETE FROM p3d.Equipment")

    def test_dictionary_rows_are_loaded(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM p3d.ClassDefinition")[0][0], 1 + len(CLASS_TABLES))


if __name__ == "__main__":
    unittest.main()
