#!/usr/bin/env python3
"""Generate the SmartPlant-style backend files for W-SP (DEC-019, DEC-035, DEC-081).

Each revision of the world becomes one complete snapshot (DEC-037): one JSON file per
sps data table, holding the rows the product would have saved. The generator also
writes the world's answer key, which maps the world's aliases to the snapshot's GUIDs.
The answer key goes to a separate folder and is never part of a snapshot.

Usage:
  generate_sps.py            write fixtures/sps-wsp/ and fixtures/answer-keys/sps-wsp.json
  generate_sps.py --check    fail if the committed files differ from a fresh generation

The snapshot stores W-SP the way DEC-081's patterns do, so it differs from the world
file in shape: each pipe run is one item drawn as line depictions, one per pipe
segment; vessels gain nozzle rows; LT-302 reaches TK-302 through a nozzle and a
process connection; the pipeline is a line group row that holds only line 301's key
values, and no run points to it. W-SP is hand-authored and has no
seed (DEC-016), so the output is a pure function of the world file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from liong_facts import ROOT
from world import State, load, problems, state

GENERATOR_VERSION = "synthetic-v0.1"
WORLD = ROOT / "worlds" / "W-SP.yaml"
SCHEMA = ROOT / "schemas" / "smartplant-style.sql"
OUT = ROOT / "fixtures" / "sps-wsp"
ANSWER_KEY = ROOT / "fixtures" / "answer-keys" / "sps-wsp.json"

# When the source recorded each revision (DEC-045). LIONG-006 gives W-SP no time;
# DEC-083 places W0 at 08:00 on 2030-02-01, after R0's revisions.
RECORDED_AT = {"W0": "2030-02-01T08:00:00"}
# Runs drawn against their flow, so end 2 is upstream (DEC-083). The rest are drawn
# with it. Drawing one each way makes extraction read the run's flow sense.
DRAWN_AGAINST_FLOW = {"B"}
TABLES = (
    "DesignItem", "Vessel", "Instrument", "PipeRun", "LineGroup", "PipingFitting", "Nozzle", "ProcessConnection", "SheetLink",
    "Depiction", "LineDepiction", "LabelDepiction", "InlinePlacement", "PortPoint", "Sheet", "SheetRevision",
)
# Port points each owning class gets: a fitting has an inlet and an outlet.
PORT_POINTS = {"PipingFitting": 2, "Instrument": 1, "Nozzle": 1}
# A fixed namespace, so every GUID is reproducible from the world and its parts.
NAMESPACE = uuid.UUID("9b3e6f1c-27a4-4d8b-8c5e-0a1f7d2e6b94")


class GenerationError(Exception):
    """The world holds something this backend cannot store."""


def guid(world: dict, *parts: object) -> str:
    return str(uuid.uuid5(NAMESPACE, "/".join([world["world"], *map(str, parts)]))).upper()


def tag_parts(tag: str) -> dict[str, str | None]:
    """A vessel or instrument tag, such as TK-301 or LT-302, split into its parts (DEC-082)."""
    pieces = tag.split("-")
    if len(pieces) != 2:
        raise GenerationError(f"tag {tag} does not fit the Lead-Number tag format")
    return {"TagLead": pieces[0], "TagNumber": pieces[1], "TagTail": None}


class Snapshot:
    """The rows of one revision, built table by table."""

    def __init__(self, world: dict, revision: str):
        self.world, self.revision = world, revision
        self.current: State = state(world, revision)
        self.rows: dict[str, list[dict]] = {table: [] for table in TABLES}
        self.marks: dict[str, str] = {}       # item GUID -> its mark depiction GUID
        self.nozzles: dict[str, int] = {}     # vessel alias -> nozzles placed on it so far

    def g(self, *parts: object) -> str:
        return guid(self.world, *parts)

    def node(self, alias: str) -> dict:
        return self.current.nodes[alias]

    def sheet(self, alias: str) -> str:
        return self.g("sheet", self.node(alias)["sheet"])

    def item(self, item_guid: str, kind: str, row: dict) -> None:
        self.rows["DesignItem"].append({"ItemGuid": item_guid, "ItemKind": kind, "ItemState": "Active"})
        self.rows[kind].append({"ItemGuid": item_guid, **row})
        for number in range(1, PORT_POINTS.get(kind, 0) + 1):
            self.rows["PortPoint"].append({"PointGuid": self.g("point", item_guid, number),
                                           "OwnerItem": item_guid, "PointNo": number})

    def depiction(self, depiction_guid: str, item_guid: str | None, sheet_guid: str, kind: str) -> str:
        self.rows["Depiction"].append({"DepictionGuid": depiction_guid, "ItemGuid": item_guid,
                                       "SheetGuid": sheet_guid, "DepictionKind": kind})
        return depiction_guid

    def mark(self, item_guid: str, sheet_guid: str) -> str:
        self.marks[item_guid] = self.depiction(self.g("mark", item_guid), item_guid, sheet_guid, "Mark")
        return self.marks[item_guid]

    def line(self, depiction_guid: str, item_guid: str, sheet_guid: str, upstream: str | None,
             downstream: str | None, against_flow: bool) -> None:
        self.depiction(depiction_guid, item_guid, sheet_guid, "Line")
        ends = (downstream, upstream) if against_flow else (upstream, downstream)
        self.rows["LineDepiction"].append({"DepictionGuid": depiction_guid, "End1Mark": ends[0], "End2Mark": ends[1]})

    def nozzle(self, vessel: str, purpose: str) -> str:
        """A nozzle on `vessel` for one pipe end or one instrument; returns its mark (DEC-081 pattern 7)."""
        self.nozzles[vessel] = self.nozzles.get(vessel, 0) + 1
        item_guid = self.g("nozzle", vessel, purpose)
        self.item(item_guid, "Nozzle", {"ItemTag": f"N{self.nozzles[vessel]}", "ParentItem": self.g("item", vessel)})
        return self.mark(item_guid, self.sheet(vessel))


def runs(current: State) -> dict[str, list[str]]:
    """Each run's pipe segments, in the world file's order."""
    found: dict[str, list[str]] = {}
    for alias, node in current.nodes.items():
        if node["class"] == "pipe_segment":
            found.setdefault(node["attributes"]["run"], []).append(alias)
    return found


def run_row(current: State, name: str, segments: list[str]) -> dict:
    """A run's PipeRun columns, from its segments, which must agree on line number and size."""
    lines = {(current.nodes[s]["tag"].rsplit("-", 1)[0], current.nodes[s]["attributes"]["line_number"]) for s in segments}
    sizes = {current.nodes[s]["attributes"]["nominal_diameter_mm"] for s in segments}
    if len(lines) != 1 or len(sizes) != 1:
        raise GenerationError(f"run {name}'s segments disagree on line number or size")
    (line_tag, number), = lines
    lead, tag_number = line_tag.split("-")
    if tag_number != number:
        raise GenerationError(f"run {name}'s tags say line {tag_number} but its attributes say {number}")
    return {"ItemTag": line_tag, "TagLead": lead, "TagNumber": number, "TagTail": None,
            "NominalSizeMm": sizes.pop(), "FlowSense": "End2Upstream" if name in DRAWN_AGAINST_FLOW else "End1Upstream"}


