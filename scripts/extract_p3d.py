#!/usr/bin/env python3
"""Extract source records from a Plant 3D-style backend (MILESTONE-001 step 2).

Usage:
  extract_p3d.py database OUT_FILE          read the backend LIONG_SQLSERVER names
  extract_p3d.py snapshot FOLDER OUT_FILE   read a snapshot folder, such as fixtures/p3d-r0/R0

Both read the same fifteen p3d tables and write the same records, in the shapes
LIONG-005 names: a SourceManifest, a SourceRevision, and the EngineeringObject,
TagAssignment, EngineeringAssertion and DrawingAppearance records the rows state.
Every record keeps the table and row it came from.

Extraction reads only the backend. It never opens an answer key, and it does not
judge the rows: a relationship to a missing object is kept as stated, for validation
to reject later. WorkHistory and the PlantObject bookkeeping columns (GUID, revision,
status, row stamp) feed revision handling in later milestones, not these records.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import load_p3d as loader

SOURCE_ID = "p3d"
WORLD = "R0"  # the synthetic world this backend holds (LIONG-006)
OBJECT_KIND = {
    "Equipment": "equipment", "Valve": "valve", "Instrument": "instrument",
    "LineSegment": "pipe_segment", "Junction": "junction", "SheetConnector": "sheet_connector",
}
# Attribute columns of each class table, as (column, predicate). Tag columns become TagAssignments.
ATTRIBUTES = {
    "Equipment": (("TagType", "tag_type"), ("TagNumber", "tag_number"), ("Description", "description")),
    "Valve": (("TagType", "tag_type"), ("TagNumber", "tag_number"), ("Description", "description")),
    "Instrument": (("TagType", "tag_type"), ("LoopNumber", "loop_number"), ("Unit", "unit"),
                   ("Description", "description")),
    "LineSegment": (("LinePrefix", "line_prefix"), ("LineNumber", "line_number"),
                    ("SegmentSuffix", "segment_suffix"), ("NominalSizeMm", "nominal_size_mm")),
    "Junction": (("Description", "description"),),
    "SheetConnector": (("Label", "label"), ("Direction", "direction")),
}
# Relationship tables, as (subject column, predicate, target column).
RELATIONS = {
    "SegmentStart": ("SegmentId", "starts_at", "ObjectId"),
    "SegmentEnd": ("SegmentId", "ends_at", "ObjectId"),
    "ConnectorPair": ("Connector1", "connects_to", "Connector2"),
    "SheetConnectorLink": ("OutConnector", "continues_to", "InConnector"),
    "Ownership": ("OwnedId", "owned_by", "OwnerId"),
}


def object_id(key: int) -> str:
    return f"{SOURCE_ID}:object:{key}"


def drawing_id(key: int) -> str:
    return f"{SOURCE_ID}:drawing:{key}"


def rows_from_database(conn) -> tuple[dict, dict[str, list[dict]]]:
    """(revision, rows) as the backend holds them now; the revision is the last one loaded."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 1 Revision, RecordedAt FROM outbox.PendingEvent "
        "WHERE Backend = %s AND World = %s ORDER BY LoadSequence DESC", (SOURCE_ID, WORLD))
    loaded = cursor.fetchone()
    if loaded is None:
        raise loader.LoadError("the backend holds no revision; load one first")
    rows = {}
    for table, columns in loader.COLUMNS.items():
        cursor.execute(f"SELECT {', '.join(columns)} FROM p3d.{table}")  # columns come from COLUMNS only
        rows[table] = [dict(zip(columns, (plain(value) for value in record))) for record in cursor.fetchall()]
    return {"revision": loaded[0], "recorded_at": plain(loaded[1])}, rows


def plain(value: object) -> object:
    """A database value as the snapshot files write it: GUIDs upper-case, times without an offset."""
    if isinstance(value, datetime):
        return value.isoformat()
    if type(value).__name__ == "UUID":
        return str(value).upper()
    return value


def rows_from_snapshot(folder: Path) -> tuple[dict, dict[str, list[dict]]]:
    """(revision, rows) of a snapshot folder, after checking every file against its manifest."""
    record, _, rows = loader.read_snapshot(folder)
    return {"revision": record["revision"], "recorded_at": record["recorded_at"]}, rows


def checksum(rows: dict[str, list[dict]]) -> str:
    """SHA-256 of the rows in a fixed order, so the same rows always give the same digest."""
    ordered = {table: sorted(rows[table], key=lambda row: json.dumps(row, sort_keys=True)) for table in sorted(rows)}
    return hashlib.sha256(json.dumps(ordered, sort_keys=True).encode("utf-8")).hexdigest()


