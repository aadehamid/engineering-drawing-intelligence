#!/usr/bin/env python3
"""Validate DEXPI 2.0.1 output in DEC-064's four stages, in order, then round-trip it.

Usage:
  dexpi_validate.py FOLDER   a folder that dexpi_generate.py wrote: DEXPI files and sidecar.json

The stages stop at the first one that fails, and every failure names its stage.
1. schema: each file validates against the pinned XSD in standards/dexpi/2.0.1. The XSD
   is read with only its own internal entities resolved, which its patterns need; a
   DEXPI file is read with no entity resolution and no network, and may not have a DTD.
2. references: every Import maps to a pinned model through dexpi_pins.local_path, every
   "#id" reference resolves in its file, and every class, enumeration literal and named
   reference a file names exists in the pinned Core and Plant models.
3. model: every class is concrete; every property is declared on the class or a
   supertype, with the right kind and a value of an allowed type; every property has an
   allowed number of values, and no object is referenced more often than a reference
   property's opposite bound allows; a named reference is checked by the class it names.
   The models' documentation annotations are ignored.
4. liong_rules: only classes of the supported subset, in the shapes the parser reads, and
   no named references; unique tags; a sidecar entry for every node, drawing, appearance and relationship;
   and an ExportDateTime equal to the source revision's recorded time.
After all four pass, the round trip parses the folder, generates it again, and requires
identical bytes for every file.

The claim names only the stages that passed (DEC-065, DEC-072). It never says
conformant or certified.
"""
from __future__ import annotations

from collections import Counter
from functools import cache
from pathlib import Path
import sys

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dexpi_generate as gen  # noqa: E402
import dexpi_parse as parse  # noqa: E402
import dexpi_pins as pins  # noqa: E402

STAGES = ("schema", "references", "model", "liong_rules")
CLAIMS = {
    "schema": "the DEXPI 2.0.1 XSD",
    "references": "its reference checks",
    "model": "the 2.0.1 Core and Plant models for the classes LIONG uses",
}
TYPE_DEFINITIONS = ("ConcreteClass", "AbstractClass", "Enumeration", "AggregatedDataType", "AbstractDataType")
PRIMITIVES = {"String": {"Builtin/String", "Builtin/AnyURI"}, "Integer": {"Builtin/Integer", "Builtin/UnsignedByte"},
              "Double": {"Builtin/Double"}, "Boolean": {"Builtin/Boolean"}, "DateTime": {"Builtin/DateTime"},
              "Undefined": {"Builtin/Undefined"}}


class Models:
    """The classes, data types and enumerations of the pinned Core and Plant models."""

    def __init__(self, pin_dir: Path = pins.PIN_DIR):
        self.types: dict[str, dict] = {}
        self.names: dict[str, str] = {}  # import URI -> model name
        for uri, path in pins.import_table(pin_dir).items():
            root = parse.parse_xml(path).getroot()
            self.names[uri] = root.get("name")
            self._walk(root.get("name"), root, "")

    def _walk(self, model: str, element: etree._Element, prefix: str) -> None:
        qualify = lambda ref: model + ref if ref.startswith("/") else ref  # noqa: E731
        for child in element:
            if child.tag == "Package":
                self._walk(model, child, prefix + child.get("name") + ".")
            elif child.tag in TYPE_DEFINITIONS:
                props = {}
                for p in child:
                    if isinstance(p.tag, str) and p.tag.endswith("Property"):
                        upper = p.get("upper")
                        props[p.get("name")] = {
                            "kind": p.tag[:-len("Property")], "lower": int(p.get("lower") or 0),
                            "upper": None if upper in (None, "", "*") else int(upper),
                            "opposite_upper": None if p.get("oppositeUpper") in (None, "", "*") else int(p.get("oppositeUpper")),
                            "types": [qualify(r.get("type")) for r in p.iter("ClassReference", "DataTypeReference")],
                        }
                self.types[f"{model}/{prefix}{child.get('name')}"] = {
                    "kind": child.tag, "props": props,
                    "supers": [qualify(s) for s in (child.get("superTypes") or "").split()],
                    "literals": {lit.get("name") for lit in child.iter("EnumerationLiteral")},
                }

    def ancestors(self, name: str) -> list[str]:
        found, todo = [], [name]
        while todo:
            current = todo.pop(0)
            if current not in found:
                found.append(current)
                todo += self.types.get(current, {}).get("supers", [])
        return found

    def properties(self, name: str) -> dict[str, dict]:
        props = {}
        for ancestor in reversed(self.ancestors(name)):
            for prop, spec in self.types.get(ancestor, {}).get("props", {}).items():
                props[prop] = spec | {"owner": ancestor}
        return props

    def is_a(self, name: str, other: str) -> bool:
        return other in self.ancestors(name)


