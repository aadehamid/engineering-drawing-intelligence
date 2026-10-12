"""The one source for figures the documents quote.

Usage:
  python3 scripts/liong_facts.py figures [--json]   every figure, the files read, and the commit
  python3 scripts/liong_facts.py check              fail if a registered claim or swept count disagrees,
                                                    or a decision record disagrees with its index
  python3 scripts/liong_facts.py find PATTERN       search the documents, matching across line breaks

Figures are computed from the R0 fixture tables and edge lists in LIONG-006 and the
workload table in LIONG-010. The tool reads files only; it never writes to the repository.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path("docs/LIONG-006-synthetic-data.md")
EVALUATION = Path("docs/LIONG-010-evaluation.md")
README = Path("README.md")
DECISIONS = Path("docs/decisions")
INDEX = Path("docs/LIONG-000-index.md")
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
STATE_PAIRS = ("r0", "r2", "scn010", "scn011")
FLOW = "FLOW"
ON_SHEET = "ON_SHEET"


class Edge(NamedTuple):
    kind: str
    source: str
    target: str


def number(text: str) -> int:
    text = text.strip().lower()
    return WORDS[text] if text in WORDS else int(text.replace(",", ""))


def section(text: str, start: str) -> str:
    """Return the text from a heading up to the next level-2 heading."""
    begin = text.index(start)
    end = text.find("\n## ", begin + len(start))
    return text[begin:] if end == -1 else text[begin:end]


def table_row(text: str, label: str) -> str:
    match = re.search(rf"^\| {re.escape(label)} \|.*$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"no table row labelled {label}")
    return match.group(0)


def code_blocks(text: str) -> list[str]:
    return re.findall(r"^```text\n(.*?)^```", text, re.MULTILINE | re.DOTALL)


def table_aliases(text: str, header: str) -> list[tuple[str, str]]:
    """Expand the alias column of the table under `header` into (alias, type) rows."""
    rows = []
    lines = text[text.index(header):].splitlines()[2:]
    for line in lines:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        for alias in re.split(r"\s*,\s*", cells[0]):
            rows.append((alias, cells[1]))
    return rows


def parse_edges(block: str, default: str | None = None) -> list[Edge]:
    """Read `A -> B` pairs; a `TYPE:` line sets the type for the pairs after it.

    Comma-separated sources expand into one edge per source.
    """
    edges: list[Edge] = []
    kind = default
    for line in block.splitlines():
        label = re.match(r"\s*([A-Z_]+):\s*(.*)$", line)
        if label:
            kind, line = label.group(1), label.group(2)
        for sources, target in re.findall(r"([\w,\s]+?)\s*->\s*(\w+)", line):
            for source in re.split(r"\s*,\s*", sources.strip()):
                edges.append(Edge(kind, source, target))
    return edges


def touches(edge: Edge, nodes: set[str]) -> bool:
    return edge.source in nodes or edge.target in nodes


def simple_paths(edges: list[Edge], start: str, goal: str) -> list[list[str]]:
    """Every simple directed path from start to goal, as node lists."""
    graph: dict[str, list[str]] = {}
    for edge in edges:
        graph.setdefault(edge.source, []).append(edge.target)

    def walk(path: list[str]) -> list[list[str]]:
        if path[-1] == goal:
            return [path]
        return [p for n in graph.get(path[-1], []) if n not in path for p in walk(path + [n])]

    return walk([start])


def compute(root: Path) -> dict[str, int]:
    fixtures = (root / FIXTURES).read_text(encoding="utf-8")
    evaluation = (root / EVALUATION).read_text(encoding="utf-8")

    baseline = section(fixtures, "## Exact baseline R0")
    aliases = table_aliases(baseline, "| Alias | Type |")
    nodes = {alias for alias, _ in aliases}
    drawings = {alias for alias, kind in aliases if kind.startswith("Drawing document")}
    objects = nodes - drawings
    flow_block, other_block = code_blocks(baseline)[:2]
    flow = parse_edges(flow_block, FLOW)
    r0_edges = flow + parse_edges(other_block)
    r0_paths = simple_paths(flow, "E1", "E2")
    export_nodes = {node for path in r0_paths for node in path}
    export_edges = [e for e in flow if e.source in export_nodes and e.target in export_nodes]

    deleted = set(re.search(r"delete (\w+) and (\w+);", table_row(fixtures, "R2")).groups())
    r2_nodes = nodes - deleted
    r2_edges = [e for e in r0_edges if not touches(e, deleted)]

    cut = re.search(r"evidence for `(\w+)→(\w+)`", table_row(fixtures, "SCN-010")).groups()
    scn010_edges = [e for e in r0_edges if (e.source, e.target) != cut]

    operational = section(fixtures, "## Operational fixture for SCN-011")
    context_nodes = table_aliases(operational, "| Alias | Type and payload |")
    accepted = re.search(r"The exact accepted edges are (.*?)\. ", operational).group(1)
    context_edges = re.findall(r"`(\w+) ([A-Z_]+) (\w+)`", accepted)

    worlds = number(re.search(r"(\d+) disjoint R0-sized worlds", evaluation).group(1))
    # LIONG-000 is the index; the substantive documents are LIONG-001 onward.
    substantive = [
        p for p in (root / "docs").glob("LIONG-0[0-9][0-9]-*.md") if not p.name.startswith("LIONG-000")
    ]

    return {
        "r0.nodes": len(nodes),
        "r0.engineering_objects": len(objects),
        "r0.drawings": len(drawings),
        "r0.flow_edges": len(flow),
        "r0.other_edges": len(r0_edges) - len(flow),
        "r0.on_sheet_edges": sum(1 for e in r0_edges if e.kind == ON_SHEET),
        "r0.instrument_parent_edges": sum(1 for e in r0_edges if e.kind == "INSTRUMENT_PARENT"),
        "r0.cross_sheet_edges": sum(1 for e in r0_edges if e.kind == "CROSS_SHEET_REFERENCE"),
        "r0.edges": len(r0_edges),
        "r0.e1_e2_paths": len(r0_paths),
        "r2.nodes": len(r2_nodes),
        "r2.edges": len(r2_edges),
        "r2.on_sheet_removed": sum(1 for e in r0_edges if e.kind == ON_SHEET and touches(e, deleted)),
        "r2.e1_e2_paths": len(simple_paths([e for e in r2_edges if e.kind == FLOW], "E1", "E2")),
        "scn012.export_nodes": len(export_nodes),
        "scn012.export_flow_edges": len(export_edges),
        "scn010.nodes": len(nodes),
        "scn010.edges": len(scn010_edges),
        "scn011.contextual_nodes": len(context_nodes),
        "scn011.contextual_edges": len(context_edges),
        "scn011.nodes": len(nodes) + len(context_nodes),
        "scn011.edges": len(r0_edges) + len(context_edges),
        "scaled.worlds": worlds,
        "scaled.sheets": worlds * len(drawings),
        "scaled.engineering_objects": worlds * len(objects),
        "scaled.nodes": worlds * len(nodes),
        "scaled.edges": worlds * len(r0_edges),
        "scaled.r2_nodes": worlds * len(r2_nodes),
        "scaled.r2_edges": worlds * len(r2_edges),
        "documents.substantive": len(substantive),
    }


# Each claim: the file, a pattern whose groups are figures, and the figure each group states.
# A claim that no longer matches is an error, so a reworded sentence cannot slip past.
CLAIMS: list[tuple[Path, str, tuple[str, ...]]] = [
    (FIXTURES, r"fixture contains (\d+) nodes: (\d+) engineering objects and (\w+) drawing documents",
     ("r0.nodes", "r0.engineering_objects", "r0.drawings")),
    (FIXTURES, r"These (\d+) edges express", ("r0.flow_edges",)),
    (FIXTURES, r"The other (\d+) edges are", ("r0.other_edges",)),
    (FIXTURES, r"baseline therefore contains (\d+) edges", ("r0.edges",)),
    (FIXTURES, r"\| Baseline above \| (\d+) nodes, (\d+) edges", ("r0.nodes", "r0.edges")),
    (FIXTURES, r"equals the (\d+)-node/(\d+)-edge R0 set", ("r0.nodes", "r0.edges")),
    (FIXTURES, r"Same (\d+) identities and (\d+) edges", ("r0.nodes", "r0.edges")),
    (FIXTURES, r"their (\w+) `ON_SHEET` edges", ("r2.on_sheet_removed",)),
    (FIXTURES, r"\| (\d+) nodes, (\d+) edges\. No bypass", ("r2.nodes", "r2.edges")),
    (FIXTURES, r"R0 has exactly (\w+) simple directed E1-to-E2 paths", ("r0.e1_e2_paths",)),
    (FIXTURES, r"R2 has exactly (\w+) path", ("r2.e1_e2_paths",)),
    (FIXTURES, r"has (\d+) nodes and (\d+) edges after removing", ("scn010.nodes", "scn010.edges")),
    (FIXTURES, r"Exactly (\w+) contextual nodes and (\w+) accepted contextual edges",
     ("scn011.contextual_nodes", "scn011.contextual_edges")),
    (FIXTURES, r"exactly these (\w+) contextual nodes", ("scn011.contextual_nodes",)),
    (FIXTURES, r"comparison view has (\d+) nodes and (\d+) edges", ("scn011.nodes", "scn011.edges")),
    (FIXTURES, r"current state has (\d+) nodes, (\d+) edges, and tag", ("r0.nodes", "r0.edges")),
    (FIXTURES, r"and all (\d+) FLOW edges, with identifiers", ("scn012.export_flow_edges",)),
    (EVALUATION, r"(\d+) nodes and (\d+) edges, not merely", ("r0.nodes", "r0.edges")),
    (EVALUATION, r"(\w+)-node/(\w+)-edge contextual diff", ("scn011.contextual_nodes", "scn011.contextual_edges")),
    (EVALUATION, r"entity recall has (\d+) expected nodes", ("r0.nodes",)),
    (EVALUATION, r"edge recall has (\d+) expected edges", ("r0.edges",)),
    (EVALUATION, r"node recall with denominator (\d+) as", ("r0.engineering_objects",)),
    (EVALUATION,
     r"FLOW recall with denominator (\d+), ON_SHEET with (\d+), INSTRUMENT_PARENT with (\d+), "
     r"and CROSS_SHEET_REFERENCE with (\d+)",
     ("r0.flow_edges", "r0.on_sheet_edges", "r0.instrument_parent_edges", "r0.cross_sheet_edges")),
    (EVALUATION, r"\| Selection manifest, (\d+) engineering nodes and (\d+) FLOW edges",
     ("scn012.export_nodes", "scn012.export_flow_edges")),
    (EVALUATION, r"contains (\d+) engineering nodes, excluding I1, plus all (\d+) FLOW edges",
     ("scn012.export_nodes", "scn012.export_flow_edges")),
    (EVALUATION, r"(\d+) engineering objects, (\d+) total comparison nodes, (\d+) edges \|",
     ("r0.engineering_objects", "r0.nodes", "r0.edges")),
    (EVALUATION,
     r"(\d+) disjoint R0-sized worlds: ([\d,]+) sheets, ([\d,]+) engineering objects, "
     r"([\d,]+) total comparison nodes, ([\d,]+) edges",
     ("scaled.worlds", "scaled.sheets", "scaled.engineering_objects", "scaled.nodes", "scaled.edges")),
    (EVALUATION, r"comparison total is ([\d,]+) nodes and ([\d,]+) edges",
     ("scaled.r2_nodes", "scaled.r2_edges")),
    (README, r"(\w+) draft documents", ("documents.substantive",)),
    (INDEX, r"All (\w+) substantive documents", ("documents.substantive",)),
]

# In these files, any `nodes/edges` shorthand such as `17/31` must name a known graph state.
# Every number in a sentence that mentions nodes or edges, in digits or words, must sit inside
# a registered claim or an exempt phrase. A figure sentence nobody registered therefore fails,
# whatever its spelling.
SWEPT_FILES = (FIXTURES, EVALUATION)
PAIR = r"(?<![\w/-])(\d+)/(\d+)(?![\d/])"
_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
         "fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety hundred thousand".split()
# A number may be joined to "node" or "edge" by a hyphen ("17-node/31-edge"); a slash before a
# number counts as a boundary only after a letter, so ID ranges such as 009/010 stay skipped.
NUMBER = (rf"(?<![\w.-])(?<!\d/)(?:\d[\d,]*(?:\.\d+)?|(?:{'|'.join(_ONES + _TENS)})"
          rf"(?:-(?:{'|'.join(_ONES)}))?)(?![\w/]|-(?!(?:node|edge)s?\b))")
SENTENCE = r"(?:[^.|!?]|(?<=\d)\.(?=\d))+"
# Numbers near "nodes" or "edges" that are not node or edge figures.
EXEMPT: list[tuple[Path, str]] = [
    (FIXTURES, "expand into one edge per source"),
    (EVALUATION, "One two-sheet R0 world"),
    (EVALUATION, "equal 1.0"),
]


def flat(text: str) -> str:
    """Join wrapped lines so a claim split across lines still matches."""
    return re.sub(r"\s+", " ", text)


def check(root: Path) -> list[str]:
    figures = compute(root)
    names = {name for name, _, _ in CLAIMS} | set(SWEPT_FILES)
    texts = {name: flat((root / name).read_text(encoding="utf-8")) for name in names}
    errors: list[str] = []
    for name, pattern, keys in CLAIMS:
        matches = list(re.finditer(pattern, texts[name]))
        if not matches:
            errors.append(f"{name}: claim not found: {pattern}")
        for match in matches:
            for key, stated in zip(keys, match.groups()):
                if number(stated) != figures[key]:
                    errors.append(f"{name}: states {stated} for {key}; the fixture gives {figures[key]}")
    pairs = {(figures[f"{s}.nodes"], figures[f"{s}.edges"]) for s in STATE_PAIRS}
    for name in SWEPT_FILES:
        for nodes, edges in re.findall(PAIR, texts[name]):
            if (int(nodes), int(edges)) not in pairs:
                errors.append(f"{name}: {nodes}/{edges} matches no known graph state")
        covered = [m.span() for n, pattern, _ in CLAIMS if n == name for m in re.finditer(pattern, texts[name])]
        covered += [m.span() for n, phrase in EXEMPT if n == name for m in re.finditer(re.escape(phrase), texts[name])]
        for sentence in re.finditer(SENTENCE, texts[name]):
            if not re.search(r"\b(?:nodes?|edges?)\b", sentence.group(0), re.IGNORECASE):
                continue
            for found in re.finditer(NUMBER, sentence.group(0), re.IGNORECASE):
                start, end = sentence.start() + found.start(), sentence.start() + found.end()
                if not any(a <= start and end <= b for a, b in covered):
                    errors.append(f"{name}: unregistered figure: {found.group(0)} in \"{sentence.group(0).strip()[:80]}\"")
    return errors


RECORD_SECTIONS = ("## Context", "## Decision", "## Alternatives considered", "## Owner's words", "## Evidence")
STATUSES = ("Proposed", "Decided", "Superseded")
INDEX_ROW = r"^\| \[(DEC-\d{3})\]\(([^)]+)\) \| (.+?) \| (\w+) \| (\d{4}-\d{2}-\d{2}) \|$"


class IndexRow(NamedTuple):
    link: str
    title: str
    status: str
    date: str


INDEX_HEADER = ("| ID | Decision | Status | Date |", "| --- | --- | --- | --- |")


class Record(NamedTuple):
    record_id: str
    title: str
    statuses: list[str]
    dates: list[str]
    sections: list[tuple[str, str]]
    amends: list[str]
    superseded_by: list[str]


def rendered(text: str) -> str:
    """The text a reader sees outside code: HTML comments and fenced code blocks removed.

    One pass tracks both, so a comment marker inside code and a fence inside a comment
    are left alone. A fence closes only on the same character repeated at least as
    many times; an unclosed fence or comment runs to the end of the document.
    """
    kept: list[str] = []
    fence = None
    in_comment = False
    for line in text.splitlines():
        if fence is not None:
            marker = re.match(r" {0,3}(`{3,}|~{3,})\s*$", line)
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        visible = ""
        rest = line
        while rest:
            if in_comment:
                end = rest.find("-->")
                if end == -1:
                    rest = ""
                else:
                    in_comment, rest = False, rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start == -1:
                    visible, rest = visible + rest, ""
                else:
                    visible, in_comment, rest = visible + rest[:start], True, rest[start + 4:]
        if in_comment and not visible.strip():
            continue
        opening = re.match(r" {0,3}(`{3,}|~{3,})", visible)
        if opening:
            fence = opening.group(1)
            continue
        kept.append(visible)
    return "\n".join(kept) + "\n"


INVISIBLE_LINE = (
    r" {0,3}#{1,6}(\s.*)?"                 # a heading
    r"| {0,3}([-*_])(\s*\2){2,}\s*"          # a horizontal rule
    r"| {0,3}\[[^\]]+\]:\s*\S.*"            # a link reference definition, which renders nothing
    r"|\s*(</?[A-Za-z][\w-]*(\s[^>]*)?/?>\s*)+"  # only HTML tags (an autolink such as <https://...> is text)
)


def has_content(body: str) -> bool:
    """True when some line renders text a reader sees, beyond headings, rules, and markup."""
    return any(line.strip() and not re.fullmatch(INVISIBLE_LINE, line) for line in body.splitlines())


def owner_answer_is_visible(body: str) -> bool:
    """The quote block after 'The owner answered:' (or said/wrote) renders some text."""
    answer = re.search(r"^The owner (?:answered|said|wrote):\n+((?:>.*\n?)+)", body, re.MULTILINE)
    if not answer:
        return False
    quoted = "\n".join(re.sub(r"^> ?", "", line) for line in answer.group(1).splitlines())
    return has_content(quoted)


def parse_record(text: str) -> Record | None:
    text = rendered(text)
    heading = re.match(r"\s*# (DEC-\d{3}): (.+)\n", text)
    if not heading:
        return None
    sections: list[tuple[str, str]] = []
    for line in text.splitlines():
        if re.match(r"## \S", line):
            sections.append((line.strip(), ""))
        elif sections:
            title_line, body = sections[-1]
            sections[-1] = (title_line, body + line + "\n")
    return Record(
        heading.group(1),
        heading.group(2),
        re.findall(r"^Status: (\w+)$", text, re.MULTILINE),
        re.findall(r"^Date: (\d{4}-\d{2}-\d{2})$", text, re.MULTILINE),
        sections,
        re.findall(r"^Amends (DEC-\d{3})\b", text, re.MULTILINE),
        re.findall(r"^Superseded by (DEC-\d{3}) on \d{4}-\d{2}-\d{2}\.?$", text, re.MULTILINE),
    )


def read_index(text: str, label: str, errors: list[str]) -> list[tuple[str, IndexRow]]:
    """Every table row a reader sees in the Index: the exact header, then well-formed entries."""
    lines = [line.strip() for line in section(rendered(text), "## Index").splitlines() if re.match(r" {0,3}\|", line)]
    if tuple(lines[:2]) != INDEX_HEADER:
        errors.append(f"{label}: the Index table must start with {INDEX_HEADER[0]}")
    rows = []
    for line in lines[2:]:
        row = re.match(INDEX_ROW, line)
        if not row:
            errors.append(f"{label}: malformed index row: {line}")
            continue
        record_id, link, title, status, date = row.groups()
        rows.append((record_id, IndexRow(link, title, status, date)))
    return rows


def check_record(record: Record, label: str, records: dict[str, Record]) -> list[str]:
    """One status and date, non-empty sections in order, the owner's answer, and two-way amendments."""
    errors: list[str] = []
    if len(record.statuses) != 1 or record.statuses[0] not in STATUSES:
        errors.append(f"{label}: needs exactly one Status line, one of {', '.join(STATUSES)}")
    if len(record.dates) != 1:
        errors.append(f"{label}: needs exactly one 'Date: YYYY-MM-DD' line")
    if [h for h, _ in record.sections if h in RECORD_SECTIONS] != list(RECORD_SECTIONS):
        errors.append(f"{label}: needs sections {', '.join(RECORD_SECTIONS)}, each once, in that order")
        return errors
    bodies = {h: body for h, body in record.sections if h in RECORD_SECTIONS}
    for heading in RECORD_SECTIONS:
        if not has_content(bodies[heading]):
            errors.append(f"{label}: section {heading} is empty")
    status = record.statuses[0] if record.statuses else None
    if status == "Decided" and not owner_answer_is_visible(bodies["## Owner's words"]):
        errors.append(f"{label}: a Decided record quotes the owner after 'The owner answered:' in a '>' block")
    if status == "Superseded":
        if len(record.superseded_by) != 1:
            errors.append(f"{label}: a Superseded record says 'Superseded by DEC-NNN on YYYY-MM-DD'")
        elif record.superseded_by[0] not in records:
            errors.append(f"{label}: successor {record.superseded_by[0]} has no record")
        elif record.record_id not in records[record.superseded_by[0]].amends:
            errors.append(f"{label}: successor {record.superseded_by[0]} does not say 'Amends {record.record_id}'")
    for earlier in record.amends:
        target = records.get(earlier)
        if not target:
            errors.append(f"{label}: amends {earlier}, which has no record")
        elif target.statuses != ["Superseded"] or target.superseded_by != [record.record_id]:
            errors.append(f"{label}: amends {earlier}, which is not marked 'Superseded by {record.record_id} on YYYY-MM-DD'")
    return errors


