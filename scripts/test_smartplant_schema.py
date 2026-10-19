#!/usr/bin/env python3
"""Check the SmartPlant-style schema file, and apply it to SQL Server when one is reachable.

The static tests read schemas/smartplant-style.sql. The live tests run when
LIONG_SQLSERVER is set to "host,port,user,password"; CI sets it for its SQL Server
service container, and scripts/require_ci_services.sh stops CI from skipping them.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
DDL = ROOT / "schemas" / "smartplant-style.sql"
CLASS_TABLES = ("Vessel", "Instrument", "PipeRun", "PipingFitting", "Nozzle", "ProcessConnection", "SheetLink")
# Every table DEC-081's patterns and DEC-082 call for, written out so that dropping one fails.
EXPECTED_TABLES = {
    "DesignItem", *CLASS_TABLES,                       # pattern 1, with patterns 2, 5, 6 and 7's classes
    "Depiction", "LineDepiction", "LabelDepiction",    # patterns 1 and 2
    "InlinePlacement", "PortPoint",                    # pattern 3
    "Sheet", "SheetRevision",                          # sheets and their revision rows
    "ItemType", "ItemProperty", "SelectEntry",         # the data dictionary (DEC-032)
}
TYPES = r"INT|BIGINT|NVARCHAR|UNIQUEIDENTIFIER|DATETIME2"


def batches(text: str) -> list[str]:
    """The batches a SQL Server client sends: the text between lines that hold only GO."""
    return [b.strip() for b in re.split(r"^\s*GO\s*$", text, flags=re.MULTILINE | re.IGNORECASE) if b.strip()]


def tables(text: str) -> dict[str, list[str]]:
    """Each sps table's column names, read from its CREATE TABLE statement."""
    return {name: re.findall(rf"^\s+(\w+)\s+(?:{TYPES})", body, re.MULTILINE)
            for name, body in re.findall(r"CREATE TABLE sps\.(\w+) \((.*?)\n\);", text, re.DOTALL)}


def dictionary_rows(text: str, table: str) -> list[tuple[str, ...]]:
    """The value tuples of the INSERT into sps.<table>, one row per line, NULL kept as "NULL"."""
    block = re.search(rf"INSERT INTO sps\.{table} \(.*?\) VALUES\n(.*?);", text, re.DOTALL)
    assert block, table
    return [tuple(quoted or bare for quoted, bare in re.findall(r"N'([^']*)'|\b(NULL|\d+)\b", line))
            for line in re.findall(r"^\s*\((.*)\),?$", block.group(1), re.MULTILINE)]


