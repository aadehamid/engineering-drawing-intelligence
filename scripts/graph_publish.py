#!/usr/bin/env python3
"""Publish one immutable graph snapshot to Neo4j, and query its cross-sheet connections.

Usage (LIONG_NEO4J is "uri,user,password", such as "bolt://localhost:7687,neo4j,secret"):
  graph_publish.py publish GRAPH_FILE RECEIPT_FILE   publish a graph and write its receipt
  graph_publish.py query SNAPSHOT_ID [LABEL]         print the snapshot's cross-sheet connections

A graph file holds "source_revision", "nodes" and "edges". A node has an "id", a "kind"
and optional "tag", "name" and "evidence"; an edge has a "kind" (FLOW, ON_SHEET,
INSTRUMENT_PARENT or CROSS_SHEET_REFERENCE), a "source", a "target" and optional
"evidence". Evidence is a list of objects naming where a fact came from.

The snapshot ID is the SHA-256 of the graph's content, so a snapshot cannot change
once published: publishing the same graph again changes nothing, and a stored
snapshot whose content differs is refused. A publish is one transaction, so a
reader sees the whole snapshot or none of it (DEC-056, DEC-057, DEC-058).
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

from neo4j import GraphDatabase

EDGE_KINDS = ("FLOW", "ON_SHEET", "INSTRUMENT_PARENT", "CROSS_SHEET_REFERENCE")
NODE_FIELDS = {"id", "kind", "tag", "name", "evidence"}
EDGE_FIELDS = {"kind", "source", "target", "evidence"}
CROSS_SHEET_QUERY = """
MATCH (a:Entity {snapshot_id: $snapshot_id})-[r:CROSS_SHEET_REFERENCE]->(b:Entity {snapshot_id: $snapshot_id})
WHERE $label IS NULL OR a.name = $label OR b.name = $label
OPTIONAL MATCH (a)-[:ON_SHEET]->(sheet_a:Entity)
OPTIONAL MATCH (b)-[:ON_SHEET]->(sheet_b:Entity)
RETURN a.id AS from_id, a.name AS from_label, sheet_a.name AS from_sheet, a.evidence AS from_evidence,
       b.id AS to_id, b.name AS to_label, sheet_b.name AS to_sheet, b.evidence AS to_evidence,
       r.evidence AS evidence
ORDER BY from_id, to_id
"""


class PublishError(Exception):
    """The graph is malformed, or its snapshot already exists with other content."""


def canonical(graph: dict) -> dict:
    """The graph's content in a fixed order, after checking its shape."""
    nodes, edges = graph.get("nodes"), graph.get("edges")
    if not isinstance(graph.get("source_revision"), str) or not isinstance(nodes, list) or not isinstance(edges, list):
        raise PublishError("a graph needs a source_revision, a list of nodes and a list of edges")
    ids = set()
    for node in nodes:
        if set(node) - NODE_FIELDS or not isinstance(node.get("id"), str) or not isinstance(node.get("kind"), str):
            raise PublishError(f"malformed node: {node}")
        if node["id"] in ids:
            raise PublishError(f"duplicate node {node['id']}")
        ids.add(node["id"])
    for edge in edges:
        if set(edge) - EDGE_FIELDS or edge.get("kind") not in EDGE_KINDS:
            raise PublishError(f"malformed edge: {edge}")
        missing = [end for end in (edge.get("source"), edge.get("target")) if end not in ids]
        if missing:
            raise PublishError(f"{edge['kind']} {edge.get('source')}->{edge.get('target')} has missing endpoint {missing[0]}")
    # An absent evidence list and an empty one mean the same; a null tag or name means absent.
    fill = lambda item: {k: v for k, v in item.items() if v is not None} | {"evidence": item.get("evidence") or []}  # noqa: E731
    order = lambda item: json.dumps(item, sort_keys=True)  # noqa: E731
    return {"source_revision": graph["source_revision"],
            "nodes": sorted(map(fill, nodes), key=order), "edges": sorted(map(fill, edges), key=order)}


def snapshot_id(graph: dict) -> str:
    return hashlib.sha256(json.dumps(canonical(graph), sort_keys=True).encode("utf-8")).hexdigest()


def connect(setting: str | None = None):
    uri, user, password = (setting or os.environ.get("LIONG_NEO4J", "")).split(",", 2)
    return GraphDatabase.driver(uri, auth=(user, password))


def ensure_constraints(driver) -> None:
    driver.execute_query("CREATE CONSTRAINT entity_uid IF NOT EXISTS FOR (n:Entity) REQUIRE n.uid IS UNIQUE")
    driver.execute_query("CREATE CONSTRAINT snapshot_id IF NOT EXISTS FOR (s:Snapshot) REQUIRE s.snapshot_id IS UNIQUE")


