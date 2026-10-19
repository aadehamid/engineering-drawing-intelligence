#!/usr/bin/env python3
"""Read DEXPI 2.0.1 files and their sidecar back into an engineering graph (DEC-077, DEC-086).

Usage:
  dexpi_parse.py PATH GRAPH_FILE [REPORT_FILE]

PATH is a folder that dexpi_generate.py wrote, or one DEXPI file such as DEXPI's
reference P&ID. GRAPH_FILE gets the graph in the shape graph_publish.py reads.
REPORT_FILE, if given, gets the unsupported report.

The graph's nodes, kinds, tags, names and edges come from the DEXPI files. The
sidecar adds only the evidence and the values DEXPI has no property for. A plant
object is a node when it is one of the supported classes; it gets back the ID its
PersistentIdentifier's context and value name, such as p3d:object:101 or
sps:item:<GUID>, or, in a file LIONG did not write, "dexpi:<file>#<id>". The context
of a file's drawing identifier names its backend, and so the predicate names its
attributes get (dexpi_generate.BACKENDS); a file LIONG did not write gets the p3d
names.
Everything else is counted in the unsupported report by class, and the parser never
fails on it (DEC-066). An off-page connector whose partner cannot be found is reported
as a gap, with no edge.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dexpi_generate as gen  # noqa: E402

MODEL_URIS = {gen.CORE_URI: "Core", gen.PLANT_URI: "Plant"}
NODE_KIND = {
    **{cls: "equipment" for cls in gen.EQUIPMENT_CLASS.values()},
    **{cls: "valve" for cls in gen.VALVE_CLASS.values()},
    **{cls: "sheet_connector" for cls in gen.CONNECTOR_CLASS.values()},
    "Plant/Instrumentation.ProcessInstrumentationFunction": "instrument",
    "Plant/Piping.PipingNetworkSegment": "pipe_segment",
    "Plant/Piping.PipeTee": "junction",
}
DIRECTION_OF_CLASS = {cls: direction for direction, cls in gen.CONNECTOR_CLASS.items()}
# Classes read only as structure around the nodes.
STRUCTURE = {
    "Core/EngineeringModel", "Plant/PlantModel", "Plant/Diagram.PlantMetaData", "Core/PersistentIdentifier",
    "Core/Diagram.Diagram", "Core/Diagram.RepresentationGroup", "Plant/Piping.PipingNetworkSystem",
    "Plant/Piping.Pipe", "Plant/Piping.DirectPipingConnection", "Plant/Piping.PipingNode",
    "Plant/ProcessEquipment.ProcessNozzle", "Plant/ProcessEquipment.InstrumentNozzle",
    "Plant/Instrumentation.ProcessSignalGeneratingFunction",
    "Plant/Piping.PipeOffPageConnectorReferenceByNumber", "Plant/Piping.PipeOffPageConnectorObjectReference",
}
SUPPORTED_CLASSES = frozenset(NODE_KIND) | frozenset(STRUCTURE)
NOZZLES = {"Plant/ProcessEquipment.ProcessNozzle", "Plant/ProcessEquipment.InstrumentNozzle"}
LETTERS_TYPE = {letters: tag_type for tag_type, letters in gen.INSTRUMENT_LETTERS.items()}
LIONG_IDS = tuple(prefix for prefix, _ in gen.CONTEXTS.values())  # the ID prefixes of nodes LIONG wrote
SAFE_PARSER = dict(resolve_entities=False, no_network=True, load_dtd=False)


def parse_xml(path: Path) -> etree._ElementTree:
    """A DEXPI file, parsed without the network and without entity resolution."""
    return etree.parse(str(path), etree.XMLParser(**SAFE_PARSER))


def dexpi_files(path: Path) -> list[Path]:
    return sorted(path.glob("*.xml")) if path.is_dir() else [path]


def load_sidecar(path: Path) -> dict | None:
    file = path / gen.SIDECAR if path.is_dir() else None
    return json.loads(file.read_text(encoding="utf-8")) if file and file.exists() else None


def text(o: etree._Element, prop: str) -> str | None:
    return o.findtext(f"Data[@property='{prop}']/String")


def ref(o: etree._Element, prop: str) -> str | None:
    found = o.find(f"References[@property='{prop}']")
    objects = found.get("objects", "") if found is not None else ""
    return objects[1:] if objects.startswith("#") and " " not in objects else None


def children(o: etree._Element, prop: str) -> list[etree._Element]:
    return o.findall(f"Components[@property='{prop}']/Object")


def identity(o: etree._Element) -> str | None:
    """The ID a LIONG PersistentIdentifier names, such as p3d:object:101, else None."""
    for pid in children(o, "PersistentIdentifiers"):
        context, key = text(pid, "Context"), text(pid, "Value")
        if context in gen.CONTEXTS and key:
            return gen.CONTEXTS[context][0] + key
    return None


def backend_of(o: etree._Element | None) -> gen.Backend:
    """The backend whose drawing context the PlantMetaData `o` carries; p3d for any other file."""
    for pid in children(o, "PersistentIdentifiers") if o is not None else []:
        if text(pid, "Context") in gen.CONTEXTS:
            return gen.CONTEXTS[text(pid, "Context")][1]
    return gen.BACKENDS["p3d"]


def read(path: Path) -> dict:
    """The facts the DEXPI files state, before any sidecar is used."""
    facts = {"nodes": {}, "drawings": {}, "relations": [], "appearances": [], "exported": {},
             "unsupported": Counter(), "problems": [], "gaps": [], "model_uri": None}
    connectors = []
    for file in dexpi_files(path):
        read_file(file, facts, connectors)
    index = {(c["drawing_name"], c["label"]): c for c in connectors if c["label"] is not None}
    by_node = {c["node"]: c for c in connectors}
    for out in sorted((c for c in connectors if c["direction"] == "Out"), key=lambda c: c["node"]):
        target = out["target"]
        partner = index.get(target[1:]) if target and target[0] == "number" else by_node.get(target[1]) if target else None
        if partner is None:
            facts["gaps"].append(f"{out['node']} continues to {target[1:] if target else 'nothing'}, which is not here")
            continue
        back = partner["target"]
        points_back = back == ("number", out["drawing_name"], out["label"]) or back == ("node", out["node"])
        if partner["direction"] != "In" or not points_back:
            facts["problems"].append(f"{out['node']} and {partner['node']} do not refer to each other as Out and In")
            continue
        facts["relations"].append(("continues_to", out["node"], partner["node"]))
    continued = {r[2] for r in facts["relations"] if r[0] == "continues_to"}
    for c in connectors:
        if c["direction"] == "In" and c["node"] not in continued:
            facts["gaps"].append(f"nothing here continues to {c['node']}")
    facts["relations"].sort()
    facts["appearances"].sort()
    return facts


def read_file(file: Path, facts: dict, connectors: list) -> None:
    root = parse_xml(file).getroot()
    facts["model_uri"] = facts["model_uri"] or root.get("uri")
    prefixes = {i.get("prefix"): MODEL_URIS.get(i.get("source")) for i in root.findall("Import")}

    def kind_of(o: etree._Element) -> str:
        prefix, _, rest = (o.get("type") or "").partition("/")
        return f"{prefixes.get(prefix) or prefix}/{rest}"

    byid = {o.get("id"): o for o in root.iter("Object") if o.get("id")}
    for o in root.iter("Object"):
        cls = kind_of(o)
        if cls not in SUPPORTED_CLASSES:
            facts["unsupported"][cls] += 1

    metadata = next((o for o in root.iter("Object") if kind_of(o) == "Plant/Diagram.PlantMetaData"), None)
    diagram = next((o for o in root.iter("Object") if kind_of(o) == "Core/Diagram.Diagram"), None)
    backend = backend_of(metadata)
    drawing = (identity(metadata) if metadata is not None else None) or f"dexpi:{file.name}"
    name = (text(metadata, "FileName") if metadata is not None else None) or (
        text(diagram, "Name") if diagram is not None else None) or file.stem
    facts["drawings"][drawing] = {"name": name, "file": file.name,
                                  "revision": text(metadata, "RevisionNumber") if metadata is not None else None}
    facts["exported"][file.name] = root.findtext("Object/Data[@property='ExportDateTime']/DateTime")

    node_of_element = {}
    for o in root.iter("Object"):
        kind = NODE_KIND.get(kind_of(o))
        if kind is None:
            continue
        if kind == "pipe_segment" and not pipe_shaped(o, kind_of):
            continue
        node = identity(o)
        if node is None and o.get("id"):
            node = f"dexpi:{file.name}#{o.get('id')}"
        elif node is None:
            facts["problems"].append(f"a {kind_of(o)} in {file.name} has no id")
            continue
        node_of_element[o] = node

    def node_of(xml_id: str | None) -> str | None:
        o = byid.get(xml_id)
        if o is None:
            return None
        if o in node_of_element:
            return node_of_element[o]
        if kind_of(o) in NOZZLES:
            owner = o.getparent().getparent()
            return node_of_element.get(owner)
        return None

    for o, node in node_of_element.items():
        cls = kind_of(o)
        kind = NODE_KIND[cls]
        entry = {"kind": kind, "drawing": drawing, "attributes": {}, "file": file.name, "xml_id": o.get("id")}
        attrs = entry["attributes"]
        if kind == "equipment":
            entry["tag"] = text(o, "TagName")
            attrs.update({backend.tag_letters: text(o, "TagNamePrefix"), backend.tag_number: text(o, "TagNameSequenceNumber"),
                          "description": o.findtext("Data[@property='EquipmentDescription']//Data[@property='Value']/String")})
        elif kind == "valve":
            entry["tag"] = text(o, "PipingComponentNumber")
        elif kind == "instrument":
            letters = (text(o, "ProcessInstrumentationFunctionCategory"), text(o, "ProcessInstrumentationFunctions"))
            number = text(o, "ProcessInstrumentationFunctionNumber")
            tag_type = LETTERS_TYPE.get(letters)  # letter codes outside the table get no tag type and no tag
            if tag_type is None and node.startswith(LIONG_IDS):
                facts["problems"].append(f"{node} has instrument letters {'/'.join(map(str, letters))}, "
                                         "outside the supported subset")
            attrs.update({backend.tag_letters: tag_type, backend.instrument_number: number})
            entry["tag"] = f"{tag_type}-{number}" if tag_type and number else None
            for sensing in children(o, "ProcessSignalGeneratingFunctions"):
                owner = node_of(ref(sensing, "SensingLocation"))
                if owner is None:
                    facts["problems"].append(f"{node} senses at {ref(sensing, 'SensingLocation')}, which is no supported node")
                else:
                    facts["relations"].append(("owned_by", node, owner))
        elif kind == "pipe_segment":
            entry["tag"] = text(o, "SegmentNumber")
            system = o.getparent().getparent()
            size = text(o, "NominalDiameterNumericalValueRepresentation")
            attrs.update(line_number=text(system, "LineNumber") if kind_of(system) == "Plant/Piping.PipingNetworkSystem" else None,
                         nominal_size_mm=int(size) if size and size.isdigit()
                         and text(o, "NominalDiameterTypeRepresentation") == "DN" else None)
            for predicate, prop in (("starts_at", "SourceItem"), ("ends_at", "TargetItem")):
                other = node_of(ref(o, prop))
                if other is None:
                    facts["problems"].append(f"{node}'s {prop} {ref(o, prop)} is no supported node")
                else:
                    facts["relations"].append((predicate, node, other))
        elif kind == "sheet_connector":
            direction = DIRECTION_OF_CLASS[cls]
            label = text(o, "PipeConnectorNumber")
            entry["name"] = label
            words = {value: name for name, value in backend.directions.items()}
            attrs.update({"label": label, backend.direction: words[direction]})
            target = None
            for reference in children(o, "ConnectorReference"):
                if kind_of(reference) == "Plant/Piping.PipeOffPageConnectorReferenceByNumber":
                    target = ("number", text(reference, "ReferencedDrawingNumber"), text(reference, "ReferencedConnectorNumber"))
                else:
                    target = ("node", node_of(ref(reference, "ReferencedConnector")))
            connectors.append({"node": node, "direction": direction, "label": label, "drawing_name": name, "target": target})
        entry["attributes"] = {k: v for k, v in attrs.items() if v is not None}
        facts["nodes"][node] = entry

    for segment in root.iter("Object"):
        if kind_of(segment) != "Plant/Piping.PipingNetworkSegment" or segment in node_of_element:
            continue
        connections = children(segment, "Connections")
        direct = all(kind_of(c) == "Plant/Piping.DirectPipingConnection" for c in connections)
        if not connections or not direct or children(segment, "Items") or identity(segment):
            facts["unsupported"]["Plant/Piping.PipingNetworkSegment"] += 1
            facts["problems"].append(f"segment {segment.get('id')} in {file.name} is neither one pipe nor direct connections")
            continue
        for c in connections:
            a, b = node_of(ref(c, "SourceItem")), node_of(ref(c, "TargetItem"))
            if a is None or b is None:
                facts["problems"].append(f"a direct connection in {segment.get('id')} joins no supported nodes")
            else:
                facts["relations"].append(("connects_to", a, b))

    if diagram is not None:
        for group in children(diagram, "Groups"):
            if kind_of(group) != "Core/Diagram.RepresentationGroup":
                continue
            node = node_of_element.get(byid.get(ref(group, "Represents")))
            if node is not None:
                facts["appearances"].append((node, drawing))


def pipe_shaped(segment: etree._Element, kind_of) -> bool:
    """Whether a segment is one pipe between its own two ends, the shape that makes it a node."""
    connections = children(segment, "Connections")
    if len(connections) != 1 or kind_of(connections[0]) != "Plant/Piping.Pipe":
        return False
    return all(ref(connections[0], p) == ref(segment, p) for p in ("SourceItem", "SourceNode", "TargetItem", "TargetNode"))


def relation_index(sidecar: dict | None) -> dict[tuple, tuple[str, dict]]:
    """Each relationship assertion in the sidecar, by (predicate, subject, target)."""
    if not sidecar:
        return {}
    return {(a["predicate"], a["subject_id"], a["value_or_target"]): (aid, a)
            for aid, a in sidecar["assertions"].items() if a["predicate"] in gen.RELATIONS}


def graph(facts: dict, sidecar: dict | None) -> dict:
    """The graph in graph_publish.py's shape, with evidence from the sidecar when there is one."""
    objects = sidecar["objects"] if sidecar else {}
    appearances = sidecar["appearances"] if sidecar else {}
    drawings = sidecar["drawings"] if sidecar else {}
    relations = relation_index(sidecar)
    nodes, edges = [], []
    for did, d in sorted(facts["drawings"].items()):
        evidence = [drawings[did]["source_locator"]] if did in drawings else [{"file": d["file"]}]
        nodes.append({"id": did, "kind": "drawing", "name": d["name"], "evidence": evidence})
    for nid, n in sorted(facts["nodes"].items()):
        node = {"id": nid, "kind": n["kind"]}
        if n.get("tag"):
            node["tag"] = n["tag"]
        if n.get("name"):
            node["name"] = n["name"]
        if nid in objects:
            evidence = [objects[nid]["source_locator"]]
            if "tag" in objects[nid] and n.get("tag"):
                evidence.append(objects[nid]["tag"]["source_locator"])
            if nid in appearances:
                evidence.append({"artifact_id": n["drawing"], **appearances[nid]})
        else:
            evidence = [{"file": n["file"], "object": n["xml_id"]}]
        node["evidence"] = evidence
        nodes.append(node)
    for predicate, subject, target in facts["relations"]:
        kind, source, sink = gen.edge_of(predicate, subject, target)
        found = relations.get((predicate, subject, target))
        evidence = [found[1]["source_locator"]] if found else []
        edges.append({"kind": kind, "source": source, "target": sink, "evidence": evidence})
        if predicate == "continues_to":
            edges.append({"kind": "CROSS_SHEET_REFERENCE", "source": source, "target": sink, "evidence": evidence})
    for node, drawing in facts["appearances"]:
        evidence = [appearances[node]["source_locator"]] if node in appearances else []
        edges.append({"kind": "ON_SHEET", "source": node, "target": drawing, "evidence": evidence})
    revision = sidecar["source_revision"]["revision_id"] if sidecar else f"dexpi:{facts['model_uri']}"
    return {"source_revision": revision, "nodes": nodes, "edges": sorted(edges, key=lambda e: json.dumps(e, sort_keys=True))}