@cache
def models() -> Models:
    return Models()


@cache
def schema() -> etree.XMLSchema:
    xsd = pins.PIN_DIR / "DEXPI_XML_Schema.xsd"
    # The XSD builds its patterns from its own internal entities, so only those are resolved.
    return etree.XMLSchema(etree.parse(str(xsd), etree.XMLParser(resolve_entities="internal", no_network=True)))


def check_schema(path: Path) -> list[str]:
    try:
        doc = parse.parse_xml(path)
    except etree.XMLSyntaxError as error:
        return [f"{path.name}: not well-formed XML: {error}"]
    if doc.docinfo.doctype or doc.docinfo.internalDTD is not None:
        return [f"{path.name}: has a document type declaration, which DEXPI files do not use"]
    xsd = schema()
    if xsd.validate(doc):
        return []
    return [f"{path.name} line {e.line}: {e.message}" for e in xsd.error_log]


def resolver(root: etree._Element):
    """A function from a prefixed name, such as Plant/Piping.Pipe, to the model's full name."""
    prefixes = {i.get("prefix"): models().names.get(i.get("source")) for i in root.findall("Import")}

    def resolve(name: str | None) -> str | None:
        prefix, slash, rest = (name or "").partition("/")
        return f"{prefixes[prefix]}/{rest}" if slash and prefixes.get(prefix) else None
    return resolve


def check_references(path: Path) -> list[str]:
    root = parse.parse_xml(path).getroot()
    problems = []
    for imported in root.findall("Import"):
        try:
            pins.local_path(imported.get("source"))
        except pins.UnpinnedImport as error:
            problems.append(f"{path.name}: import {imported.get('prefix')}: {error}")
    resolve, m = resolver(root), models()
    ids = {o.get("id") for o in root.iter("Object") if o.get("id")}
    for element in root.iter("Object", "AggregatedDataValue"):
        if resolve(element.get("type")) not in m.types:
            problems.append(f"{path.name} line {element.sourceline}: type {element.get('type')} is not in the pinned models")
    for element in root.iter("DataReference"):
        full = resolve(element.get("data")) or ""
        enumeration, _, literal = full.rpartition(".")
        if literal not in m.types.get(enumeration, {}).get("literals", ()):
            problems.append(f"{path.name} line {element.sourceline}: literal {element.get('data')} is not in the pinned models")
    for element in root.iter("References", "ObjectReference"):
        for target in (element.get("objects") or element.get("object") or "").split():
            if not target.startswith("#"):
                full = resolve(target) or ""
                enumeration, _, literal = full.rpartition(".")
                if full not in m.types and literal not in m.types.get(enumeration, {}).get("literals", ()):
                    problems.append(f"{path.name} line {element.sourceline}: {target} does not resolve in the pinned models")
            elif target[1:] not in ids:
                problems.append(f"{path.name} line {element.sourceline}: {target} does not resolve")
    return problems


