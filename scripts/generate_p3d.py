#!/usr/bin/env python3
"""Generate the Plant 3D-style backend files for a canonical world (DEC-019, DEC-035).

Each revision of the world becomes one complete snapshot (DEC-037): one JSON file per
p3d table, holding the rows the product would have saved. The generator also writes
the world's answer key, which maps the world's aliases to the snapshot's source-local
keys. The answer key goes to a separate folder and is never part of a snapshot.

Usage:
  generate_p3d.py            write fixtures/p3d-r0/ and fixtures/answer-keys/p3d-r0.json
  generate_p3d.py --check    fail if the committed files differ from a fresh generation

R0 is hand-authored and has no seed (DEC-016), so the output is a pure function of the
world file: keys, GUIDs, handles and times are all derived from it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from liong_facts import ON_SHEET, ROOT, Edge
from world import State, load, problems, state

GENERATOR_VERSION = "synthetic-v0.1"
WORLD = ROOT / "worlds" / "R0.yaml"
SCHEMA = ROOT / "schemas" / "plant3d-style.sql"
OUT = ROOT / "fixtures" / "p3d-r0"
ANSWER_KEY = ROOT / "fixtures" / "answer-keys" / "p3d-r0.json"

# The order revisions are generated in, and when each source revision was recorded
# (LIONG-006 "Revision and time rules"; DEC-045: the vendor records its own time).
# Rbad has no time in LIONG-006; DEC-050 places it at 12:00 on R0's day.
RECORDED_AT = {
    "R0": "2030-01-01T08:00:00",
    "R1": "2030-01-02T08:00:00",
    "R2": "2030-01-03T08:00:00",
    "Rbad": "2030-01-01T12:00:00",
}
CLASS_TABLE = {
    "equipment": "Equipment",
    "valve": "Valve",
    "instrument": "Instrument",
    "pipe_segment": "LineSegment",
}
TABLES = (
    "PlantObject", "Equipment", "Valve", "Instrument", "LineSegment", "Junction", "SheetConnector",
    "SegmentStart", "SegmentEnd", "ConnectorPair", "Ownership", "SheetConnectorLink",
    "Drawing", "DrawingAppearance", "WorkHistory",
)
# A fixed namespace, so every GUID is reproducible from the world and the alias.
NAMESPACE = uuid.UUID("5f0c8a2e-3b7d-4c1e-9a6f-2d8e4b1c7a30")


class GenerationError(Exception):
    """The world holds something this backend cannot store."""


def class_table(node: dict) -> str:
    """The p3d class table for a world node."""
    if node["class"] == "connection_point":
        return "SheetConnector" if "tag" in node else "Junction"
    return CLASS_TABLE[node["class"]]


def keys(world: dict) -> dict[str, int]:
    """Stable source-local keys (DEC-044): plant objects from 101, drawings from 901, in file order."""
    found, next_object, next_drawing = {}, 101, 901
    for alias, node in world["nodes"].items():
        if node["class"] == "drawing":
            found[alias], next_drawing = next_drawing, next_drawing + 1
        else:
            found[alias], next_object = next_object, next_object + 1
    return found


def guid(world: dict, *parts: object) -> str:
    return str(uuid.uuid5(NAMESPACE, "/".join([world["world"], *map(str, parts)]))).upper()


def tag_parts(table: str, tag: str) -> dict[str, str]:
    """A composed tag split into the class's subparts (DEC-049)."""
    pieces = tag.split("-")
    if table in ("Equipment", "Valve") and len(pieces) == 2:
        return {"TagType": pieces[0], "TagNumber": pieces[1]}
    if table == "Instrument" and len(pieces) == 2:
        return {"TagType": pieces[0], "LoopNumber": pieces[1]}
    if table == "LineSegment" and len(pieces) == 3:
        return {"LinePrefix": pieces[0], "LineNumber": pieces[1], "SegmentSuffix": pieces[2]}
    raise GenerationError(f"tag {tag} does not fit the {table} tag format")


def last_touched(world: dict, chain: list[str]) -> dict[str, str]:
    """For each alias, the last revision in `chain` that created or changed it."""
    touched = {alias: chain[0] for alias in world["nodes"]}
    for name in chain[1:]:
        for change in world["revisions"][name].get("changes", []):
            if "set_tag" in change:
                touched[change["set_tag"]["node"]] = name
    return touched


def ancestry(world: dict, revision: str) -> list[str]:
    chain, current = [], revision
    while current is not None:
        chain.append(current)
        current = world["revisions"][current]["base"]
    return list(reversed(chain))


def history(world: dict, chain: list[str], key: dict[str, int]) -> list[dict]:
    """One work-history row per change along the revision's ancestry (DEC-037)."""
    rows = []

    def add(revision: str, alias: str, kind: str, detail: str | None) -> None:
        drawing = world["nodes"][alias]["class"] == "drawing"
        rows.append({
            "HistoryId": len(rows) + 1,
            "ObjectId": None if drawing else key[alias],
            "DrawingId": key[alias] if drawing else None,
            "Revision": revision,
            "ChangeKind": kind,
            "Detail": detail,
            "RecordedAt": RECORDED_AT[revision],
        })

    for alias in world["nodes"]:
        add(chain[0], alias, "Created", None)
    for name in chain[1:]:
        for change in world["revisions"][name].get("changes", []):
            if "set_tag" in change:
                alias = change["set_tag"]["node"]
                add(name, alias, "Modified", f"Tag {world['nodes'][alias].get('tag')} -> {change['set_tag']['tag']}")
            elif "delete_node" in change:
                add(name, change["delete_node"], "Deleted", None)
            elif "delete_edge" in change:
                # A removed connection names no object as deleted; its detail uses keys, not aliases
                kind, source, target = change["delete_edge"]
                rows.append({
                    "HistoryId": len(rows) + 1, "ObjectId": None, "DrawingId": None, "Revision": name,
                    "ChangeKind": "Deleted", "Detail": f"{kind} {key[source]} -> {key[target]}",
                    "RecordedAt": RECORDED_AT[name],
                })
            else:
                raise GenerationError(f"revision {name} has a change this backend cannot record: {change}")
    return rows