def snapshot(world: dict, revision: str) -> dict[str, list[dict]]:
    """Every sps row for one revision."""
    s = Snapshot(world, revision)
    current, g = s.current, s.g
    flows = {(e.source, e.target) for e in current.edges if e.kind == "FLOW"}
    cross = {(e.source, e.target) for e in current.edges if e.kind == "CROSS_SHEET_REFERENCE"}
    parents = {(e.source, e.target) for e in current.edges if e.kind == "INSTRUMENT_PARENT"}
    if set(world["edges"]) - {"FLOW", "CROSS_SHEET_REFERENCE", "INSTRUMENT_PARENT"}:
        raise GenerationError("the world has an edge kind this backend cannot store")

    for alias, node in current.nodes.items():
        if node["class"] == "drawing":
            sheet = g("sheet", alias)
            s.rows["Sheet"].append({"SheetGuid": sheet, "SheetNo": node["name"]})
            s.rows["SheetRevision"].append({
                "RevisionGuid": g("revision", alias, revision), "SheetGuid": sheet, "MajorRev": revision,
                "MinorRev": "0", "RevisedOn": RECORDED_AT[revision], "ApprovalState": "Approved"})

    # Items with a mark: vessels, fittings, instruments and sheet links.
    for alias, node in current.nodes.items():
        item = g("item", alias)
        if node["class"] == "equipment":
            s.item(item, "Vessel", {"ItemTag": node["tag"], **tag_parts(node["tag"]), "Description": node.get("role")})
        elif node["class"] == "valve":
            s.item(item, "PipingFitting", {"ItemTag": node["tag"], "Description": node.get("role")})
        elif node["class"] == "instrument":
            s.item(item, "Instrument", {"ItemTag": node["tag"], **tag_parts(node["tag"]),
                                        "Unit": node.get("attributes", {}).get("unit"), "Description": node.get("role")})
        elif node["class"] == "connection_point" and "tag" in node:
            mates = [t for src, t in cross if src == alias] + [src for src, t in cross if t == alias]
            if len(mates) != 1:
                raise GenerationError(f"sheet connector {alias} needs exactly one cross-sheet mate")
            outgoing = node["role"].startswith("outgoing")
            pair = (alias, mates[0]) if outgoing else (mates[0], alias)
            if pair not in flows:
                raise GenerationError(f"cross-sheet reference {pair[0]}->{pair[1]} has no flow; "
                                      "this backend stores the pair as continuation only")
            s.item(item, "SheetLink", {"LinkLabel": node["tag"], "LinkSense": "To" if outgoing else "From",
                                       "MateItem": g("item", mates[0]), "MateSheet": s.sheet(mates[0])})
        elif node["class"] in ("pipe_segment", "drawing"):
            continue
        else:
            raise GenerationError(f"{alias} is a {node['class']}, which this backend cannot store")
        s.mark(item, s.sheet(alias))

    # Runs, drawn as one line depiction per segment, each labelled with the segment's tag.
    run_of = {}
    for name, segments in runs(current).items():
        run = g("run", name)
        row = run_row(current, name, segments)
        s.item(run, "PipeRun", row)
        # One line group per distinct line key; it holds the key values only (DEC-083)
        group = {"GroupGuid": g("group", row["ItemTag"]), "TagLead": row["TagLead"], "TagNumber": row["TagNumber"]}
        if group not in s.rows["LineGroup"]:
            s.rows["LineGroup"].append(group)
        for segment in segments:
            run_of[segment] = name
            ends = []
            for incoming in (True, False):
                found = [a if incoming else b for a, b in flows if (b if incoming else a) == segment]
                if len(found) != 1:
                    raise GenerationError(f"segment {segment} needs exactly one {'upstream' if incoming else 'downstream'} item")
                other = found[0]
                if s.node(other)["class"] == "equipment":
                    ends.append(s.nozzle(other, segment))
                elif s.node(other)["class"] in ("valve", "connection_point"):
                    ends.append(s.marks[g("item", other)])
                else:
                    raise GenerationError(f"segment {segment} meets {other} directly; this backend joins runs at items")
            line = g("line", segment)
            s.line(line, run, s.sheet(segment), ends[0], ends[1], name in DRAWN_AGAINST_FLOW)
            label = s.depiction(g("label", segment), None, s.sheet(segment), "Label")
            s.rows["LabelDepiction"].append({"DepictionGuid": label, "LabelledDepiction": line,
                                             "LabelText": s.node(segment)["tag"]})

    # Every flow must be a segment end or a sheet-link pair.
    for a, b in sorted(flows):
        if a not in run_of and b not in run_of and (a, b) not in cross:
            raise GenerationError(f"flow {a}->{b} touches no pipe segment and is not a sheet-link pair")

    # Inline placement: a fitting sits on the run whose segments it joins (DEC-081 pattern 3).
    for alias, node in current.nodes.items():
        if node["class"] == "valve":
            joined = {run_of.get(a) for a, b in flows if b == alias} | {run_of.get(b) for a, b in flows if a == alias}
            if len(joined) != 1 or None in joined:
                raise GenerationError(f"fitting {alias} does not sit inside one run")
            s.rows["InlinePlacement"].append({"PlacementGuid": g("placement", alias), "ItemGuid": g("item", alias),
                                              "RunGuid": g("run", joined.pop())})

    # An instrument on a vessel: a nozzle on the vessel and a process connection drawn
    # from the instrument's mark to the nozzle's mark (DEC-081 pattern 7).
    for instrument, vessel in sorted(parents):
        if s.node(vessel)["class"] != "equipment":
            raise GenerationError(f"{instrument}'s parent {vessel} is not a vessel")
        nozzle_mark = s.nozzle(vessel, instrument)
        connection = g("process", instrument)
        s.item(connection, "ProcessConnection", {"Description": f"process connection for {s.node(instrument)['tag']}"})
        s.line(g("line", "process", instrument), connection, s.sheet(instrument),
               s.marks[g("item", instrument)], nozzle_mark, against_flow=False)
    return s.rows