def check_decisions(root: Path) -> list[str]:
    """Each decision record has the documented shape and matches its index row."""
    folder = root / DECISIONS
    index_label = f"{DECISIONS}/README.md"
    errors: list[str] = []
    files = {path.name: path for path in folder.glob("DEC-*.md")}
    records: dict[str, Record] = {}
    names: dict[str, str] = {}
    for name, path in sorted(files.items()):
        record = parse_record(path.read_text(encoding="utf-8"))
        if not record or not name.startswith(record.record_id + "-"):
            errors.append(f"{DECISIONS}/{name}: first line must be '# DEC-NNN: <decision>' matching the file name")
            continue
        if record.record_id in records:
            errors.append(f"{DECISIONS}/{name}: {record.record_id} is already used by {names[record.record_id]}")
            continue
        records[record.record_id] = record
        names[record.record_id] = name

    rows = read_index((folder / "README.md").read_text(encoding="utf-8"), index_label, errors)
    seen: set[str] = set()
    for record_id, row in rows:
        if record_id in seen:
            errors.append(f"{index_label}: {record_id} is indexed twice")
        seen.add(record_id)
        if row.link not in files:
            errors.append(f"{index_label}: {record_id} links to missing file {row.link}")
            continue
        if names.get(record_id) != row.link:
            errors.append(f"{index_label}: {record_id} links to {row.link}, which is not the {record_id} record")
            continue
        record = records[record_id]
        if row.title != record.title:
            errors.append(f"{index_label}: {record_id} title differs from its record")
        if record.statuses and row.status != record.statuses[0]:
            errors.append(f"{index_label}: {record_id} status {row.status}; the record says {record.statuses[0]}")
        if record.dates and row.date != record.dates[0]:
            errors.append(f"{index_label}: {record_id} date {row.date}; the record says {record.dates[0]}")

    for record_id, record in sorted(records.items()):
        label = f"{DECISIONS}/{names[record_id]}"
        errors += check_record(record, label, records)
        if record_id not in seen:
            errors.append(f"{label}: {record_id} has no index row")
    return errors


