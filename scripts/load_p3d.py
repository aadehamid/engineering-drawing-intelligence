#!/usr/bin/env python3
"""Apply a Plant 3D-style backend snapshot to SQL Server (DEC-019, DEC-047).

Usage (LIONG_SQLSERVER is "host,port,user,password,database"):
  load_p3d.py create                 create schemas p3d and outbox in an empty database
  load_p3d.py load SNAPSHOT_FOLDER   load one revision, such as fixtures/p3d-r0/R1

A load first checks every file against the manifest, then, in one transaction,
replaces the p3d rows with the snapshot's rows and adds the revision's pending event
to outbox.PendingEvent. A snapshot loads only on top of its base revision, so a
backend holds one line of revisions, as a saved project database does. Loading the
revision already loaded, with the same files, changes nothing.
"""
from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

import pytds

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = (ROOT / "schemas" / "plant3d-style.sql", ROOT / "schemas" / "outbox.sql")
# The tables a snapshot fills; the class definitions are part of the schema.
DATA_TABLES = (
    "PlantObject", "Equipment", "Valve", "Instrument", "LineSegment", "Junction", "SheetConnector",
    "SegmentStart", "SegmentEnd", "ConnectorPair", "Ownership", "SheetConnectorLink",
    "Drawing", "DrawingAppearance", "WorkHistory",
)
EVENT_NAMESPACE = uuid.UUID("0d6e1b4a-8f2c-4e57-b9a3-61c27f0e5d48")


class LoadError(Exception):
    """The snapshot cannot be loaded: a bad file, a wrong base, or a conflicting reload."""


def batches(text: str) -> list[str]:
    """The batches a SQL Server client sends: the text between lines that hold only GO."""
    out, current = [], []
    for line in text.splitlines():
        if line.strip().upper() == "GO":
            out.append("\n".join(current))
            current = []
        else:
            current.append(line)
    out.append("\n".join(current))
    return [b for b in out if b.strip()]


def connect(setting: str | None = None, autocommit: bool = False) -> pytds.Connection:
    host, port, user, password, database = (setting or os.environ["LIONG_SQLSERVER"]).split(",", 4)
    return pytds.connect(dsn=host, port=int(port), user=user, password=password,
                         database=database, autocommit=autocommit)


def create(conn: pytds.Connection) -> None:
    cursor = conn.cursor()
    for path in SCHEMAS:
        for batch in batches(path.read_text(encoding="utf-8")):
            cursor.execute(batch)
    conn.commit()


def read_snapshot(folder: Path) -> tuple[dict, str, dict[str, list[dict]]]:
    """(revision record, payload digest, rows) for one snapshot, after checking every file's hash."""
    manifest = json.loads((folder.parent / "manifest.json").read_text(encoding="utf-8"))
    revision = folder.name
    if revision not in manifest["revisions"]:
        raise LoadError(f"the manifest has no revision {revision}")
    rows, digests = {}, []
    for table in DATA_TABLES:
        name = f"{revision}/{table}.json"
        data = (folder / f"{table}.json").read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if manifest["files"].get(name) != digest:
            raise LoadError(f"{name} does not match the manifest; nothing was loaded")
        rows[table] = json.loads(data)
        digests.append(f"{name} {digest}")
    record = manifest["revisions"][revision] | {
        "world": manifest["world"], "backend": manifest["backend"], "revision": revision}
    payload = hashlib.sha256("\n".join(digests).encode("utf-8")).hexdigest()
    return record, payload, rows


def current(cursor, backend: str, world: str) -> tuple[str, str] | None:
    """(revision, payload digest) of the last revision loaded, or None for an empty backend."""
    cursor.execute(
        "SELECT TOP 1 Revision, PayloadSha256 FROM outbox.PendingEvent "
        "WHERE Backend = %s AND World = %s ORDER BY LoadSequence DESC", (backend, world))
    row = cursor.fetchone()
    return (row[0], row[1]) if row else None


def load(conn: pytds.Connection, folder: Path, before_commit: Callable[[], None] | None = None) -> str:
    """Load one snapshot in one transaction. Returns 'loaded' or 'unchanged'.

    `before_commit` lets a test interrupt the load after every write and before the
    commit, the first interruption point in LIONG-006's recovery table.
    """
    record, payload, rows = read_snapshot(folder)
    cursor = conn.cursor()
    loaded = current(cursor, record["backend"], record["world"])
    cursor.execute("SELECT PayloadSha256 FROM outbox.PendingEvent WHERE Backend = %s AND World = %s AND Revision = %s",
                   (record["backend"], record["world"], record["revision"]))
    earlier = cursor.fetchone()
    if earlier:
        conn.rollback()
        if earlier[0] == payload:
            return "unchanged"
        raise LoadError(f"revision {record['revision']} was already loaded with different files")
    if (loaded[0] if loaded else None) != record["base"]:
        conn.rollback()
        raise LoadError(f"revision {record['revision']} has base {record['base']}, "
                        f"but the backend holds {loaded[0] if loaded else 'nothing'}")
    try:
        for table in reversed(DATA_TABLES):
            cursor.execute(f"DELETE FROM p3d.{table}")
        for table in DATA_TABLES:
            for row in rows[table]:
                columns = list(row)
                cursor.execute(
                    f"INSERT INTO p3d.{table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
                    tuple(row[c] for c in columns))
        event = uuid.uuid5(EVENT_NAMESPACE, f"{record['backend']}/{record['world']}/{record['revision']}/{payload}")
        cursor.execute(
            "INSERT INTO outbox.PendingEvent (EventId, Backend, World, Revision, PayloadSha256, RecordedAt) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (str(event), record["backend"], record["world"], record["revision"], payload, record["recorded_at"]))
        if before_commit:
            before_commit()
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return "loaded"


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("create", "load") or (argv[0] == "load" and len(argv) != 2):
        print(__doc__, file=sys.stderr)
        return 2
    conn = connect()
    try:
        if argv[0] == "create":
            create(conn)
            print("Created schemas p3d and outbox.")
        else:
            print(f"{argv[1]}: {load(conn, Path(argv[1]))}")
    except LoadError as error:
        print(f"Cannot load: {error}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