def check_model(path: Path) -> list[str]:
    root = parse.parse_xml(path).getroot()
    resolve, m = resolver(root), models()
    byid = {o.get("id"): o for o in root.iter("Object") if o.get("id")}
    problems, referrers = [], Counter()
    for o in root.iter("Object"):
        cls = resolve(o.get("type"))
        where = f"{path.name} line {o.sourceline}"
        if m.types[cls]["kind"] != "ConcreteClass":
            problems.append(f"{where}: {cls} is not a concrete class")
        props, counts = m.properties(cls), Counter()
        for child in o:
            if not isinstance(child.tag, str):
                continue
            name = child.get("property")
            spec = props.get(name)
            kind = {"Components": "Composition", "References": "Reference", "Data": "Data"}[child.tag]
            if spec is None:
                problems.append(f"{where}: {cls} declares no property {name}")
                continue
            if spec["kind"] != kind:
                problems.append(f"{where}: {cls}.{name} is a {spec['kind']} property, written as {child.tag}")
                continue
            if kind == "Composition":
                values = list(child)
                for v in values:
                    if not any(m.is_a(resolve(v.get("type")), t) for t in spec["types"]):
                        problems.append(f"{where}: {cls}.{name} holds a {resolve(v.get('type'))}")
            elif kind == "Reference":
                values = child.get("objects").split()
                for v in values:
                    if v.startswith("#"):
                        target = resolve(byid[v[1:]].get("type"))
                    else:  # a named reference, which stage 2 resolved to a class or a literal
                        named = resolve(v)
                        target = named if named in m.types else named.rpartition(".")[0]
                    if not any(m.is_a(target, t) for t in spec["types"]):
                        problems.append(f"{where}: {cls}.{name} refers to a {target}")
                    referrers[(spec["owner"], name, v)] += 1
            else:
                values = list(child)
                problems += check_value(values, spec, f"{where}: {cls}.{name}", resolve, m, spec["types"])
            counts[name] += len(values)
        for name, spec in props.items():
            if not spec["lower"] <= counts[name] <= (spec["upper"] if spec["upper"] is not None else counts[name]):
                bound = spec["upper"] if spec["upper"] is not None else "*"
                problems.append(f"{where}: {cls}.{name} has {counts[name]} values, allowed {spec['lower']}..{bound}")
    for (owner, name, target), count in sorted(referrers.items()):
        limit = m.types[owner]["props"][name]["opposite_upper"]
        if limit is not None and count > limit:
            problems.append(f"{path.name}: {target} is the {owner}.{name} of {count} objects, at most {limit} allowed")
    return problems


def check_value(values: list, spec: dict, where: str, resolve, m: Models, bound: list[str]) -> list[str]:
    """Problems with data values. `bound` is what a type parameter such as PhysicalQuantity.UnitType stands for."""
    problems = []
    types = set()
    for t in spec["types"]:
        types |= set(bound) if t not in m.types and not t.startswith("Builtin/") else {t}
    for v in values:
        if v.tag in PRIMITIVES:
            if not PRIMITIVES[v.tag] & types:
                problems.append(f"{where} holds a {v.tag}")
            elif v.tag == "Integer" and "Builtin/UnsignedByte" in types and not 0 <= int(v.text) <= 255:
                problems.append(f"{where} holds {v.text}, not an unsigned byte")
        elif v.tag == "DataReference":
            enumeration = (resolve(v.get("data")) or "").rpartition(".")[0]
            if not any(m.is_a(enumeration, t) for t in types):
                problems.append(f"{where} holds a literal of {enumeration}")
        elif v.tag == "AggregatedDataValue":
            aggregate = resolve(v.get("type"))
            if not any(m.is_a(aggregate, t) for t in types):
                problems.append(f"{where} holds a {aggregate}")
                continue
            fields, counts = m.properties(aggregate), Counter()
            for field in v.findall("Data"):
                fspec = fields.get(field.get("property"))
                if fspec is None:
                    problems.append(f"{where}: {aggregate} has no field {field.get('property')}")
                    continue
                problems += check_value(list(field), fspec, f"{where}.{field.get('property')}", resolve, m, spec["types"])
                counts[field.get("property")] += len(field)
            for name, fspec in fields.items():
                if not fspec["lower"] <= counts[name] <= (fspec["upper"] if fspec["upper"] is not None else counts[name]):
                    problems.append(f"{where}: {aggregate}.{name} has {counts[name]} values")
    return problems