def records(facts: dict, sidecar: dict) -> dict:
    """The extraction records the DEXPI files and the sidecar state together, for generating again."""
    found = []
    assertions = sidecar["assertions"]
    by_subject_predicate = {(a["subject_id"], a["predicate"]): (aid, a) for aid, a in assertions.items()
                            if a["predicate"] not in gen.RELATIONS}
    objects, tags = [], []
    backend = gen.BACKENDS[sidecar["source_revision"]["source_id"]]
    for nid, n in facts["nodes"].items():
        found_id = gen.split_id(nid, backend.objects)
        if found_id is None:
            continue
        side = sidecar["objects"].get(nid, {})
        objects.append({"object_id": nid, "object_kind": n["kind"], "source_object_key": backend.key_type(found_id[1]),
                        "source_locator": side.get("source_locator")})
        if n.get("tag") is not None:
            tags.append({"object_id": nid, "tag_value": n["tag"], **side.get("tag", {})})
        for predicate, value in n["attributes"].items():
            if predicate in backend.carried.get(n["kind"], set()) and (nid, predicate) in by_subject_predicate:
                aid, a = by_subject_predicate[(nid, predicate)]
                found.append({"assertion_id": aid, **a, "value_or_target": value})
    for (subject, predicate), (aid, a) in by_subject_predicate.items():
        if subject in facts["nodes"] and predicate not in backend.carried.get(facts["nodes"][subject]["kind"], set()):
            found.append({"assertion_id": aid, **a})
    relations = relation_index(sidecar)
    for relation in facts["relations"]:
        if relation in relations:
            aid, a = relations[relation]
            found.append({"assertion_id": aid, **a})
    drawings = [{"artifact_id": did, "name": d["name"], "revision": d["revision"], **sidecar["drawings"].get(did, {})}
                for did, d in facts["drawings"].items()]
    appearances = [{"object_id": node, "artifact_id": drawing, **sidecar["appearances"].get(node, {})}
                   for node, drawing in facts["appearances"]]
    by = lambda field: lambda record: str(record[field])  # noqa: E731
    return {
        "source_manifest": sidecar["source_manifest"],
        "source_revision": sidecar["source_revision"],
        "objects": sorted(objects, key=by("object_id")),
        "tag_assignments": sorted(tags, key=by("object_id")),
        "assertions": sorted(found, key=by("assertion_id")),
        "drawings": sorted(drawings, key=by("artifact_id")),
        "appearances": sorted(appearances, key=by("appearance_id")),
    }


def report(facts: dict) -> dict:
    """What the parser did not turn into graph facts."""
    return {"unsupported_classes": dict(sorted(facts["unsupported"].items())),
            "problems": facts["problems"], "gaps": facts["gaps"]}


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[0])
    facts = read(path)
    result = graph(facts, load_sidecar(path))
    Path(argv[1]).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    unsupported = report(facts)
    if len(argv) == 3:
        Path(argv[2]).write_text(json.dumps(unsupported, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(result['nodes'])} nodes, {len(result['edges'])} edges; "
          f"{sum(unsupported['unsupported_classes'].values())} unsupported objects in "
          f"{len(unsupported['unsupported_classes'])} classes, {len(unsupported['problems'])} problems, "
          f"{len(unsupported['gaps'])} gaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
