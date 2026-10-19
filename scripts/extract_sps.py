#!/usr/bin/env python3
"""Extract source records from the SmartPlant-style backend (MILESTONE-001b step 2).

Usage:
  extract_sps.py database OUT_FILE          read the backend LIONG_SQLSERVER names
  extract_sps.py snapshot FOLDER OUT_FILE   read a snapshot folder, such as fixtures/sps-wsp/W0

Both read the same sps tables and write the same records, in the shapes
scripts/extract_p3d.py writes (DEC-075): a SourceManifest, a SourceRevision, and the
EngineeringObject, TagAssignment, EngineeringAssertion and DrawingAppearance records.

The SmartPlant-style backend stores W-SP in a different shape from the graph
(DEC-081), so extraction rebuilds what the rows imply, as DEC-085 sets out:

- Each line depiction of a pipe run is one pipe segment. Its tag is the label
  placed on it.
- A segment's flow runs from the end its run's flow sense names as upstream. Each end
  becomes `starts_at` or `ends_at`, the predicates extract_p3d.py uses.
- An active nozzle is collapsed into its parent vessel: a segment ending at a nozzle
  ends at the vessel, and an instrument whose process connection reaches a vessel's
  nozzle is `owned_by` that vessel. A deleted nozzle is not collapsed: the fact names
  the nozzle, which is no object, so validation rejects it.
- A sheet-link pair whose two sides name each other, and each other's sheets, becomes
  `continues_to` from the "To" side to the "From" side. Sides that disagree stop
  extraction.
- A run belongs to the line group whose key values its line prefix and number
  match; a run with either part NULL belongs to none. No run stores a key to its
  group, so membership is found only by matching. Each segment of a member run gets
  a `pipeline` assertion.

Rebuilt facts have evidence_status "derived"; facts a row states directly have
"source_stated". Every record names the rows it came from. Extraction reads only the
backend and never opens an answer key.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

import extract_p3d
import load_sps as loader

SOURCE_ID = "sps"
WORLD = "W-SP"  # the synthetic world this backend holds (LIONG-006)
BASELINE = "W0"
OBJECT_KIND = {"Vessel": "equipment", "PipingFitting": "valve", "Instrument": "instrument",
               "SheetLink": "sheet_connector"}
# Attribute columns of each class table, as (column, predicate). ItemTag becomes a TagAssignment.
ATTRIBUTES = {
    "Vessel": (("TagLead", "tag_lead"), ("TagNumber", "tag_number"), ("TagTail", "tag_tail"),
               ("Description", "description")),
    "Instrument": (("TagLead", "tag_lead"), ("TagNumber", "tag_number"), ("TagTail", "tag_tail"),
                   ("Unit", "unit"), ("Description", "description")),
    "PipingFitting": (("Description", "description"),),
    "SheetLink": (("LinkLabel", "label"), ("LinkSense", "link_sense")),
}
# What a pipe segment takes from its run's row.
RUN_ATTRIBUTES = (("TagLead", "line_prefix"), ("TagNumber", "line_number"), ("TagTail", "line_suffix"),
                  ("NominalSizeMm", "nominal_size_mm"))


class ExtractionError(Exception):
    """The rows contradict themselves in a way extraction cannot record as stated."""


def item_id(guid: str) -> str:
    return f"{SOURCE_ID}:item:{guid}"


def line_id(guid: str) -> str:
    return f"{SOURCE_ID}:line:{guid}"


def sheet_id(guid: str) -> str:
    return f"{SOURCE_ID}:sheet:{guid}"


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
        cursor.execute(f"SELECT {', '.join(columns)} FROM sps.{table}")  # columns come from COLUMNS only
        rows[table] = [dict(zip(columns, (extract_p3d.plain(v) for v in record))) for record in cursor.fetchall()]
    return {"revision": loaded[0], "recorded_at": extract_p3d.plain(loaded[1])}, rows


def rows_from_snapshot(folder: Path) -> tuple[dict, dict[str, list[dict]]]:
    """(revision, rows) of a snapshot folder, after checking every file against its manifest."""
    record, _, rows = loader.read_snapshot(folder)
    return {"revision": record["revision"], "recorded_at": record["recorded_at"]}, rows


class Rows:
    """The snapshot's rows indexed by key, with the lookups the derivations share."""

    def __init__(self, rows: dict[str, list[dict]]):
        self.rows = rows
        self.items = {r["ItemGuid"]: r for r in rows["DesignItem"]}
        self.by_class = {table: {r["ItemGuid"]: r for r in rows[table]} for table in loader.COLUMNS
                         if loader.COLUMNS[table][0] == "ItemGuid" and table != "DesignItem"}
        self.depictions = {r["DepictionGuid"]: r for r in rows["Depiction"]}
        # Neither a depiction's labels nor an item's marks are unique in the schema, so
        # both keep every row, sorted, and no lookup depends on row order
        self.labels: dict[str, list[dict]] = {}
        for label in sorted(rows["LabelDepiction"], key=lambda x: x["DepictionGuid"]):
            self.labels.setdefault(label["LabelledDepiction"], []).append(label)
        self.mark_sheets: dict[str, set[str]] = {}
        for depiction in rows["Depiction"]:
            if depiction["DepictionKind"] == "Mark" and depiction["ItemGuid"] is not None:
                self.mark_sheets.setdefault(depiction["ItemGuid"], set()).add(depiction["SheetGuid"])

    def active(self, guid: str, table: str) -> bool:
        item = self.items.get(guid)
        return item is not None and item["ItemState"] == "Active" and guid in self.by_class[table]

    def lines_of(self, table: str) -> list[tuple[dict, dict]]:
        """(LineDepiction row, owning item row) for every line of an active item of `table`."""
        return [(line, self.by_class[table][self.depictions[line["DepictionGuid"]]["ItemGuid"]])
                for line in self.rows["LineDepiction"]
                if line["DepictionGuid"] in self.depictions
                and self.active(self.depictions[line["DepictionGuid"]]["ItemGuid"] or "", table)]

    def end(self, guid: str | None) -> tuple[str | None, list[dict]]:
        """The object a line end's item reaches, and the rows passed on the way.

        Each end names a design item (DEC-081 pattern 2). An active nozzle collapses
        into its parent vessel. A deleted nozzle does not: the end names the nozzle
        itself, which is no object, for validation to reject. An item that is missing
        or deleted is kept as stated for the same reason.
        """
        if guid is None:
            return None, []
        if guid in self.by_class["Nozzle"]:
            return self.through_nozzle(guid), [{"table": "Nozzle", "ItemGuid": guid}]
        return item_id(guid), []

    def through_nozzle(self, guid: str) -> str:
        """The vessel an active nozzle belongs to, or the deleted nozzle itself."""
        if not self.active(guid, "Nozzle"):
            return item_id(guid)
        return item_id(self.by_class["Nozzle"][guid]["ParentItem"])