def snapshot(world: dict, revision: str) -> dict[str, list[dict]]:
    """Every p3d row for one revision: the saved state plus its own history."""
    current: State = state(world, revision)
    key = keys(world)
    chain = ancestry(world, revision)
    touched = last_touched(world, chain)
    rows: dict[str, list[dict]] = {table: [] for table in TABLES}
    for alias, node in current.nodes.items():
        if node["class"] == "drawing":
            rows["Drawing"].append({"DrawingId": key[alias], "FileName": node["name"],
                                    "Revision": revision, "Status": "Approved"})
            continue
        table = class_table(node)
        rows["PlantObject"].append({
            "ObjectId": key[alias], "ObjectGuid": guid(world, "object", alias), "ClassName": table,
            "Revision": touched[alias], "Status": "Approved", "RowStamp": key[alias] * 1000 + chain.index(touched[alias]),
        })
        attributes = node.get("attributes", {})
        row: dict = {"ObjectId": key[alias]}
        if table == "SheetConnector":
            row |= {"Label": node["tag"], "Direction": "Out" if node["role"].startswith("outgoing") else "In"}
        elif table == "Junction":
            row |= {"Description": node.get("role")}
        else:
            row |= {"Tag": node.get("tag"), **(tag_parts(table, node["tag"]) if "tag" in node else {})}
            if table == "LineSegment":
                row["NominalSizeMm"] = attributes.get("nominal_diameter_mm")
            else:
                row["Description"] = node.get("role")
            if table == "Instrument":
                row["Unit"] = attributes.get("unit")
        rows[table].append(row)

    def relation(table: str, first: str, second: str, a: str, b: str) -> None:
        # Every alias keeps its key after deletion, so Rbad's rows to a deleted node
        # still name that node's key: the dangling reference the pipeline must reject.
        rows[table].append({"RowId": len(rows[table]) + 1, "RowGuid": guid(world, table, a, b),
                            first: key[a], second: key[b]})

    def is_class(alias: str, name: str) -> bool:
        return world["nodes"][alias]["class"] == name

    flows = {(e.source, e.target) for e in current.edges if e.kind == "FLOW"}
    cross = {(e.source, e.target) for e in current.edges if e.kind == "CROSS_SHEET_REFERENCE"}
    connectors = {a for a, n in world["nodes"].items() if n["class"] == "connection_point" and "tag" in n}
    for source, target in sorted(flows):
        if is_class(target, "pipe_segment"):
            relation("SegmentStart", "SegmentId", "ObjectId", target, source)
        elif is_class(source, "pipe_segment"):
            relation("SegmentEnd", "SegmentId", "ObjectId", source, target)
        elif source in connectors and target in connectors:
            if (source, target) not in cross:
                raise GenerationError(f"flow {source}->{target} joins two sheet connectors without a cross-sheet reference")
            relation("SheetConnectorLink", "OutConnector", "InConnector", source, target)
        else:
            relation("ConnectorPair", "Connector1", "Connector2", source, target)
    for source, target in sorted(cross - flows):
        raise GenerationError(f"cross-sheet reference {source}->{target} has no flow; this backend stores both as one row")
    for e in sorted(current.edges):
        if e.kind == "INSTRUMENT_PARENT":
            relation("Ownership", "OwnerId", "OwnedId", e.target, e.source)
    for alias, node in current.nodes.items():
        if "sheet" in node:
            rows["DrawingAppearance"].append({
                "RowId": len(rows["DrawingAppearance"]) + 1, "ObjectId": key[alias], "DrawingId": key[node["sheet"]],
                "DrawingHandle": format(0x2A0 + key[alias], "X"),
            })
    rows["WorkHistory"] = history(world, chain, key)
    return rows


def answer_key(world: dict) -> dict:
    """The world's aliases mapped to this backend's keys, with each revision's expected view."""
    key = keys(world)
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
    return {"world": world["world"], "backend": "p3d", "keys": key, "revisions": revisions}


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
        "backend": "p3d",
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
        extra = [p for folder in (OUT, ANSWER_KEY.parent) for p in folder.rglob("*") if p.is_file() and p not in files]
        for p in stale + extra:
            print(f"stale or extra: {p.relative_to(ROOT)}", file=sys.stderr)
        if stale or extra:
            print("Run: uv run python scripts/generate_p3d.py", file=sys.stderr)
            return 1
        print(f"Plant 3D-style fixtures match {WORLD.name}: {len(files)} files.")
        return 0
    for p, b in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    print(f"Wrote {len(files)} files under {OUT.relative_to(ROOT)} and {ANSWER_KEY.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
