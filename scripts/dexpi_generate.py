#!/usr/bin/env python3
"""Write extraction records as DEXPI 2.0.1, one file per drawing, plus a sidecar (DEC-077).

Usage:
  dexpi_generate.py RECORDS_FILE OUT_FOLDER   RECORDS_FILE is what extract_p3d.py writes

Each drawing becomes one EngineeringModel file named for the drawing, because a DEXPI
2.0.1 file holds one diagram. Each plant object carries its ID, such as p3d:object:101,
in a PersistentIdentifier; each drawing's PlantMetaData carries p3d:drawing:<id>. The
mapping, the objects DEXPI needs that the source lacks, and their IDs are DEC-077's.

`sidecar.json` is a LIONG manifest, not DEXPI. It holds what DEXPI 2.0.1 has no
property for (units, the descriptions of valves, junctions and instruments, tag parts,
drawing status) and the source locators that the graph uses as evidence, keyed by the
records' IDs.

The generator refuses a source it cannot write faithfully. A relationship that names a
missing object raises Rejection, which names the graph edge it would have made. Data
outside the supported subset raises Unsupported. The output is a function of the
records alone: the same records always give the same bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

from lxml import etree

CORE_URI = "https://data.dexpi.org/models/2.0.1/Core.xml"
PLANT_URI = "https://data.dexpi.org/models/2.0.1/Plant.xml"
OBJECT_CONTEXT = "p3d/PlantObject.ObjectId"
DRAWING_CONTEXT = "p3d/Drawing.DrawingId"
SIDECAR = "sidecar.json"
SIDECAR_FORMAT = "liong-dexpi-sidecar/1"
GENERATOR = ("LIONG p3d-to-DEXPI mapper", "LIONG", "dexpi_generate 1")
EQUIPMENT_CLASS = {"TK": "Plant/ProcessEquipment.Tank"}
VALVE_CLASS = {"XV": "Plant/Piping.OperatedValve"}
INSTRUMENT_LETTERS = {"PI": ("P", "I")}  # tag type -> (ProcessInstrumentationFunctionCategory, ...Functions)
CONNECTOR_CLASS = {"Out": "Plant/Piping.FlowOutPipeOffPageConnector", "In": "Plant/Piping.FlowInPipeOffPageConnector"}
TABLE = {"equipment": "Equipment", "valve": "Valve", "instrument": "Instrument", "pipe_segment": "LineSegment",
         "junction": "Junction", "sheet_connector": "SheetConnector"}
# The attribute predicates DEXPI carries for each object kind; every other attribute goes to the sidecar.
CARRIED = {"equipment": {"tag_type", "tag_number", "description"}, "valve": set(),
           "instrument": {"tag_type", "loop_number"}, "pipe_segment": {"line_number", "nominal_size_mm"},
           "junction": set(), "sheet_connector": {"label", "direction"}}
# Relationship predicates in the order the source tables list them, with the graph edge each one makes.
RELATIONS = ("starts_at", "ends_at", "connects_to", "continues_to", "owned_by")
ID_PATTERN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


class SourceError(Exception):
    """The records cannot be written as DEXPI."""


@dataclass
class Rejection(SourceError):
    """A relationship names an object the records do not hold."""
    edge_kind: str
    source: str
    target: str
    missing: str

    def __str__(self) -> str:
        return f"{self.edge_kind} {self.source}->{self.target} has missing endpoint {self.missing}"


class Unsupported(SourceError):
    """The records hold something outside the supported subset."""


def edge_of(predicate: str, subject: str, target: str) -> tuple[str, str, str]:
    """The graph edge a relationship states, as (kind, source, target)."""
    if predicate == "starts_at":
        return "FLOW", target, subject
    if predicate == "owned_by":
        return "INSTRUMENT_PARENT", subject, target
    return "FLOW", subject, target


# ---------- XML building: each object's properties are written sorted by property name ----------

class Obj:
    def __init__(self, type_: str, id_: str | None = None):
        self.type, self.id, self.props = type_, id_, []

    def data(self, name: str, *values) -> "Obj":
        self.props.append((name, "Data", values))
        return self

    def comp(self, name: str, *objects: "Obj", ordered: bool = False) -> "Obj":
        if objects:
            self.props.append((name, "Components", list(objects) if ordered else sorted(objects, key=lambda o: o.id or "")))
        return self

    def ref(self, name: str, id_: str) -> "Obj":
        self.props.append((name, "References", id_))
        return self

    def xml(self) -> etree._Element:
        element = etree.Element("Object")
        if self.id:
            element.set("id", self.id)
        element.set("type", self.type)
        for name, kind, payload in sorted(self.props, key=lambda p: p[0]):
            child = etree.SubElement(element, kind, property=name)
            if kind == "Data":
                child.extend(payload)
            elif kind == "Components":
                child.extend(o.xml() for o in payload)
            else:
                child.set("objects", "#" + payload)
        return element


def value(tag: str, text: object) -> etree._Element:
    element = etree.Element(tag)
    element.text = str(text)
    return element


def string(text: object) -> etree._Element:
    return value("String", text)


def aggregate(type_: str, **fields: etree._Element) -> etree._Element:
    element = etree.Element("AggregatedDataValue", type=type_)
    for name, field in fields.items():
        etree.SubElement(element, "Data", property=name).append(field)
    return element


def text_in_english(text: str) -> etree._Element:
    return aggregate("Core/DataTypes.MultiLanguageString", SingleLanguageStrings=aggregate(
        "Core/DataTypes.SingleLanguageString", Language=string("en"), Value=string(text)))


def identifier(context: str, key: object) -> Obj:
    return Obj("Core/PersistentIdentifier").data("Context", string(context)).data("Value", string(key))


# ---------- the source, checked ----------

def once(group: str, keys: list) -> None:
    """Refuse records that would collapse onto each other: a key may appear only once."""
    seen = set()
    for key in keys:
        if key in seen:
            raise Unsupported(f"{group} holds {key} more than once")
        seen.add(key)


class Source:
    """The records arranged for writing, after every check that can refuse them."""

    def __init__(self, records: dict):
        self.records = records
        for group, field in (("objects", "object_id"), ("drawings", "artifact_id"), ("drawings", "name"),
                             ("tag_assignments", "object_id"), ("assertions", "assertion_id")):
            once(group, [record[field] for record in records[group]])
        once("assertions", [(a["subject_id"], a["predicate"]) for a in records["assertions"]
                            if a["predicate"] not in RELATIONS])
        # A segment has one start and one end, an instrument one owner, and a connector one
        # partner each way; a repeated connection is one connection.
        once("assertions", [(a["subject_id"], a["predicate"]) for a in records["assertions"]
                            if a["predicate"] in ("starts_at", "ends_at", "owned_by", "continues_to")])
        once("assertions", [(a["value_or_target"], "continued_from") for a in records["assertions"]
                            if a["predicate"] == "continues_to"])
        once("assertions", [(a["subject_id"], a["predicate"], a["value_or_target"]) for a in records["assertions"]
                            if a["predicate"] == "connects_to"])
        self.objects = {o["object_id"]: o for o in records["objects"]}
        self.drawings = {d["artifact_id"]: d for d in records["drawings"]}
        self.tags = {t["object_id"]: t["tag_value"] for t in records["tag_assignments"]}
        self.attributes: dict[str, dict] = {oid: {} for oid in self.objects}
        relations = []
        for a in records["assertions"]:
            if a["predicate"] in RELATIONS:
                relations.append(a)
            elif a["subject_id"] in self.objects:
                self.attributes[a["subject_id"]][a["predicate"]] = a["value_or_target"]
        relations.sort(key=lambda a: (RELATIONS.index(a["predicate"]), a["assertion_id"]))
        for a in relations:
            kind, source, target = edge_of(a["predicate"], a["subject_id"], a["value_or_target"])
            for end in (source, target):
                if end not in self.objects:
                    raise Rejection(edge_kind=kind, source=source, target=target, missing=end)
        self.relations = [(a["predicate"], a["subject_id"], a["value_or_target"]) for a in relations]
        self.sheet = {}
        for appearance in records["appearances"]:
            oid, did = appearance["object_id"], appearance["artifact_id"]
            if oid not in self.objects or did not in self.drawings:
                raise Unsupported(f"appearance {appearance['appearance_id']} names a missing object or drawing")
            if oid in self.sheet:
                raise Unsupported(f"{oid} appears on more than one drawing")
            self.sheet[oid] = did
        for oid, obj in self.objects.items():
            if obj["object_kind"] not in TABLE:
                raise Unsupported(f"{oid} has object kind {obj['object_kind']}, outside the supported subset")
            if oid not in self.sheet:
                raise Unsupported(f"{oid} appears on no drawing")
        for name in (d["name"] for d in self.drawings.values()):
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name or "") or name == Path(SIDECAR).stem:
                raise Unsupported(f"drawing name {name!r} cannot be a file name")
        self.start, self.end = {}, {}
        for predicate, subject, target in self.relations:
            if predicate in ("starts_at", "ends_at"):
                if self.kind(subject) != "pipe_segment":
                    raise Unsupported(f"{subject} {predicate} {target}, but only pipe segments start and end")
                (self.start if predicate == "starts_at" else self.end)[subject] = target
            if predicate in ("starts_at", "ends_at", "connects_to") and self.sheet[subject] != self.sheet[target]:
                raise Unsupported(f"{subject} {predicate} {target} crosses drawings without an off-page connector")
            if predicate == "owned_by":
                if (self.kind(subject), self.kind(target)) != ("instrument", "equipment"):
                    raise Unsupported(f"{subject} owned_by {target} is not an instrument owned by equipment")
                if self.sheet[subject] != self.sheet[target]:
                    raise Unsupported(f"{subject} owned_by {target} crosses drawings")
            if predicate == "continues_to":
                directions = (self.attributes[subject].get("direction"), self.attributes[target].get("direction"))
                if directions != ("Out", "In"):
                    raise Unsupported(f"{subject} continues_to {target} does not pair an Out with an In connector")
        for segment in self.of_kind("pipe_segment"):
            if segment not in self.start or segment not in self.end:
                raise Unsupported(f"{segment} lacks a start or an end")
        if len({r["revision_id"] for r in records["assertions"]} | {records["source_revision"]["revision_id"]}) != 1:
            raise Unsupported("the assertions name more than one revision")

    def kind(self, oid: str) -> str:
        return self.objects[oid]["object_kind"]

    def of_kind(self, kind: str) -> list[str]:
        return sorted((o for o in self.objects if self.kind(o) == kind), key=self.key)

    def key(self, oid: str) -> int:
        return self.objects[oid]["source_object_key"]

    def xml_id(self, oid: str) -> str:
        return f"{TABLE[self.kind(oid)]}_{self.key(oid)}"


# ---------- writing ----------

def generate(records: dict) -> dict[str, bytes]:
    """Every output file, by name: one DEXPI file per drawing and the sidecar."""
    src = Source(records)
    nodes_of: dict[str, list[Obj]] = {}
    nozzles_of: dict[str, list[Obj]] = {}

    def end(oid: str, partner: str) -> tuple[str, str]:
        """(item id, node id) where object `oid` meets the connection to `partner`, an XML id."""
        if src.kind(oid) == "equipment":
            nozzle = f"{src.xml_id(oid)}_Nozzle_{partner}"
            node = Obj("Plant/Piping.PipingNode", f"{nozzle}_Node")
            nozzles_of.setdefault(oid, []).append(Obj("Plant/ProcessEquipment.ProcessNozzle", nozzle).comp("Nodes", node))
            return nozzle, node.id
        if src.kind(oid) in ("pipe_segment", "instrument"):
            raise Unsupported(f"{oid} cannot be the end of a piping connection")
        node = Obj("Plant/Piping.PipingNode", f"{src.xml_id(oid)}_Node_{partner}")
        nodes_of.setdefault(oid, []).append(node)
        return src.xml_id(oid), node.id

    def ends(o: Obj, source: tuple[str, str], target: tuple[str, str]) -> Obj:
        return (o.ref("SourceItem", source[0]).ref("SourceNode", source[1])
                .ref("TargetItem", target[0]).ref("TargetNode", target[1]))

    segments, segment_ends, contents = {}, {}, {}
    for oid in src.of_kind("pipe_segment"):
        attrs, sid = src.attributes[oid], src.xml_id(oid)
        size = attrs.get("nominal_size_mm")
        if size is not None and (not isinstance(size, int) or isinstance(size, bool)):
            raise Unsupported(f"{oid} has a nominal size {size!r} that is not a whole number of millimetres")
        first, last = end(src.start[oid], sid), end(src.end[oid], sid)
        segment_ends[oid] = (first[0], last[0])
        o = ends(Obj("Plant/Piping.PipingNetworkSegment", sid), first, last)
        o.comp("PersistentIdentifiers", identifier(OBJECT_CONTEXT, src.key(oid)))
        if oid in src.tags:
            o.data("SegmentNumber", string(src.tags[oid]))
        if size is not None:
            o.data("NominalDiameterNumericalValueRepresentation", string(size))
            o.data("NominalDiameterRepresentation", string(f"DN {size}"))
            o.data("NominalDiameterTypeRepresentation", string("DN"))
        segments[oid] = o
        contents[sid] = ([ends(Obj("Plant/Piping.Pipe", f"{sid}_Pipe"), first, last)], [])
    carriers = []
    for predicate, a, b in src.relations:
        if predicate != "connects_to":
            continue
        cid = f"Connection_{src.xml_id(a)}_{src.xml_id(b)}"
        first, last = end(a, src.xml_id(b)), end(b, src.xml_id(a))
        o = ends(Obj("Plant/Piping.PipingNetworkSegment", cid), first, last)
        carriers.append((a, b, o))
        contents[cid] = ([ends(Obj("Plant/Piping.DirectPipingConnection", f"{cid}_Direct"), first, last)], [])

    links = {}
    for predicate, out, into in src.relations:
        if predicate == "continues_to":
            links[out], links[into] = into, out
    items = {}
    for oid in sorted(src.objects, key=src.key):
        kind, attrs, xid = src.kind(oid), src.attributes[oid], src.xml_id(oid)
        if kind == "valve":
            cls = VALVE_CLASS.get(attrs.get("tag_type"))
            if cls is None:
                raise Unsupported(f"{oid} is a valve of tag type {attrs.get('tag_type')!r}, outside the supported subset")
            o = Obj(cls, xid)
            if oid in src.tags:
                o.data("PipingComponentNumber", string(src.tags[oid]))
        elif kind == "junction":
            if len(nodes_of.get(oid, [])) > 3:
                raise Unsupported(f"{oid} has more than three connection ends, so it cannot be a tee")
            o = Obj("Plant/Piping.PipeTee", xid)
        elif kind == "sheet_connector":
            if attrs.get("direction") not in CONNECTOR_CLASS:
                raise Unsupported(f"{oid} has direction {attrs.get('direction')!r}")
            o = Obj(CONNECTOR_CLASS[attrs["direction"]], xid)
            if "label" in attrs:
                o.data("PipeConnectorNumber", string(attrs["label"]))
            if oid in links:
                other = links[oid]
                if src.sheet[other] == src.sheet[oid]:
                    reference = Obj("Plant/Piping.PipeOffPageConnectorObjectReference", f"{xid}_Reference")
                    reference.ref("ReferencedConnector", src.xml_id(other))
                else:
                    if "label" not in src.attributes[other]:
                        raise Unsupported(f"{other} has no label, so {oid} cannot refer to it by number")
                    reference = (Obj("Plant/Piping.PipeOffPageConnectorReferenceByNumber", f"{xid}_Reference")
                                 .data("ReferencedConnectorNumber", string(src.attributes[other]["label"]))
                                 .data("ReferencedDrawingNumber", string(src.drawings[src.sheet[other]]["name"])))
                o.comp("ConnectorReference", reference)
        else:
            continue
        o.comp("PersistentIdentifiers", identifier(OBJECT_CONTEXT, src.key(oid)))
        o.comp("Nodes", *nodes_of.get(oid, []))
        items[xid] = o

    # An item goes into the lowest-key segment that ends at it, else the lowest that starts at it,
    # else the first ConnectorPair segment that touches it.
    owner = {}
    for xid in items:
        ending = [s for s in segment_ends if segment_ends[s][1] == xid]
        starting = [s for s in segment_ends if segment_ends[s][0] == xid]
        if ending or starting:
            owner[xid] = src.xml_id((ending or starting)[0])
        else:
            touching = [c.id for a, b, c in carriers if xid in (src.xml_id(a), src.xml_id(b))]
            if not touching:
                raise Unsupported(f"{xid} is connected to nothing")
            owner[xid] = touching[0]
    for xid, o in items.items():
        contents[owner[xid]][1].append(o)

    equipment, functions = {}, {}
    owned = {subject: target for predicate, subject, target in src.relations if predicate == "owned_by"}
    for oid in sorted(src.objects, key=src.key):
        kind, attrs, xid = src.kind(oid), src.attributes[oid], src.xml_id(oid)
        if kind == "equipment":
            cls = EQUIPMENT_CLASS.get(attrs.get("tag_type"))
            if cls is None:
                raise Unsupported(f"{oid} is equipment of tag type {attrs.get('tag_type')!r}, outside the supported subset")
            o = Obj(cls, xid).comp("PersistentIdentifiers", identifier(OBJECT_CONTEXT, src.key(oid)))
            if oid in src.tags:
                o.data("TagName", string(src.tags[oid]))
            o.data("TagNamePrefix", string(attrs["tag_type"]))
            if "tag_number" in attrs:
                o.data("TagNameSequenceNumber", string(attrs["tag_number"]))
            if "description" in attrs:
                o.data("EquipmentDescription", text_in_english(attrs["description"]))
            equipment[oid] = o
        elif kind == "instrument":
            letters = INSTRUMENT_LETTERS.get(attrs.get("tag_type"))
            if letters is None or "loop_number" not in attrs:
                raise Unsupported(f"{oid} is an instrument of tag type {attrs.get('tag_type')!r}, outside the supported subset")
            if src.tags.get(oid) != f"{attrs['tag_type']}-{attrs['loop_number']}":
                raise Unsupported(f"{oid} has tag {src.tags.get(oid)!r}, not its tag type and loop number")
            o = (Obj("Plant/Instrumentation.ProcessInstrumentationFunction", xid)
                 .comp("PersistentIdentifiers", identifier(OBJECT_CONTEXT, src.key(oid)))
                 .data("ProcessInstrumentationFunctionCategory", string(letters[0]))
                 .data("ProcessInstrumentationFunctions", string(letters[1]))
                 .data("ProcessInstrumentationFunctionNumber", string(attrs["loop_number"])))
            if oid in owned:
                nozzle = f"{src.xml_id(owned[oid])}_Nozzle_{xid}"
                nozzles_of.setdefault(owned[oid], []).append(Obj("Plant/ProcessEquipment.InstrumentNozzle", nozzle))
                o.comp("ProcessSignalGeneratingFunctions",
                       Obj("Plant/Instrumentation.ProcessSignalGeneratingFunction", f"{xid}_Sensing").ref("SensingLocation", nozzle))
            functions[oid] = o
    for oid, o in equipment.items():
        o.comp("Nozzles", *nozzles_of.get(oid, []))

    files = {}
    revision = records["source_revision"]
    for did in sorted(src.drawings, key=lambda d: src.drawings[d]["source_locator"].get("DrawingId", 0)):
        drawing = src.drawings[did]
        here = lambda oid: src.sheet[oid] == did  # noqa: E731
        systems: dict[tuple, list[Obj]] = {}
        system_of = {}
        for oid in src.of_kind("pipe_segment"):
            if here(oid):
                key = (src.attributes[oid].get("line_prefix", ""), src.attributes[oid].get("line_number", ""))
                systems.setdefault(key, []).append(segments[oid])
                system_of[src.xml_id(oid)] = key
        for a, b, o in carriers:
            if here(a):
                key = system_of.get(owner.get(src.xml_id(a)), min(systems) if systems else ("", ""))
                systems.setdefault(key, []).append(o)
        system_objects, system_ids = [], set()
        for (prefix, number), members in sorted(systems.items()):
            sid = re.sub(r"[^A-Za-z0-9_]", "_", f"PipingNetworkSystem_{prefix}_{number}")
            if sid in system_ids:
                raise Unsupported(f"two lines on {drawing['name']} give the same system id {sid}")
            system_ids.add(sid)
            o = Obj("Plant/Piping.PipingNetworkSystem", sid)
            if number != "":
                o.data("LineNumber", string(number))
            for member in members:
                connections, member_items = contents[member.id]
                member.comp("Connections", *connections).comp("Items", *member_items)
            system_objects.append(o.comp("Segments", *members))
        key = drawing["source_locator"]["DrawingId"]
        metadata = (Obj("Plant/Diagram.PlantMetaData", f"Drawing_{key}")
                    .comp("PersistentIdentifiers", identifier(DRAWING_CONTEXT, key))
                    .data("DrawingNumber", string(drawing["name"])).data("FileName", string(drawing["name"])))
        if drawing.get("revision") is not None:
            metadata.data("RevisionNumber", string(drawing["revision"]))
        plant = (Obj("Plant/PlantModel", f"PlantModel_{key}")
                 .comp("MetaData", metadata)
                 .comp("PipingNetworkSystems", *system_objects)
                 .comp("ProcessInstrumentationFunctions", *[o for oid, o in functions.items() if here(oid)])
                 .comp("TaggedPlantItems", *[o for oid, o in equipment.items() if here(oid)]))
        groups = [Obj("Core/Diagram.RepresentationGroup").ref("Represents", src.xml_id(oid))
                  for oid in sorted(src.objects, key=src.key) if here(oid)]
        diagram = (Obj("Core/Diagram.Diagram")
                   .data("BackgroundColor", aggregate("Core/Diagram.Color", B=value("Integer", 255),
                                                      G=value("Integer", 255), R=value("Integer", 255)))
                   .data("MaxX", value("Double", "420.0")).data("MaxY", value("Double", "297.0"))
                   .data("MinX", value("Double", "0.0")).data("MinY", value("Double", "0.0"))
                   .data("Name", string(drawing["name"]))
                   .ref("Represents", f"PlantModel_{key}")
                   .comp("Groups", *groups, ordered=True))
        model = (Obj("Core/EngineeringModel")
                 .comp("ConceptualModel", plant).comp("Diagram", diagram)
                 .data("ExportDateTime", value("DateTime", revision["recorded_at"]))
                 .data("OriginatingSystemName", string(GENERATOR[0]))
                 .data("OriginatingSystemVendorName", string(GENERATOR[1]))
                 .data("OriginatingSystemVersion", string(GENERATOR[2])))
        name = re.sub(r"[^A-Za-z0-9_]", "_", f"LIONG_{revision['revision_id']}_{key}")
        root = etree.Element("Model", name=name, uri=f"urn:liong:dexpi:{revision['revision_id']}:{drawing['name']}")
        etree.SubElement(root, "Import", prefix="Core", source=CORE_URI)
        etree.SubElement(root, "Import", prefix="Plant", source=PLANT_URI)
        root.append(model.xml())
        etree.indent(root, space="  ")
        files[f"{drawing['name']}.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8") + b"\n"
    for xid in [o.id for o in items.values()] + [o.id for o in equipment.values()] + [o.id for o in functions.values()]:
        if not ID_PATTERN.fullmatch(xid):
            raise Unsupported(f"{xid} is not a valid DEXPI id")
    files[SIDECAR] = sidecar(src, files)
    return files


def sidecar(src: Source, files: dict[str, bytes]) -> bytes:
    """What DEXPI cannot carry, keyed by the records' IDs, with each DEXPI file's SHA-256."""
    records = src.records
    tags = {t["object_id"]: {k: v for k, v in t.items() if k not in ("object_id", "tag_value")}
            for t in records["tag_assignments"]}
    objects = {}
    for o in records["objects"]:
        objects[o["object_id"]] = {"source_locator": o["source_locator"]}
        if o["object_id"] in tags:
            objects[o["object_id"]]["tag"] = tags[o["object_id"]]
    assertions = {}
    for a in records["assertions"]:
        entry = {k: v for k, v in a.items() if k != "assertion_id"}
        if a["predicate"] not in RELATIONS and a["predicate"] in CARRIED[src.kind(a["subject_id"])]:
            del entry["value_or_target"]
        assertions[a["assertion_id"]] = entry
    content = {
        "format": SIDECAR_FORMAT,
        "note": "A LIONG manifest beside the DEXPI files. It is not DEXPI.",
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
        "source_manifest": records["source_manifest"],
        "source_revision": records["source_revision"],
        "objects": dict(sorted(objects.items())),
        "assertions": dict(sorted(assertions.items())),
        "drawings": {d["artifact_id"]: {k: v for k, v in d.items() if k not in ("artifact_id", "name", "revision")}
                     for d in sorted(records["drawings"], key=lambda d: d["artifact_id"])},
        "appearances": {a["object_id"]: {k: v for k, v in a.items() if k not in ("object_id", "artifact_id")}
                        for a in sorted(records["appearances"], key=lambda a: a["object_id"])},
    }
    return (json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def write(files: dict[str, bytes], folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (folder / name).write_bytes(data)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    records = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    try:
        files = generate(records)
    except SourceError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    write(files, Path(argv[1]))
    print(f"Wrote {len(files) - 1} DEXPI files and {SIDECAR} to {argv[1]}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