def extract(revision: dict, rows: dict[str, list[dict]], origin_uri: str, captured_at: str) -> dict:
    """The source records the rows state, each pointing back to its table and row.

    `revision` holds the revision's name and the time the source recorded it.
    """
    recorded_at, revision = revision["recorded_at"], revision["revision"]
    revision_id = f"{SOURCE_ID}:revision:{revision}"
    objects, tags, assertions, drawings, appearances = [], [], [], [], []

    def assert_(subject: str, predicate: str, value: object, table: str, row_key: str, row: object) -> None:
        assertions.append({
            "assertion_id": f"{subject}/{predicate}", "subject_id": subject, "predicate": predicate,
            "value_or_target": value, "source_locator": {"table": table, row_key: row},
            "revision_id": revision_id, "evidence_status": "source_stated",
        })

    for row in rows["PlantObject"]:
        table, key = row["ClassName"], row["ObjectId"]
        objects.append({"object_id": object_id(key), "object_kind": OBJECT_KIND[table],
                        "source_object_key": key, "source_locator": {"table": "PlantObject", "ObjectId": key}})
    for table, columns in ATTRIBUTES.items():
        for row in rows[table]:
            subject = object_id(row["ObjectId"])
            if row.get("Tag") is not None:
                tags.append({"object_id": subject, "namespace": SOURCE_ID, "tag_value": row["Tag"],
                             "revision_id": revision_id, "source_locator": {"table": table, "ObjectId": row["ObjectId"]}})
            for column, predicate in columns:
                if row[column] is not None:
                    assert_(subject, predicate, row[column], table, "ObjectId", row["ObjectId"])
    for table, (subject_column, predicate, target_column) in RELATIONS.items():
        for row in rows[table]:
            assertions.append({
                "assertion_id": f"{table}/{row['RowId']}", "subject_id": object_id(row[subject_column]),
                "predicate": predicate, "value_or_target": object_id(row[target_column]),
                "source_locator": {"table": table, "RowId": row["RowId"]},
                "revision_id": revision_id, "evidence_status": "source_stated",
            })
    for row in rows["Drawing"]:
        drawings.append({"artifact_id": drawing_id(row["DrawingId"]), "name": row["FileName"],
                         "revision": row["Revision"], "status": row["Status"],
                         "source_locator": {"table": "Drawing", "DrawingId": row["DrawingId"]}})
    for row in rows["DrawingAppearance"]:
        appearances.append({"appearance_id": f"{SOURCE_ID}:appearance:{row['RowId']}",
                            "object_id": object_id(row["ObjectId"]), "artifact_id": drawing_id(row["DrawingId"]),
                            "region": row["DrawingHandle"], "coordinate_system": "p3d_drawing_handle",
                            "source_locator": {"table": "DrawingAppearance", "RowId": row["RowId"]}})
    by_id = lambda record_key: lambda record: str(record[record_key])  # noqa: E731
    return {
        "source_manifest": {"source_id": SOURCE_ID, "dataset_id": f"{SOURCE_ID}-{WORLD}", "origin_uri": origin_uri,
                            "captured_at": captured_at, "rights_ref": "synthetic, LIONG-006",
                            "provenance_kind": "synthetic_backend", "checksum": checksum(rows)},
        "source_revision": {"revision_id": revision_id, "source_id": SOURCE_ID, "snapshot": "complete",
                            "recorded_at": recorded_at, "approval_ref": "baseline_import" if revision == "R0" else None},
        "objects": sorted(objects, key=by_id("object_id")),
        "tag_assignments": sorted(tags, key=by_id("object_id")),
        "assertions": sorted(assertions, key=by_id("assertion_id")),
        "drawings": sorted(drawings, key=by_id("artifact_id")),
        "appearances": sorted(appearances, key=by_id("appearance_id")),
    }


def main(argv: list[str]) -> int:
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if len(argv) == 2 and argv[0] == "database":
        with loader.connect() as conn:
            revision, rows = rows_from_database(conn)
        origin = "sqlserver:" + os.environ["LIONG_SQLSERVER"].split(",", 4)[4] + "/p3d"
        out = Path(argv[1])
    elif len(argv) == 3 and argv[0] == "snapshot":
        folder = Path(argv[1])
        revision, rows = rows_from_snapshot(folder)
        origin, out = f"snapshot:{folder.as_posix()}", Path(argv[2])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    records = extract(revision, rows, origin, captured_at)
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Extracted revision {revision['revision']}: {len(records['objects'])} objects, "
          f"{len(records['assertions'])} assertions, {len(records['appearances'])} appearances.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
