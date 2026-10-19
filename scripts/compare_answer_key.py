#!/usr/bin/env python3
"""Compare a pipeline result with the answer key, exactly (MILESTONE-001 step 6, DEC-059).

Usage:
  compare_answer_key.py RESULT_FILE REVISION ANSWER_KEY OUT_DIR

A result file holds {"outcome": "accepted", "graph": GRAPH} or
{"outcome": "rejected", "reason": TEXT}. GRAPH is the published graph, in the shape
scripts/graph_publish.py reads. The comparison maps every source ID
(`p3d:object:<ObjectId>` and `p3d:drawing:<DrawingId>`, or `sps:item:<GUID>`,
`sps:line:<GUID>` and `sps:sheet:<GUID>`) to the answer key's alias through the key's
`keys` table, for the backend the key names, then requires the expected outcome and, for an accepted
revision, exactly the expected nodes and edges; for a rejected one, exactly the
expected reason. It writes report.json and report.md to OUT_DIR, and exits 1 on any
difference.

This is the scorer, so it is the one step that reads the answer key.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

GUID = r"[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
SOURCE_ID = re.compile(rf"(p3d):(?:object|drawing):(\d+)|(sps):(?:item|line|sheet):({GUID})")


class CompareError(Exception):
    """The result names a source key the answer key does not know."""


def aliases(answer_key: dict) -> dict[tuple[str, str], str]:
    """Each (backend, source key) in the answer key, mapped to its alias."""
    return {(answer_key["backend"], str(key)): alias for alias, key in answer_key["keys"].items()}


def alias(identifier: str, names: dict[tuple[str, str], str]) -> str:
    match = SOURCE_ID.fullmatch(identifier)
    key = (match.group(1) or match.group(3), match.group(2) or match.group(4)) if match else None
    if key not in names:
        raise CompareError(f"{identifier} is not a key in the answer key")
    return names[key]


def normalize_graph(graph: dict, names: dict[tuple[str, str], str]) -> tuple[list[str], list[list[str]]]:
    """The graph as the answer key writes it: sorted aliases and sorted [kind, source, target]."""
    nodes = sorted(alias(node["id"], names) for node in graph["nodes"])
    edges = sorted([edge["kind"], alias(edge["source"], names), alias(edge["target"], names)]
                   for edge in graph["edges"])
    return nodes, edges


def normalize_reason(reason: str, names: dict[tuple[str, str], str]) -> str:
    return SOURCE_ID.sub(lambda match: alias(match.group(0), names), reason)


def compare(result: dict, answer_key: dict, revision: str) -> dict:
    """The comparison report: what was expected, what was found, and every difference.

    A source ID the answer key does not know is reported as a difference, not raised.
    """
    try:
        return _compare(result, answer_key, revision)
    except CompareError as error:
        expected = answer_key["revisions"][revision]
        return {"revision": revision, "expected_outcome": expected["expected"], "outcome": result["outcome"],
                "differences": [str(error)], "match": False}


def _compare(result: dict, answer_key: dict, revision: str) -> dict:
    expected = answer_key["revisions"][revision]
    names = aliases(answer_key)
    report = {"revision": revision, "expected_outcome": expected["expected"], "outcome": result["outcome"],
              "differences": []}
    differences = report["differences"]
    if result["outcome"] != expected["expected"]:
        differences.append(f"outcome is {result['outcome']}, expected {expected['expected']}")
    if result["outcome"] == "rejected":
        reason = normalize_reason(result["reason"], names)
        report["reason"] = reason
        if expected["expected"] == "rejected" and reason != expected["reason"]:
            differences.append(f"reason is {reason!r}, expected {expected['reason']!r}")
    else:
        nodes, edges = normalize_graph(result["graph"], names)
        report |= {"nodes": len(nodes), "edges": len(edges),
                   "expected_nodes": len(expected["nodes"]), "expected_edges": len(expected["edges"])}
        if expected["expected"] == "accepted":
            differences += [f"missing node {n}" for n in sorted(set(expected["nodes"]) - set(nodes))]
            differences += [f"extra node {n}" for n in sorted(set(nodes) - set(expected["nodes"]))]
            found, wanted = {tuple(e) for e in edges}, {tuple(e) for e in expected["edges"]}
            differences += [f"missing edge {' '.join(e)}" for e in sorted(wanted - found)]
            differences += [f"extra edge {' '.join(e)}" for e in sorted(found - wanted)]
            if len(edges) != len(found):
                differences.append("the graph repeats an edge")
            if len(nodes) != len(set(nodes)):
                differences.append("the graph repeats a node")
    report["match"] = not differences
    return report


def markdown(report: dict) -> str:
    lines = [f"# Answer-key comparison, revision {report['revision']}", "",
             f"Result: {'exact match' if report['match'] else 'mismatch'}.", "",
             f"Outcome: {report['outcome']} (expected {report['expected_outcome']})."]
    if "nodes" in report:
        lines.append(f"Nodes: {report['nodes']} (expected {report['expected_nodes']}). "
                     f"Edges: {report['edges']} (expected {report['expected_edges']}).")
    if "reason" in report:
        lines.append(f"Reason: {report['reason']}")
    if report["differences"]:
        lines += ["", "Differences:", ""] + [f"- {d}" for d in report["differences"]]
    return "\n".join(lines) + "\n"


def write(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(markdown(report), encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    result = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    answer_key = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    report = compare(result, answer_key, argv[1])
    write(report, Path(argv[3]))
    print(markdown(report), end="")
    return 0 if report["match"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
