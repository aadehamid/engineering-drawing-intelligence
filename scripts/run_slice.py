#!/usr/bin/env python3
"""Run MILESTONE-001's structured slice for one revision, end to end (DEC-058, DEC-060).

Usage:
  run_slice.py REVISION OUT_FOLDER [--database] [--answer-key KEY_FILE]

Steps, each a plain Python call, in order:
  2. extract   source records from the snapshot folder fixtures/p3d-r0/REVISION, or with
               --database from the backend LIONG_SQLSERVER names (step 1, loading it, is
               scripts/load_p3d.py)
  3. generate  DEXPI 2.0.1 files and their sidecar, then validate them in four stages
  4. parse     the DEXPI back into the graph, and publish it to Neo4j if LIONG_NEO4J is set
  5. query     the published snapshot's cross-sheet connections
  6. compare   the result with the answer key, if --answer-key is given

OUT_FOLDER gets the run's records as JSON files: source-manifest.json,
exchange-manifest.json, graph-manifest.json and publication-receipt.json, plus the
source records, the DEXPI folder, graph.json, query.json and result.json. A revision the
generator or the validator rejects stops before publication, so nothing is published
for it. Steps 2 to 5 never read the answer key; only step 6, the scorer, does.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import compare_answer_key
import dexpi_generate
import dexpi_parse
import dexpi_validate
import extract_p3d

SNAPSHOTS = extract_p3d.loader.ROOT / "fixtures" / "p3d-r0"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(revision: str, out: Path, database: bool = False, now: str | None = None) -> dict:
    """Run steps 2 to 5 and return the result: accepted with its graph, or rejected with a reason."""
    now = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    out.mkdir(parents=True, exist_ok=True)

    if database:
        with extract_p3d.loader.connect() as conn:
            source_revision, rows = extract_p3d.rows_from_database(conn)
        origin = "sqlserver:" + os.environ["LIONG_SQLSERVER"].split(",", 4)[4] + "/p3d"
        if source_revision["revision"] != revision:
            raise SystemExit(f"the backend holds {source_revision['revision']}, not {revision}")
    else:
        source_revision, rows = extract_p3d.rows_from_snapshot(SNAPSHOTS / revision)
        origin = f"snapshot:fixtures/p3d-r0/{revision}"
    records = extract_p3d.extract(source_revision, rows, origin, now)
    dump(out / "source-records.json", records)
    dump(out / "source-manifest.json", records["source_manifest"] | {"source_revision": records["source_revision"]})

    exchange = out / "dexpi"
    try:
        files = dexpi_generate.generate(records)
    except dexpi_generate.SourceError as error:
        dump(out / "exchange-manifest.json", {"outcome": "rejected", "stage": "generate", "reason": str(error)})
        return finish(out, {"outcome": "rejected", "reason": str(error)})
    dexpi_generate.write(files, exchange)
    validation = dexpi_validate.validate(exchange)
    dump(out / "exchange-manifest.json", {
        "outcome": "accepted" if validation["failed"] is None and not validation["round_trip"] else "rejected",
        "standard": "DEXPI 2.0.1", "files": {path.name: sha256(path) for path in sorted(exchange.iterdir())},
        "validation": validation, "claim": dexpi_validate.claim(validation)})
    if validation["failed"] is not None or validation["round_trip"]:
        reason = (validation["problems"] or validation["round_trip"])[0]
        return finish(out, {"outcome": "rejected", "reason": reason})

    graph = dexpi_parse.graph(*parse(exchange))
    dump(out / "graph.json", graph)
    receipt = publish(graph, out, now)
    dump(out / "graph-manifest.json", {
        "source_revision": graph["source_revision"], "nodes": len(graph["nodes"]), "edges": len(graph["edges"]),
        "graph_sha256": sha256(out / "graph.json"), "snapshot_id": receipt.get("snapshot_id")})
    return finish(out, {"outcome": "accepted", "graph": receipt.pop("graph", graph)})


def parse(folder: Path) -> tuple[dict, dict | None]:
    return dexpi_parse.read(folder), dexpi_parse.load_sidecar(folder)


def publish(graph: dict, out: Path, now: str) -> dict:
    """Publish to Neo4j when LIONG_NEO4J is set, and query the snapshot's cross-sheet connections."""
    if not os.environ.get("LIONG_NEO4J"):
        receipt = {"outcome": "not published", "reason": "LIONG_NEO4J is not set"}
        dump(out / "publication-receipt.json", receipt)
        return receipt
    import graph_publish  # the neo4j driver is needed only when there is a server to publish to

    with graph_publish.connect() as driver:
        receipt = graph_publish.publish(driver, graph, now)
        with driver.session() as session:
            published = session.execute_read(graph_publish.read_back, receipt["snapshot_id"])
        dump(out / "query.json", graph_publish.cross_sheet(driver, receipt["snapshot_id"]))
    dump(out / "publication-receipt.json", receipt)
    return receipt | {"graph": published}


def finish(out: Path, result: dict) -> dict:
    dump(out / "result.json", result)
    return result


def main(argv: list[str]) -> int:
    args = list(argv)
    database = "--database" in args
    if database:
        args.remove("--database")
    key = None
    if "--answer-key" in args:
        index = args.index("--answer-key")
        key = Path(args[index + 1])
        del args[index:index + 2]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    revision, out = args[0], Path(args[1])
    result = run(revision, out, database)
    print(f"{revision}: {result['outcome']}" + (f": {result['reason']}" if result["outcome"] == "rejected" else ""))
    if key is None:
        return 0
    report = compare_answer_key.compare(result, json.loads(key.read_text(encoding="utf-8")), revision)
    compare_answer_key.write(report, out / "comparison")
    print(compare_answer_key.markdown(report), end="")
    return 0 if report["match"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
