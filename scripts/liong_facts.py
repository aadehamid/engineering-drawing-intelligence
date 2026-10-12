"""The one source for figures the documents quote.

Usage:
  python3 scripts/liong_facts.py figures [--json]   every figure and the files it came from
  python3 scripts/liong_facts.py check              fail if a document states a different figure
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

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path("docs/LIONG-006-synthetic-data.md")
EVALUATION = Path("docs/LIONG-010-evaluation.md")
WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
STATE_PAIRS = ("r0", "r2", "scn010", "scn011")

Edge = tuple[str, str, str]


def number(text: str) -> int:
    text = text.strip().lower()
    return WORDS[text] if text in WORDS else int(text.replace(",", ""))


def section(text: str, start: str) -> str:
    """Return the text from a heading or sentence up to the next level-2 heading."""
    begin = text.index(start)
    end = text.find("\n## ", begin + len(start))
    return text[begin:] if end == -1 else text[begin:end]


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
                edges.append((kind, source, target))
    return edges


def simple_paths(edges: list[Edge], start: str, goal: str) -> int:
    graph: dict[str, list[str]] = {}
    for _, source, target in edges:
        graph.setdefault(source, []).append(target)

    def walk(node: str, seen: frozenset[str]) -> int:
        if node == goal:
            return 1
        return sum(walk(n, seen | {n}) for n in graph.get(node, []) if n not in seen)

    return walk(start, frozenset({start}))


def compute(root: Path) -> dict[str, int]:
    fixtures = (root / FIXTURES).read_text(encoding="utf-8")
    evaluation = (root / EVALUATION).read_text(encoding="utf-8")

    baseline = section(fixtures, "## Exact baseline R0")
    aliases = table_aliases(baseline, "| Alias | Type |")
    nodes = {alias for alias, _ in aliases}
    drawings = {alias for alias, kind in aliases if kind.startswith("Drawing document")}
    flow_block, other_block = code_blocks(baseline)[:2]
    flow = parse_edges(flow_block, "FLOW")
    other = parse_edges(other_block)
    r0_edges = flow + other

    r2_row = re.search(r"^\| R2 \|.*$", fixtures, re.MULTILINE).group(0)
    deleted = set(re.search(r"delete (\w+) and (\w+);", r2_row).groups())
    r2_edges = [e for e in r0_edges if not {e[1], e[2]} & deleted]
    r2_on_sheet_removed = sum(
        1 for e in r0_edges if e[0] == "ON_SHEET" and {e[1], e[2]} & deleted
    )

    scn010_row = re.search(r"^\| SCN-010 \|.*$", fixtures, re.MULTILINE).group(0)
    cut = re.search(r"evidence for `(\w+)→(\w+)`", scn010_row).groups()
    scn010_edges = [e for e in r0_edges if (e[1], e[2]) != cut]

    operational = section(fixtures, "## Operational fixture for SCN-011")
    context_nodes = table_aliases(operational, "| Alias | Type and payload |")
    accepted = re.search(r"The exact accepted edges are (.*?)\. ", operational).group(1)
    context_edges = re.findall(r"`(\w+) ([A-Z_]+) (\w+)`", accepted)

    worlds = number(re.search(r"(\d+) disjoint R0-sized worlds", evaluation).group(1))

    return {
        "r0.nodes": len(nodes),
        "r0.engineering_objects": len(nodes - drawings),
        "r0.drawings": len(drawings),
        "r0.flow_edges": len(flow),
        "r0.other_edges": len(other),
        "r0.edges": len(r0_edges),
        "r0.e1_e2_paths": simple_paths(flow, "E1", "E2"),
        "r2.nodes": len(nodes - deleted),
        "r2.edges": len(r2_edges),
        "r2.on_sheet_removed": r2_on_sheet_removed,
        "r2.e1_e2_paths": simple_paths([e for e in r2_edges if e[0] == "FLOW"], "E1", "E2"),
        "scn010.nodes": len(nodes),
        "scn010.edges": len(scn010_edges),
        "scn011.contextual_nodes": len(context_nodes),
        "scn011.contextual_edges": len(context_edges),
        "scn011.nodes": len(nodes) + len(context_nodes),
        "scn011.edges": len(r0_edges) + len(context_edges),
        "scaled.worlds": worlds,
        "scaled.sheets": worlds * len(drawings),
        "scaled.engineering_objects": worlds * len(nodes - drawings),
        "scaled.nodes": worlds * len(nodes),
        "scaled.edges": worlds * len(r0_edges),
        "scaled.r2_nodes": worlds * len(nodes - deleted),
        "scaled.r2_edges": worlds * len(r2_edges),
        "documents.substantive": len(
            [p for p in (root / "docs").glob("LIONG-0[0-9][0-9]-*.md") if not p.name.startswith("LIONG-000")]
        ),
    }


# Each claim: the file, a pattern whose groups are figures, and the figure each group states.
# A claim that no longer matches is an error, so a reworded sentence cannot slip past.
CLAIMS: list[tuple[str, str, tuple[str, ...]]] = [
    (str(FIXTURES), r"fixture contains (\d+) nodes: (\d+) engineering objects and (\w+) drawing documents",
     ("r0.nodes", "r0.engineering_objects", "r0.drawings")),
    (str(FIXTURES), r"These (\d+) edges express", ("r0.flow_edges",)),
    (str(FIXTURES), r"The other (\d+) edges are", ("r0.other_edges",)),
    (str(FIXTURES), r"baseline therefore contains (\d+) edges", ("r0.edges",)),
    (str(FIXTURES), r"\| Baseline above \| (\d+) nodes, (\d+) edges", ("r0.nodes", "r0.edges")),
    (str(FIXTURES), r"their (\w+) `ON_SHEET` edges", ("r2.on_sheet_removed",)),
    (str(FIXTURES), r"\| (\d+) nodes, (\d+) edges\. No bypass", ("r2.nodes", "r2.edges")),
    (str(FIXTURES), r"R0 has exactly (\w+) simple directed E1-to-E2 paths", ("r0.e1_e2_paths",)),
    (str(FIXTURES), r"R2 has exactly (\w+) path", ("r2.e1_e2_paths",)),
    (str(FIXTURES), r"has (\d+) nodes and (\d+) edges after removing", ("scn010.nodes", "scn010.edges")),
    (str(FIXTURES), r"Exactly (\w+) contextual nodes and (\w+) accepted contextual edges",
     ("scn011.contextual_nodes", "scn011.contextual_edges")),
    (str(FIXTURES), r"exactly these (\w+) contextual nodes", ("scn011.contextual_nodes",)),
    (str(FIXTURES), r"comparison view has (\d+) nodes and (\d+) edges", ("scn011.nodes", "scn011.edges")),
    (str(FIXTURES), r"current state has (\d+) nodes, (\d+) edges, and tag", ("r0.nodes", "r0.edges")),
    (str(EVALUATION), r"(\d+) nodes and (\d+) edges, not merely", ("r0.nodes", "r0.edges")),
    (str(EVALUATION), r"(\d+) engineering objects, (\d+) total comparison nodes, (\d+) edges \|",
     ("r0.engineering_objects", "r0.nodes", "r0.edges")),
    (str(EVALUATION),
     r"(\d+) disjoint R0-sized worlds: ([\d,]+) sheets, ([\d,]+) engineering objects, "
     r"([\d,]+) total comparison nodes, ([\d,]+) edges",
     ("scaled.worlds", "scaled.sheets", "scaled.engineering_objects", "scaled.nodes", "scaled.edges")),
    (str(EVALUATION), r"comparison total is ([\d,]+) nodes and ([\d,]+) edges",
     ("scaled.r2_nodes", "scaled.r2_edges")),
    ("README.md", r"(\w+) draft documents", ("documents.substantive",)),
    ("docs/LIONG-000-index.md", r"All (\w+) substantive documents", ("documents.substantive",)),
]

# Any `nodes/edges` shorthand such as `17/31` in these files must name a known graph state.
PAIR_FILES = (str(FIXTURES), str(EVALUATION))


def flat(text: str) -> str:
    """Join wrapped lines so a claim split across lines still matches."""
    return re.sub(r"\s+", " ", text)


def check(root: Path) -> list[str]:
    figures = compute(root)
    errors: list[str] = []
    for name, pattern, keys in CLAIMS:
        text = flat((root / name).read_text(encoding="utf-8"))
        matches = list(re.finditer(pattern, text))
        if not matches:
            errors.append(f"{name}: claim not found: {pattern}")
        for match in matches:
            for key, stated in zip(keys, match.groups()):
                if number(stated) != figures[key]:
                    errors.append(f"{name}: states {stated} for {key}; the fixture gives {figures[key]}")
    pairs = {(figures[f"{s}.nodes"], figures[f"{s}.edges"]) for s in STATE_PAIRS}
    for name in PAIR_FILES:
        text = (root / name).read_text(encoding="utf-8")
        for nodes, edges in re.findall(r"(?<![\d/])([1-9]\d*)/([1-9]\d*)(?![\d/])", text):
            if (int(nodes), int(edges)) not in pairs:
                errors.append(f"{name}: {nodes}/{edges} matches no known graph state")
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
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True
    )
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
        source = {"commit": commit(ROOT), "files": [str(FIXTURES), str(EVALUATION), "docs/"]}
        if args.json:
            print(json.dumps({"source": source, "figures": figures}, indent=2))
        else:
            print(f"Read {', '.join(source['files'])} at commit {source['commit']}")
            for key, value in figures.items():
                print(f"{key} = {value}")
        return 0
    if args.command == "check":
        errors = check(ROOT)
        print("\n".join(errors) if errors else f"Figures match the fixtures in {len(CLAIMS)} claims.")
        return 1 if errors else 0
    results = find(ROOT, args.pattern)
    print("\n".join(results) if results else "No matches.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