class StaticSchemaTests(unittest.TestCase):
    text = DDL.read_text(encoding="utf-8")

    def test_the_file_creates_exactly_the_expected_tables(self):
        self.assertEqual(set(tables(self.text)), EXPECTED_TABLES)

    def test_everything_is_in_schema_sps(self):
        created = re.findall(r"CREATE (?:TABLE|SCHEMA|UNIQUE INDEX \w+ ON) (\w+)", self.text)
        self.assertEqual(set(created), {"sps"})

    def test_no_foreign_keys(self):
        # DEC-043: the product keeps integrity in the application, not the database
        sql = re.sub(r"--[^\n]*", "", self.text).upper()
        self.assertIsNone(re.search(r"FOREIGN\s+KEY|REFERENCES", sql))

    def test_base_table_has_guid_kind_and_state(self):
        self.assertEqual(tables(self.text)["DesignItem"], ["ItemGuid", "ItemKind", "ItemState"])

    def test_every_class_table_shares_the_item_key(self):
        cols = tables(self.text)
        for name in CLASS_TABLES:
            self.assertEqual(cols[name][0], "ItemGuid", name)

    def test_every_key_is_a_guid(self):
        for name, body in re.findall(r"CREATE TABLE sps\.(\w+) \((.*?)\n\);", self.text, re.DOTALL):
            key = re.search(r"^\s+(\w+)\s+(\w+).*PRIMARY KEY", body, re.MULTILINE)
            if name in ("ItemType", "ItemProperty", "SelectEntry"):
                continue  # dictionary tables are keyed by name
            self.assertIsNotNone(key, name)
            self.assertEqual(key.group(2), "UNIQUEIDENTIFIER", name)

    def test_items_carry_no_sheet_key(self):
        # Pattern 1: only depictions and the sheet tables hold a sheet key. A sheet link
        # holds its mate's sheet (pattern 5), which is not its own.
        for name, cols in tables(self.text).items():
            if name not in ("Depiction", "Sheet", "SheetRevision"):
                self.assertNotIn("SheetGuid", cols, name)
        self.assertIn("MateSheet", tables(self.text)["SheetLink"])

    def test_line_depictions_name_both_end_marks_and_runs_hold_the_flow_sense(self):
        cols = tables(self.text)
        self.assertEqual(cols["LineDepiction"], ["DepictionGuid", "End1Mark", "End2Mark"])
        self.assertIn("FlowSense", cols["PipeRun"])

    def test_run_membership_is_its_own_row(self):
        cols = tables(self.text)
        self.assertEqual(cols["InlinePlacement"], ["PlacementGuid", "ItemGuid", "RunGuid"])
        self.assertNotIn("RunGuid", cols["PipingFitting"])
        self.assertIn("CONSTRAINT UQ_PortPoint_Owner UNIQUE (OwnerItem, PointNo)", self.text)

    def test_no_table_records_a_pipeline(self):
        # Pattern 4: runs carry the line-number parts and no row groups them
        for name, cols in tables(self.text).items():
            self.assertNotIn("pipeline", name.lower())
            self.assertFalse([c for c in cols if "pipeline" in c.lower()], name)

    def test_sheet_links_store_their_mate_on_both_sides(self):
        self.assertEqual(tables(self.text)["SheetLink"], ["ItemGuid", "LinkLabel", "LinkSense", "MateItem", "MateSheet"])

    def test_nozzles_store_their_parent(self):
        self.assertIn("ParentItem", tables(self.text)["Nozzle"])

    def test_composed_tags_are_unique_for_vessels_and_instruments_and_per_vessel_for_nozzles(self):
        unique = set(re.findall(r"CREATE UNIQUE INDEX \w+ ON sps\.(\w+) \(ItemTag\) WHERE ItemTag IS NOT NULL", self.text))
        self.assertEqual(unique, {"Vessel", "Instrument"})
        self.assertIn("ON sps.Nozzle (ParentItem, ItemTag) WHERE ItemTag IS NOT NULL", self.text)
        # Pipe runs and fittings have none: three unique indexes in all
        self.assertEqual(len(re.findall(r"CREATE UNIQUE INDEX", self.text)), 3)

    def test_revision_numbers_are_unique_together_on_their_sheet(self):
        self.assertIn("CONSTRAINT UQ_SheetRevision_Number UNIQUE (SheetGuid, MajorRev, MinorRev)", self.text)

    def test_dictionary_describes_every_class_table_and_column(self):
        cols = tables(self.text)
        kinds = dictionary_rows(self.text, "ItemType")
        self.assertEqual({row[2] for row in kinds}, {"DesignItem", *CLASS_TABLES})
        described = {(kind, prop) for kind, prop, *_ in dictionary_rows(self.text, "ItemProperty")}
        for kind, prop in described:
            self.assertIn(prop, cols[kind], f"{kind}.{prop}")
        for name in ("DesignItem", *CLASS_TABLES):
            for col in cols[name][1:]:
                self.assertIn((name, col), described, f"{name}.{col} has no ItemProperty row")

    def test_tag_parts_are_numbered_from_one(self):
        rows = dictionary_rows(self.text, "ItemProperty")
        for name in ("Vessel", "Instrument", "PipeRun"):
            parts = sorted(int(r[4]) for r in rows if r[0] == name and r[4] != "NULL")
            self.assertEqual(parts, [1, 2, 3], name)

    def test_every_select_list_named_has_entries(self):
        named = {r[5] for r in dictionary_rows(self.text, "ItemProperty") if r[5] != "NULL"}
        listed = {r[0] for r in dictionary_rows(self.text, "SelectEntry")}
        self.assertEqual(named, {"ItemState", "FlowSense", "LinkSense"})
        self.assertEqual(listed, named | {"DepictionKind"})

    def test_no_vendor_names(self):
        # DEC-081: no vendor table or column name. These are the prefixes and names the
        # research lists as not to be copied.
        for vendor in ("T_", "SP_", "ModelItem", "Representation", "TagSequenceNo", "ItemStatus",
                       "InStockpile", "MatingOPC", "PlantItem"):
            self.assertNotIn(vendor, re.sub(r"--[^\n]*", "", self.text), vendor)


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
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'sps'")}
        self.assertEqual(found, EXPECTED_TABLES)

    def test_server_holds_no_foreign_keys(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM sys.foreign_keys")[0][0], 0)

    def assert_second_tag(self, table: str, unique: bool) -> None:
        import pytds

        cursor = self.conn.cursor()
        insert = f"INSERT INTO sps.{table} (ItemGuid, ItemTag) VALUES (%s, N'X-301')"
        cursor.execute(insert, (str(uuid.uuid4()),))
        try:
            if unique:
                with self.assertRaises(pytds.IntegrityError):
                    cursor.execute(insert, (str(uuid.uuid4()),))
            else:
                cursor.execute(insert, (str(uuid.uuid4()),))
        finally:
            cursor.execute(f"DELETE FROM sps.{table}")

    def test_duplicate_vessel_tag_is_rejected(self):
        self.assert_second_tag("Vessel", unique=True)

    def test_duplicate_instrument_tag_is_rejected(self):
        self.assert_second_tag("Instrument", unique=True)

    def test_pipe_runs_may_share_a_composed_tag(self):
        import pytds

        cursor = self.conn.cursor()
        insert = ("INSERT INTO sps.PipeRun (ItemGuid, ItemTag, TagLead, TagNumber, FlowSense) "
                  "VALUES (%s, N'L-301', N'L', N'301', N'End1Upstream')")
        try:
            cursor.execute(insert, (str(uuid.uuid4()),))
            cursor.execute(insert, (str(uuid.uuid4()),))
            cursor.execute("SELECT COUNT(*) FROM sps.PipeRun WHERE ItemTag = N'L-301'")
            self.assertEqual(cursor.fetchone()[0], 2)
        except pytds.IntegrityError:
            self.fail("a second pipe run with the same composed tag was refused")
        finally:
            cursor.execute("DELETE FROM sps.PipeRun")

    def test_fitting_tags_may_repeat(self):
        self.assert_second_tag("PipingFitting", unique=False)

    def test_nozzle_tags_are_unique_within_their_vessel_only(self):
        import pytds

        cursor = self.conn.cursor()
        insert = "INSERT INTO sps.Nozzle (ItemGuid, ItemTag, ParentItem) VALUES (%s, N'N1', %s)"
        first, second = str(uuid.uuid4()), str(uuid.uuid4())
        try:
            cursor.execute(insert, (str(uuid.uuid4()), first))
            cursor.execute(insert, (str(uuid.uuid4()), second))  # the same tag on another vessel
            with self.assertRaises(pytds.IntegrityError):
                cursor.execute(insert, (str(uuid.uuid4()), first))
        finally:
            cursor.execute("DELETE FROM sps.Nozzle")

    def test_revision_numbers_are_unique_on_a_sheet(self):
        import pytds

        cursor = self.conn.cursor()
        insert = ("INSERT INTO sps.SheetRevision (RevisionGuid, SheetGuid, MajorRev, MinorRev, RevisedOn, ApprovalState) "
                  "VALUES (%s, %s, N'W0', N'0', '2030-02-01T08:00:00', N'Approved')")
        first, second = str(uuid.uuid4()), str(uuid.uuid4())
        try:
            cursor.execute(insert, (str(uuid.uuid4()), first))
            cursor.execute(insert, (str(uuid.uuid4()), second))  # the same numbers on another sheet
            with self.assertRaises(pytds.IntegrityError):
                cursor.execute(insert, (str(uuid.uuid4()), first))
        finally:
            cursor.execute("DELETE FROM sps.SheetRevision")

    def test_port_point_numbers_are_unique_on_their_owner(self):
        import pytds

        cursor = self.conn.cursor()
        owner = str(uuid.uuid4())
        insert = "INSERT INTO sps.PortPoint (PointGuid, OwnerItem, PointNo) VALUES (%s, %s, 1)"
        try:
            cursor.execute(insert, (str(uuid.uuid4()), owner))
            with self.assertRaises(pytds.IntegrityError):
                cursor.execute(insert, (str(uuid.uuid4()), owner))
        finally:
            cursor.execute("DELETE FROM sps.PortPoint")

    def test_dictionary_rows_are_loaded(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM sps.ItemType")[0][0], 1 + len(CLASS_TABLES))
        self.assertEqual(self.query("SELECT COUNT(*) FROM sps.SelectEntry")[0][0], 9)


if __name__ == "__main__":
    unittest.main()
