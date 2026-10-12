#!/usr/bin/env python3
"""Load a canonical world file, apply its revisions, and check each revision's state.

A world file holds nodes, edges, and revisions written as changes from a named base
(DEC-018). Each non-drawing node's `sheet` gives its ON_SHEET edge, so deleting a node
removes that edge too. Every other edge is listed, and deleting a node leaves them in
place: a revision that does so has dangling edges and is invalid. A revision marked
`expected: rejected` must be invalid; every other revision must be valid.

Usage: world.py check [WORLD.yaml ...]   (default: every worlds/*.yaml)
"""
from __future__ import annotations

import functools
import json
import sys
from pathlib import Path
from typing import NamedTuple

import yaml
from jsonschema import Draft202012Validator

from liong_facts import ON_SHEET, ROOT, Edge

SCHEMA = ROOT / "schemas" / "canonical-world.schema.json"


class State(NamedTuple):
    """One revision of a world: its nodes and its listed (non-ON_SHEET) edges."""

    nodes: dict[str, dict]
    edges: frozenset[Edge]

    def all_edges(self) -> frozenset[Edge]:
        on_sheet = {Edge(ON_SHEET, alias, node["sheet"]) for alias, node in self.nodes.items() if "sheet" in node}
        return self.edges | on_sheet


class RevisionError(Exception):
    """A revision cannot be built: a missing base, a cycle, or a change to something absent."""


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@functools.cache
def validator() -> Draft202012Validator:
    return Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def schema_errors(world: dict) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in validator().iter_errors(world)]


def base_state(world: dict) -> State:
    edges = frozenset(Edge(kind, s, t) for kind, pairs in world["edges"].items() for s, t in pairs)
    return State({alias: dict(node) for alias, node in world["nodes"].items()}, edges)


def apply(state: State, changes: list[dict]) -> State:
    nodes = {alias: dict(node) for alias, node in state.nodes.items()}
    edges = set(state.edges)
    for change in changes:
        if "set_tag" in change:
            alias = change["set_tag"]["node"]
            if alias not in nodes or nodes[alias]["class"] == "drawing":
                raise RevisionError(f"set_tag names {alias}, which is not an engineering node in the base")
            nodes[alias]["tag"] = change["set_tag"]["tag"]
        elif "delete_node" in change:
            alias = change["delete_node"]
            if alias not in nodes:
                raise RevisionError(f"delete_node names {alias}, which is not in the base")
            del nodes[alias]
        else:
            edge = Edge(*change["delete_edge"])
            if edge not in edges:
                raise RevisionError(f"delete_edge names {edge.kind} {edge.source}->{edge.target}, which is not in the base")
            edges.remove(edge)
    return State(nodes, frozenset(edges))


def state(world: dict, revision: str) -> State:
    """The state of `revision`, built by applying each change along its chain of bases."""
    chain: list[str] = []
    current: str | None = revision
    while current is not None:
        if current in chain:
            raise RevisionError(f"cycle in its bases: {' -> '.join(chain + [current])}")
        if current not in world["revisions"]:
            raise RevisionError(f"unknown base {current}" if chain else f"no revision named {current}")
        chain.append(current)
        current = world["revisions"][current]["base"]
    result = base_state(world)
    for name in reversed(chain):
        result = apply(result, world["revisions"][name].get("changes", []))
    return result


def problems(s: State) -> list[str]:
    """Why a state is invalid: edges whose endpoints are missing, or sheets that are not drawings."""
    found = []
    for edge in sorted(s.edges):
        missing = [end for end in (edge.source, edge.target) if end not in s.nodes]
        if missing:
            found.append(f"{edge.kind} {edge.source}->{edge.target} has missing endpoint {', '.join(missing)}")
    for alias, node in sorted(s.nodes.items()):
        sheet = node.get("sheet")
        if sheet is not None and s.nodes.get(sheet, {}).get("class") != "drawing":
            found.append(f"{alias} is on sheet {sheet}, which is not a drawing node")
    return found


def check(world: dict, label: str) -> tuple[list[str], list[str]]:
    """(errors, notes) for one world file. Notes report each rejected revision and why."""
    errors = [f"{label}: {e}" for e in schema_errors(world)]
    if errors:
        return errors, []
    notes = []
    for name, revision in world["revisions"].items():
        try:
            found = problems(state(world, name))
        except RevisionError as error:
            errors.append(f"{label}: revision {name}: {error}")
            continue
        if revision.get("expected") == "rejected":
            if found:
                notes.append(f"{label}: revision {name} is rejected as expected: {found[0]}")
            else:
                errors.append(f"{label}: revision {name} is marked expected: rejected but is valid")
        else:
            errors += [f"{label}: revision {name}: {p}" for p in found]
    return errors, notes


def main(argv: list[str]) -> int:
    if not argv or argv[0] != "check":
        print(__doc__, file=sys.stderr)
        return 2
    paths = [Path(p) for p in argv[1:]] or sorted((ROOT / "worlds").glob("*.yaml"))
    errors: list[str] = []
    for path in paths:
        found, notes = check(load(path), path.name)
        errors += found
        for note in notes:
            print(note)
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print(f"World files valid: {', '.join(p.name for p in paths)}.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