def extract(revision: dict, rows: dict[str, list[dict]], origin_uri: str, captured_at: str) -> dict:
    """The source records the rows state or imply, each pointing back to its rows."""
    recorded_at, revision = revision["recorded_at"], revision["revision"]
    revision_id = f"{SOURCE_ID}:revision:{revision}"
    r = Rows(rows)
    objects, tags, assertions, drawings, appearances = [], [], [], [], []

    def state(subject: str, predicate: str, value: object, locator: dict, status: str = "source_stated",
              assertion_id: str | None = None) -> None:
        assertions.append({
            "assertion_id": assertion_id or f"{subject}/{predicate}", "subject_id": subject, "predicate": predicate,
            "value_or_target": value, "source_locator": locator, "revision_id": revision_id,
            "evidence_status": status,
        })

    # Objects that are items: vessels, fittings, instruments and sheet links.
    for table, kind in OBJECT_KIND.items():
        for guid, row in r.by_class[table].items():
            if not r.active(guid, table):
                continue
            subject, locator = item_id(guid), {"table": table, "ItemGuid": guid}
            objects.append({"object_id": subject, "object_kind": kind, "source_object_key": guid,
                            "source_locator": {"table": "DesignItem", "ItemGuid": guid}})
            if row.get("ItemTag") is not None:
                tags.append({"object_id": subject, "namespace": SOURCE_ID, "tag_value": row["ItemTag"],
                             "revision_id": revision_id, "source_locator": locator})
            for column, predicate in ATTRIBUTES[table]:
                if row[column] is not None:
                    state(subject, predicate, row[column], locator)
    for placement in rows["InlinePlacement"]:
        if r.active(placement["ItemGuid"], "PipingFitting"):
            state(item_id(placement["ItemGuid"]), "run", item_id(placement["RunGuid"]),
                  {"table": "InlinePlacement", "PlacementGuid": placement["PlacementGuid"]})

    # Pipelines: each line group's members are the active runs whose line prefix and
    # number match its key values; nothing else links them (REF-TECH-022).
    pipeline_of: dict[str, tuple[str, dict]] = {}
    for group in rows["LineGroup"]:
        key = (group["TagLead"], group["TagNumber"])
        members = sorted(g for g, run in r.by_class["PipeRun"].items()
                         if r.active(g, "PipeRun") and None not in key and (run["TagLead"], run["TagNumber"]) == key)
        locator = {"table": "LineGroup", "GroupGuid": group["GroupGuid"],
                   "via": [{"table": "PipeRun", "ItemGuid": g} for g in members]}
        for guid in members:
            if guid in pipeline_of:
                raise ExtractionError(f"run {guid} matches more than one line group")
            pipeline_of[guid] = (f"{key[0]}-{key[1]}", locator)

    # Pipe segments: one per line depiction of a run, flowing by the run's flow sense.
    for line, run in r.lines_of("PipeRun"):
        guid = line["DepictionGuid"]
        subject, locator = line_id(guid), {"table": "LineDepiction", "DepictionGuid": guid}
        objects.append({"object_id": subject, "object_kind": "pipe_segment", "source_object_key": guid,
                        "source_locator": locator})
        labels = r.labels.get(guid, [])
        if len({label["LabelText"] for label in labels}) > 1:
            raise ExtractionError(f"line {guid} carries labels with different texts")
        if labels:
            tags.append({"object_id": subject, "namespace": SOURCE_ID, "tag_value": labels[0]["LabelText"],
                         "revision_id": revision_id,
                         "source_locator": {"table": "LabelDepiction", "DepictionGuid": labels[0]["DepictionGuid"]}})
        run_locator = {"table": "PipeRun", "ItemGuid": run["ItemGuid"]}
        for column, predicate in RUN_ATTRIBUTES:
            if run[column] is not None:
                state(subject, predicate, run[column], run_locator, "derived")
        state(subject, "run", item_id(run["ItemGuid"]), {"table": "Depiction", "DepictionGuid": guid})
        if run["ItemGuid"] in pipeline_of:
            name, group_locator = pipeline_of[run["ItemGuid"]]
            state(subject, "pipeline", name, group_locator, "derived")
        if run["FlowSense"] not in ("End1Upstream", "End2Upstream"):
            raise ExtractionError(f"run {run['ItemGuid']} has flow sense {run['FlowSense']!r}")
        upstream, downstream = ((line["End1Item"], line["End2Item"]) if run["FlowSense"] == "End1Upstream"
                                else (line["End2Item"], line["End1Item"]))
        for predicate, end_item in (("starts_at", upstream), ("ends_at", downstream)):
            target, via = r.end(end_item)
            if target is not None:
                state(subject, predicate, target, locator | {"via": [run_locator, *via]}, "derived",
                      f"LineDepiction/{guid}/{predicate}")

    # Instrument parents: a process connection from an instrument to a vessel's nozzle.
    for line, connection in r.lines_of("ProcessConnection"):
        ends = [line["End1Item"], line["End2Item"]]
        instruments = [g for g in ends if g in r.by_class["Instrument"]]
        nozzles = [g for g in ends if g in r.by_class["Nozzle"]]
        if len(instruments) != 1 or len(nozzles) != 1:
            raise ExtractionError(f"process connection {connection['ItemGuid']} does not join one instrument "
                                  "to one nozzle")
        nozzle = r.by_class["Nozzle"][nozzles[0]]
        state(item_id(instruments[0]), "owned_by", r.through_nozzle(nozzle["ItemGuid"]),
              {"table": "LineDepiction", "DepictionGuid": line["DepictionGuid"],
               "via": [{"table": "ProcessConnection", "ItemGuid": connection["ItemGuid"]},
                       {"table": "Nozzle", "ItemGuid": nozzle["ItemGuid"]}]},
              "derived", f"ProcessConnection/{connection['ItemGuid']}/owned_by")

    # Continuation: each side of a sheet-link pair names the other and the other's sheet.
    links = {g: row for g, row in r.by_class["SheetLink"].items() if r.active(g, "SheetLink")}
    # Every link that names a mate, and every link that a mate names, is checked from
    # both sides; only a link no row pairs with stays unpaired, with no continuation.
    named = {link["MateItem"]: guid for guid, link in links.items() if link["MateItem"] is not None}
    for guid, link in sorted(links.items()):
        if link["MateItem"] is None and guid not in named:
            continue
        mate = links.get(link["MateItem"] or named[guid])
        if (link["MateItem"] is None or mate is None or mate["MateItem"] != guid
                or {link["LinkSense"], mate["LinkSense"]} != {"To", "From"}
                or link["MateSheet"] not in r.mark_sheets.get(mate["ItemGuid"], set())
                or mate["MateSheet"] not in r.mark_sheets.get(guid, set())):
            raise ExtractionError(f"sheet links {guid} and {link['MateItem'] or named[guid]} do not name each "
                                  "other, with one To and one From side, and each other's sheets")
        if link["LinkSense"] != "To":
            continue
        state(item_id(guid), "continues_to", item_id(mate["ItemGuid"]),
              {"table": "SheetLink", "ItemGuid": guid, "via": [{"table": "SheetLink", "ItemGuid": mate["ItemGuid"]}]},
              "derived", f"SheetLink/{guid}/continues_to")

    # Drawings, and where each object appears on them.
    for sheet in rows["Sheet"]:
        # The latest revision is the one the source recorded last (DEC-045); revision
        # labels are text and do not sort as numbers. The source approval is that
        # revision's approver and approval date (DEC-039): with both it is "Approved",
        # without them it has no status. The numbers break a tie in recorded time.
        revisions = sorted((str(x["RevisedOn"]), x["MajorRev"], x["MinorRev"],
                            "Approved" if x["Approver"] is not None and x["ApprovedOn"] is not None else None)
                           for x in rows["SheetRevision"] if x["SheetGuid"] == sheet["SheetGuid"])
        latest = revisions[-1][1:] if revisions else (None, None, None)
        drawings.append({"artifact_id": sheet_id(sheet["SheetGuid"]), "name": sheet["SheetNo"],
                         "revision": f"{latest[0]}.{latest[1]}" if latest[0] else None, "status": latest[2],
                         "source_locator": {"table": "Sheet", "SheetGuid": sheet["SheetGuid"]}})
    object_ids = {o["object_id"] for o in objects}
    for depiction in rows["Depiction"]:
        guid = depiction["DepictionGuid"]
        subject = line_id(guid) if depiction["DepictionKind"] == "Line" else item_id(depiction["ItemGuid"] or "")
        if subject in object_ids and depiction["DepictionKind"] in ("Mark", "Line"):
            appearances.append({"appearance_id": f"{SOURCE_ID}:appearance:{guid}", "object_id": subject,
                                "artifact_id": sheet_id(depiction["SheetGuid"]), "region": guid,
                                "coordinate_system": "sps_depiction",
                                "source_locator": {"table": "Depiction", "DepictionGuid": guid}})

    by_id = lambda record_key: lambda record: str(record[record_key])  # noqa: E731
    return {
        "source_manifest": {"source_id": SOURCE_ID, "dataset_id": f"{SOURCE_ID}-{WORLD}", "origin_uri": origin_uri,
                            "captured_at": captured_at, "rights_ref": "synthetic, LIONG-006",
                            "provenance_kind": "synthetic_backend", "checksum": extract_p3d.checksum(rows)},
        "source_revision": {"revision_id": revision_id, "source_id": SOURCE_ID, "snapshot": "complete",
                            "recorded_at": recorded_at,
                            "approval_ref": "baseline_import" if revision == BASELINE else None},
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
        origin = "sqlserver:" + os.environ["LIONG_SQLSERVER"].split(",", 4)[4] + "/sps"
        out = Path(argv[1])
    elif len(argv) == 3 and argv[0] == "snapshot":
        folder = Path(argv[1])
        revision, rows = rows_from_snapshot(folder)
        origin, out = f"snapshot:{folder.as_posix()}", Path(argv[2])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        records = extract(revision, rows, origin, captured_at)
    except ExtractionError as error:
        print(f"Cannot extract: {error}", file=sys.stderr)
        return 1
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Extracted revision {revision['revision']}: {len(records['objects'])} objects, "
          f"{len(records['assertions'])} assertions, {len(records['appearances'])} appearances.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