def keys(world: dict) -> dict[str, str]:
    """Each alias's GUID in this backend: the item, a segment's line depiction, or a drawing's sheet."""
    found = {}
    for alias, node in world["nodes"].items():
        kind = {"drawing": "sheet", "pipe_segment": "line"}.get(node["class"], "item")
        found[alias] = guid(world, kind, alias)
    return found


def answer_key(world: dict) -> dict:
    """The world's aliases mapped to this backend's GUIDs, with each revision's expected view."""
    revisions = {}
    for name, revision in world["revisions"].items():
        current = state(world, name)
        found = problems(current)
        revisions[name] = {
            "expected": "rejected" if revision.get("expected") == "rejected" else "accepted",
            "reason": found[0] if found else None,
            "nodes": sorted(current.nodes),
            "edges": sorted([e.kind, e.source, e.target] for e in current.all_edges()),
        }
    return {"world": world["world"], "backend": "sps", "keys": keys(world), "revisions": revisions}


def dump(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def outputs(world_path: Path = WORLD) -> dict[Path, bytes]:
    """Every file the generator writes, keyed by path, with the manifest last."""
    world = load(world_path)
    files: dict[Path, bytes] = {}
    for name in world["revisions"]:
        for table, rows in snapshot(world, name).items():
            files[OUT / name / f"{table}.json"] = dump(rows)
    files[ANSWER_KEY] = dump(answer_key(world))
    manifest = {
        "generator": GENERATOR_VERSION,
        "world": world["world"],
        "backend": "sps",
        "seed": None,
        "inputs": {
            str(p.relative_to(ROOT)): sha256(p.read_bytes())
            for p in (world_path, SCHEMA, Path(__file__).resolve(), ROOT / "uv.lock")
        },
        "revisions": {name: {"base": r["base"], "moc": r["moc"], "recorded_at": RECORDED_AT[name]}
                      for name, r in world["revisions"].items()},
        "files": {str(p.relative_to(OUT)): sha256(b) for p, b in sorted(files.items()) if p.is_relative_to(OUT)},
    }
    files[OUT / "manifest.json"] = dump(manifest)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the committed files are stale")
    args = parser.parse_args(argv)
    try:
        files = outputs()
    except GenerationError as error:
        print(f"Cannot generate: {error}", file=sys.stderr)
        return 1
    if args.check:
        stale = [p for p, b in files.items() if not p.is_file() or p.read_bytes() != b]
        extra = [p for p in OUT.rglob("*") if p.is_file() and p not in files]
        for p in stale + extra:
            print(f"stale or extra: {p.relative_to(ROOT)}", file=sys.stderr)
        if stale or extra:
            print("Run: uv run python scripts/generate_sps.py", file=sys.stderr)
            return 1
        print(f"SmartPlant-style fixtures match {WORLD.name}: {len(files)} files.")
        return 0
    for p, b in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    print(f"Wrote {len(files)} files under {OUT.relative_to(ROOT)} and {ANSWER_KEY.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
