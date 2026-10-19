#!/usr/bin/env python3
"""Apply a SmartPlant-style backend snapshot to SQL Server (DEC-019, DEC-047, DEC-084).

Usage (LIONG_SQLSERVER is "host,port,user,password,database"):
  load_sps.py create                 create schema sps, and schema outbox if it is missing
  load_sps.py load SNAPSHOT_FOLDER   load one revision, such as fixtures/sps-wsp/W0

The load works as scripts/load_p3d.py's does, through the same code: every file is
checked against the manifest first, then one transaction replaces the sps rows with
the snapshot's and adds the revision's event to outbox.PendingEvent. Both backends
share the one outbox in the same database (DEC-028, DEC-047).
"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys

import load_p3d as shared
from load_p3d import LoadError, connect  # noqa: F401  (part of this module's interface)

BACKEND = "sps"
SCHEMAS = (shared.ROOT / "schemas" / "smartplant-style.sql", shared.ROOT / "schemas" / "outbox.sql")
# The tables a snapshot fills, with their columns as schemas/smartplant-style.sql creates
# them. A row's keys must be exactly these: column names never come from a snapshot file.
COLUMNS = {
    "DesignItem": ("ItemGuid", "ItemKind", "ItemState"),
    "Vessel": ("ItemGuid", "ItemTag", "TagLead", "TagNumber", "TagTail", "Description"),
    "Instrument": ("ItemGuid", "ItemTag", "TagLead", "TagNumber", "TagTail", "Unit", "Description"),
    "PipeRun": ("ItemGuid", "ItemTag", "TagLead", "TagNumber", "TagTail", "NominalSizeMm", "FlowSense"),
    "LineGroup": ("GroupGuid", "TagLead", "TagNumber"),
    "PipingFitting": ("ItemGuid", "ItemTag", "Description"),
    "Nozzle": ("ItemGuid", "ItemTag", "ParentItem"),
    "ProcessConnection": ("ItemGuid", "Description"),
    "SheetLink": ("ItemGuid", "LinkLabel", "LinkSense", "MateItem", "MateSheet"),
    "Depiction": ("DepictionGuid", "ItemGuid", "SheetGuid", "DepictionKind"),
    "LineDepiction": ("DepictionGuid", "End1Mark", "End2Mark"),
    "LabelDepiction": ("DepictionGuid", "LabelledDepiction", "LabelText"),
    "InlinePlacement": ("PlacementGuid", "ItemGuid", "RunGuid"),
    "PortPoint": ("PointGuid", "OwnerItem", "PointNo"),
    "Sheet": ("SheetGuid", "SheetNo"),
    "SheetRevision": ("RevisionGuid", "SheetGuid", "MajorRev", "MinorRev", "RevisedOn", "ApprovalState"),
}


def create(conn) -> list[str]:
    return shared.create(conn, SCHEMAS)


def read_snapshot(folder: Path) -> tuple[dict, str, dict[str, list[dict]]]:
    return shared.read_snapshot(folder, BACKEND, COLUMNS)


def load(conn, folder: Path, before_commit: Callable[[], None] | None = None) -> str:
    return shared.load(conn, folder, before_commit, BACKEND, COLUMNS)


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("create", "load") or (argv[0] == "load" and len(argv) != 2):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        conn = connect()
    except LoadError as error:
        print(f"Cannot load: {error}", file=sys.stderr)
        return 1
    try:
        if argv[0] == "create":
            print(shared.created_message(create(conn)))
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
