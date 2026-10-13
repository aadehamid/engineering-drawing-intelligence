"""Check the review package, not the unimplemented engineering pipeline."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
BASELINE = (
    "README.md",
    "PROBLEM_STATEMENT.md",
    "ARCHITECTURE.md",
    "REQUIREMENTS.md",
    "GLOSSARY.md",
)

# A destination may sit on the next line, behind that line's quote markers.
NEXT_LINE = r"[ \t]*(?:\n[ \t>]*)?"
# A bare destination ends at ASCII whitespace or a control character only; CommonMark
# keeps a no-break space or other Unicode space inside the destination.
BARE = r"[^\x00-\x20)]+"
INLINE_LINK = r"\]\(" + NEXT_LINE + r"(<[^>\n]*>|" + BARE + ")"   # [text](target), even split across lines
# [label]: target, used by reference links. It may sit inside quotes and lists, and its
# label may escape a bracket; matching too much only checks one more target.
REFERENCE = r"^[ \t>*+\-\d.)]*\[(?:\\.|[^\]\\])+\]:" + NEXT_LINE + r"(<[^>\n]*>|[^\x00-\x20]+)"


# A fence opens on three backticks or tildes. A backtick fence's info string holds no
# backtick; a line like "``` `" is ordinary text in CommonMark.
FENCE_OPEN = r"^ {0,3}(`{3,}(?=[^`\n]*$)|~{3,})"


def as_commonmark(text: str) -> str:
    """The text CommonMark parses: CRLF and CR end lines, and a NUL becomes U+FFFD."""
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "\ufffd")


# Python ends a line at these characters and CommonMark does not, so a check that splits
# lines with Python would see a different document. Archived Markdown holds none of them.
ODD_LINE_BREAK = "[\v\f\x1c\x1d\x1e\x85\u2028\u2029]"


def odd_line_breaks(text: str) -> list[str]:
    """Every character other than LF or CR that Python treats as a line break."""
    return re.findall(ODD_LINE_BREAK, text)


def names_a_directory(path: str) -> bool:
    """True when a link path ends in '/', '.' or '..', so it cannot name a file."""
    return path.rsplit("/", 1)[-1] in ("", ".", "..")


def nested_fences(text: str) -> list[str]:
    """Every code fence that does not start in the first column.

    A fence inside a list or quote, or indented, ends by rules this check does not
    model, so such a fence could hide text or show code as text. Only a fence at the
    first column is allowed.
    """
    return re.findall(r"^[ \t>*+\-\d.)]*[ \t>*+\-.)](?:`{3,}|~{3,}).*", as_commonmark(text), re.MULTILINE)


def raw_html(text: str) -> list[str]:
    """Every HTML tag or comment, code spans and fences included. An autolink <https://...> is text.

    Code is not exempt: telling CommonMark code from text needs its full escape and
    delimiter rules, and a mistake there would hide a live tag.
    """
    return re.findall(r"<(?![A-Za-z][\w+.-]*:)[A-Za-z!/?][^>\n]*>?", as_commonmark(text))


def link_targets(text: str) -> list[str]:
    """Every Markdown link and image target: inline ones and reference definitions.

    Raw HTML links are not read; archived Markdown holds no raw HTML (see raw_html).
    """
    text = as_commonmark(text)
    found = re.findall(INLINE_LINK, text) + re.findall(REFERENCE, text, re.MULTILINE)
    # Only a destination written as <...> loses its brackets; "a.md>" names a file "a.md>".
    return [target[1:-1] if target.startswith("<") else target for target in found]


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
        for target in link_targets(text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue  # External source availability is a separate research check.
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if parsed.path and names_a_directory(unquote(parsed.path)):
                errors.append(f"{path.name}: link names a directory, not a file: {target}")
            elif not dest.is_relative_to(root.resolve()):
                errors.append(f"{path.name}: local link escapes repository: {target}")
            elif not dest.is_file():
                errors.append(f"{path.name}: missing link target: {target}")
            elif parsed.fragment and dest.suffix == ".md":
                fragment = unquote(parsed.fragment)
                if fragment not in heading_ids(dest.read_text(encoding="utf-8")):
                    errors.append(f"{path.name}: missing heading: {target}")

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