def _write(tx, graph: dict, sid: str, published_at: str, fail_after_nodes: bool) -> str:
    if tx.run("MATCH (s:Snapshot {snapshot_id: $sid}) RETURN s", sid=sid).single() is not None:
        stored = read_back(tx, sid)
        if snapshot_id(stored) != sid:
            raise PublishError(f"snapshot {sid} exists with other content")
        return "unchanged"
    tx.run("""
        UNWIND $nodes AS n
        CREATE (:Entity {uid: $sid + '/' + n.id, snapshot_id: $sid, id: n.id, kind: n.kind,
                         tag: n.tag, name: n.name, evidence: n.evidence})""",
           sid=sid, nodes=[{"tag": None, "name": None, **n, "evidence": json.dumps(n["evidence"], sort_keys=True)}
                     for n in graph["nodes"]])
    if fail_after_nodes:
        raise RuntimeError("injected failure after the nodes were written")
    for kind in EDGE_KINDS:  # a relationship type cannot be a parameter, so each kind has its own statement
        edges = [{**e, "evidence": json.dumps(e["evidence"], sort_keys=True)}
                 for e in graph["edges"] if e["kind"] == kind]
        tx.run(f"""
            UNWIND $edges AS e
            MATCH (a:Entity {{uid: $sid + '/' + e.source}}), (b:Entity {{uid: $sid + '/' + e.target}})
            CREATE (a)-[:{kind} {{snapshot_id: $sid, evidence: e.evidence}}]->(b)""", sid=sid, edges=edges)
    tx.run("""CREATE (:Snapshot {snapshot_id: $sid, source_revision: $rev,
                                 published_at: $at, node_count: $nodes, edge_count: $edges})""",
           sid=sid, rev=graph["source_revision"], at=published_at, nodes=len(graph["nodes"]), edges=len(graph["edges"]))
    return "published"


def publish(driver, graph: dict, published_at: str, fail_after_nodes: bool = False) -> dict:
    """Publish the graph in one transaction and return its receipt.

    `fail_after_nodes` lets a test interrupt the transaction after the nodes are written.
    """
    graph = canonical(graph)
    sid = snapshot_id(graph)
    ensure_constraints(driver)
    with driver.session() as session:
        outcome = session.execute_write(_write, graph, sid, published_at, fail_after_nodes)
        stored = session.run("MATCH (s:Snapshot {snapshot_id: $sid}) RETURN s", sid=sid).single()["s"]
    return {"publication_id": sid, "snapshot_id": sid, "outcome": outcome,
            "source_revision": stored["source_revision"], "published_at": stored["published_at"],
            "node_count": stored["node_count"], "edge_count": stored["edge_count"]}


def read_back(runner, sid: str) -> dict:
    """The snapshot as stored, in the graph file's shape. `runner` is a session or transaction."""
    revision = runner.run("MATCH (s:Snapshot {snapshot_id: $sid}) RETURN s.source_revision AS r", sid=sid).single()
    nodes = runner.run(
        "MATCH (n:Entity {snapshot_id: $sid}) RETURN n.id AS id, n.kind AS kind, n.tag AS tag, "
        "n.name AS name, n.evidence AS evidence", sid=sid).data()
    edges = runner.run(
        "MATCH (a:Entity {snapshot_id: $sid})-[r {snapshot_id: $sid}]->(b:Entity) "
        "RETURN type(r) AS kind, a.id AS source, b.id AS target, r.evidence AS evidence", sid=sid).data()
    clean = lambda record: {k: (json.loads(v) if k == "evidence" else v)  # noqa: E731
                            for k, v in record.items() if v is not None}
    return {"source_revision": revision["r"] if revision else None,
            "nodes": [clean(r) for r in nodes], "edges": [clean(r) for r in edges]}


def cross_sheet(driver, sid: str, label: str | None = None) -> list[dict]:
    """Each cross-sheet connection in the snapshot, with both ends' sheets and the evidence."""
    records, _, _ = driver.execute_query(CROSS_SHEET_QUERY, snapshot_id=sid, label=label)
    rows = []
    for record in records:
        row = record.data()
        for field in ("from_evidence", "to_evidence", "evidence"):
            row[field] = json.loads(row[field])
        rows.append(row)
    return rows


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "publish":
        graph = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        with connect() as driver:
            receipt = publish(driver, graph, datetime.now(timezone.utc).isoformat(timespec="seconds"))
        Path(argv[2]).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"{receipt['outcome']}: snapshot {receipt['snapshot_id']}, "
              f"{receipt['node_count']} nodes, {receipt['edge_count']} edges")
        return 0
    if len(argv) in (2, 3) and argv[0] == "query":
        with connect() as driver:
            print(json.dumps(cross_sheet(driver, argv[1], argv[2] if len(argv) == 3 else None), indent=2))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