def find(root: Path, pattern: str) -> list[str]:
    """Search documents; spaces in the pattern also match line breaks."""
    regex = re.compile(r"\s+".join(map(re.escape, pattern.split())), re.IGNORECASE)
    results = []
    for path in sorted([*root.glob("*.md"), *(root / "docs").glob("*.md")]):
        text = path.read_text(encoding="utf-8")
        for match in regex.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            results.append(f"{path.relative_to(root)}:{line}: {flat(match.group(0))}")
    return results


def commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True
        )
    except FileNotFoundError:
        return "unknown"
    return result.stdout.strip() or "unknown"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    figures_command = commands.add_parser("figures")
    figures_command.add_argument("--json", action="store_true")
    commands.add_parser("check")
    find_command = commands.add_parser("find")
    find_command.add_argument("pattern")
    args = parser.parse_args(argv)

    if args.command == "figures":
        figures = compute(ROOT)
        files = [str(FIXTURES), str(EVALUATION), "docs/LIONG-0*.md"]
        if args.json:
            print(json.dumps({"commit": commit(ROOT), "files": files, "figures": figures}, indent=2))
        else:
            print(f"Read {', '.join(files)} at commit {commit(ROOT)}")
            for key, value in figures.items():
                print(f"{key} = {value}")
        return 0
    elif args.command == "check":
        errors = check(ROOT) + check_decisions(ROOT)
        summary = f"Figures match the fixtures in {len(CLAIMS)} claims; decision records match their index."
        print("\n".join(errors) if errors else summary)
        return 1 if errors else 0
    else:
        results = find(ROOT, args.pattern)
        print("\n".join(results) if results else "No matches.")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