def check_liong_rules(folder: Path) -> list[str]:
    facts, sidecar = parse.read(folder), parse.load_sidecar(folder)
    problems = [f"{cls}: {count} objects outside the supported subset" for cls, count in sorted(facts["unsupported"].items())]
    problems += facts["problems"]
    for path in parse.dexpi_files(folder):
        for element in parse.parse_xml(path).getroot().iter("References", "ObjectReference"):
            for target in (element.get("objects") or element.get("object") or "").split():
                if not target.startswith("#"):
                    problems.append(f"{path.name} line {element.sourceline}: {target} is a named reference, "
                                    "outside the supported subset")
    tags = Counter(n["tag"] for n in facts["nodes"].values() if n.get("tag"))
    problems += [f"tag {tag} is on {count} nodes" for tag, count in sorted(tags.items()) if count > 1]
    if sidecar is None or sidecar.get("format") != gen.SIDECAR_FORMAT:
        return problems + [f"{gen.SIDECAR} is missing or not in format {gen.SIDECAR_FORMAT}"]
    problems += [f"{node} has no sidecar entry" for node in sorted(facts["nodes"]) if node not in sidecar["objects"]]
    problems += [f"{d} has no sidecar entry" for d in sorted(facts["drawings"]) if d not in sidecar["drawings"]]
    problems += [f"{node}'s appearance has no sidecar entry" for node, _ in facts["appearances"]
                 if node not in sidecar["appearances"]]
    known = parse.relation_index(sidecar)
    problems += [f"{p} {s} {t} has no sidecar entry" for p, s, t in facts["relations"] if (p, s, t) not in known]
    recorded = sidecar["source_revision"]["recorded_at"]
    problems += [f"{name}: ExportDateTime {at} is not the source's recorded time {recorded}"
                 for name, at in sorted(facts["exported"].items()) if at != recorded]
    return problems


def round_trip(folder: Path) -> list[str]:
    """Parse the folder, generate it again, and name every file whose bytes differ."""
    facts, sidecar = parse.read(folder), parse.load_sidecar(folder)
    again = gen.generate(parse.records(facts, sidecar))
    present = {p.name for p in folder.iterdir() if p.is_file()}
    problems = [f"{name} is not generated again" for name in sorted(present - set(again))]
    problems += [f"{name} is generated but not present" for name in sorted(set(again) - present)]
    problems += [f"{name} differs when generated again" for name in sorted(present & set(again))
                 if (folder / name).read_bytes() != again[name]]
    return problems


def validate(folder: Path) -> dict:
    """{"passed": [...stage], "failed": stage or None, "problems": [...], "round_trip": [...] or None}."""
    files = parse.dexpi_files(folder)
    result = {"passed": [], "failed": None, "problems": [], "round_trip": None}
    checks = {"schema": check_schema, "references": check_references, "model": check_model}
    for stage in STAGES:
        if stage == "liong_rules":
            problems = check_liong_rules(folder)
        else:
            problems = [p for f in files for p in checks[stage](f)] if files else [f"{folder} holds no DEXPI file"]
        if problems:
            result.update(failed=stage, problems=[f"{stage}: {p}" for p in problems])
            return result
        result["passed"].append(stage)
    result["round_trip"] = round_trip(folder)
    return result


def claim(result: dict) -> str:
    """The claim the result supports, naming only the stages that passed."""
    passed = [CLAIMS[s] for s in result["passed"] if s in CLAIMS]
    if result["failed"] is None:
        text = f"Valid against {', '.join(passed[:-1])} and {passed[-1]}, and passes LIONG's rules."
        if result["round_trip"] == []:
            text += " Generating it again gives identical bytes."
        elif result["round_trip"]:
            text = text[:-1] + "; fails the round trip, so it is not valid under DEC-064."
        return text
    if not passed:
        return f"Fails the {result['failed']} stage; no stage passed."
    joined = passed[0] if len(passed) == 1 else f"{', '.join(passed[:-1])} and {passed[-1]}"
    return f"Valid against {joined}; fails the {result['failed']} stage."


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    result = validate(Path(argv[0]))
    for problem in result["problems"] + [f"round_trip: {p}" for p in result["round_trip"] or []]:
        print(problem, file=sys.stderr)
    print(claim(result))
    return 0 if result["failed"] is None and result["round_trip"] == [] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
