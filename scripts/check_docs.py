"""Check the review package, not the unimplemented engineering pipeline."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from markdown_it.token import Token


ROOT = Path(__file__).resolve().parents[1]
BASELINE = (
    "README.md",
    "PROBLEM_STATEMENT.md",
    "ARCHITECTURE.md",
    "REQUIREMENTS.md",
    "GLOSSARY.md",
)

# GitHub renders this repository's Markdown as CommonMark plus tables and strikethrough.
MARKDOWN = MarkdownIt("commonmark").enable(["table", "strikethrough"])


def tokens(text: str) -> list[Token]:
    """Every token of the parsed document, the inline children of each block included."""
    found = []
    for token in MARKDOWN.parse(text):
        found.append(token)
        found += token.children or []
    return found


def odd_target(target: str) -> bool:
    """True when a link target holds whitespace of any kind or a control character.

    URL parsing drops or changes these, so a file named with one is never what a link means.
    """
    return any(ch.isspace() or ch < " " or ch == "\x7f" for ch in target)


def spaced_angle_targets(text: str) -> list[str]:
    """Every '<...>' link target that holds whitespace.

    Parsers disagree on these: markdown-it trims a leading space that GitHub keeps.
    Refusing them keeps the link check from depending on which parser is right.
    """
    return re.findall(r"\]\(\s*(<[^<>\n]*\s[^<>\n]*>)", text) + re.findall(r"\]:\s*(<[^<>\n]*\s[^<>\n]*>)", text)


def names_a_directory(path: str) -> bool:
    """True when a link path ends in '/', '.' or '..', so it cannot name a file."""
    return path.rsplit("/", 1)[-1] in ("", ".", "..")


def raw_html(text: str) -> list[str]:
    """Every HTML block or inline tag a reader's renderer would act on. HTML inside code is text."""
    return [t.content.strip() for t in tokens(text) if t.type in ("html_block", "html_inline")]


def link_targets(text: str) -> list[str]:
    """Every link and image target a reader sees, URL-encoded as the renderer writes it.

    Reference links arrive resolved; a definition nothing uses renders nothing and is skipped.
    """
    found = [t.attrGet("href") if t.type == "link_open" else t.attrGet("src")
             for t in tokens(text) if t.type in ("link_open", "image")]
    return [str(target) for target in found if target is not None]


def heading_ids(text: str) -> set[str]:
    """Support the plain ATX headings used in this documentation package."""
    result: set[str] = set()
    counts: dict[str, int] = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result


def check(root: Path) -> list[str]:
    errors: list[str] = []
    docs = sorted((root / "docs").glob("*.md"))
    files = [root / name for name in BASELINE] + docs
    for number in range(12):
        matches = list((root / "docs").glob(f"LIONG-{number:03d}-*.md"))
        if len(matches) != 1:
            errors.append(f"Expected one LIONG-{number:03d} document, found {len(matches)}")
    for name in ("LIONG-REG-001-decisions.md", "LIONG-REF-001-reference-register.md"):
        if not (root / "docs" / name).is_file():
            errors.append(f"Missing register: {name}")

    texts: dict[Path, str] = {}
    for path in files:
        if not path.is_file():
            errors.append(f"Missing document: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[path] = text
        label = str(path.relative_to(root))
        if not text.endswith("\n"):
            errors.append(f"{label}: missing final newline")
        for number, line in enumerate(text.splitlines(), 1):
            if line.rstrip() != line:
                errors.append(f"{label}:{number}: trailing whitespace")
            if re.match(r"^(<<<<<<< |=======\s*$|>>>>>>> )", line):
                errors.append(f"{label}:{number}: merge-conflict marker")
        if len(re.findall(r"^```", text, re.MULTILINE)) % 2:
            errors.append(f"{label}: unclosed code fence")
        if path in docs and "draft" not in text.lower():
            errors.append(f"{label}: missing explicit draft status")

    for path, text in texts.items():
        errors += [f"{path.name}: link target holds whitespace: {target}" for target in spaced_angle_targets(text)]
        for target in link_targets(text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue  # External source availability is a separate research check.
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if odd_target(unquote(parsed.path)):
                errors.append(f"{path.name}: link target holds whitespace or a control character: {unquote(target)!r}")
            elif parsed.path and names_a_directory(unquote(parsed.path)):
                errors.append(f"{path.name}: link names a directory, not a file: {unquote(target)}")
            elif not dest.is_relative_to(root.resolve()):
                errors.append(f"{path.name}: local link escapes repository: {unquote(target)}")
            elif not dest.is_file():
                errors.append(f"{path.name}: missing link target: {unquote(target)}")
            elif parsed.fragment and dest.suffix == ".md":
                fragment = unquote(parsed.fragment)
                if fragment not in heading_ids(dest.read_text(encoding="utf-8")):
                    errors.append(f"{path.name}: missing heading: {unquote(target)}")

    requirements = root / "docs/LIONG-002-users-and-requirements.md"
    evaluation = root / "docs/LIONG-010-evaluation.md"
    fixtures = root / "docs/LIONG-006-synthetic-data.md"
    requirement_rows = re.findall(r"^\|\s*(REQ-\d{3})\b", texts.get(requirements, ""), re.MULTILINE)
    scenario_rows = re.findall(r"^\|\s*(SCN-\d{3})\s*\|", texts.get(fixtures, ""), re.MULTILINE)
    known_requirements = set(requirement_rows)
    known_scenarios = set(scenario_rows)
    expected_requirements = {f"REQ-{number:03d}" for number in range(1, 19)}
    expected_scenarios = {f"SCN-{number:03d}" for number in range(1, 17)}
    if known_requirements != expected_requirements or len(requirement_rows) != 18:
        errors.append("LIONG-002 must define REQ-001 through REQ-018 exactly once")
    if known_scenarios != expected_scenarios or len(scenario_rows) != 16:
        errors.append("LIONG-006 must define SCN-001 through SCN-016 exactly once")
    acceptance_rows = re.findall(
        r"^\|\s*(REQ-\d{3})[^|]*\|([^|]*)\|",
        texts.get(evaluation, ""),
        re.MULTILINE,
    )
    if {row[0] for row in acceptance_rows} != expected_requirements or len(acceptance_rows) != 18:
        errors.append("LIONG-010 must map every requirement exactly once in its acceptance matrix")
    for requirement, scenarios in acceptance_rows:
        references = set(re.findall(r"SCN-\d{3}", scenarios))
        if not references or not references <= known_scenarios:
            errors.append(f"LIONG-010: invalid scenario mapping for {requirement}")
    for path, text in texts.items():
        for token in set(re.findall(r"(?:REQ|SCN)-\d{3}", text)):
            known = known_requirements if token.startswith("REQ") else known_scenarios
            if token not in known:
                errors.append(f"{path.name}: undefined reference {token}")
    register = root / "docs/LIONG-REF-001-reference-register.md"
    reference_pattern = r"REF-(?:PPC|STD|DATA|TECH)-\d{3}"
    known_references = set(re.findall(reference_pattern, texts.get(register, "")))
    for path, text in texts.items():
        for token in set(re.findall(reference_pattern, text)) - known_references:
            errors.append(f"{path.name}: unregistered source {token}")
    return errors


if __name__ == "__main__":
    issues = check(ROOT)
    if issues:
        print("\n".join(issues))
        sys.exit(1)
    print("Documentation checks passed: files, local links, headings, IDs, and formatting.")
    print("Not checked: external URL availability, Mermaid rendering, or engineering behavior.")
