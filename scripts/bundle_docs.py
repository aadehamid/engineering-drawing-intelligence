"""Create a reproducible review archive with a manifest of the included bytes."""

import argparse
import hashlib
import io
import json
import posixpath
from pathlib import Path
import re
import zipfile
from urllib.parse import unquote, urlsplit

from check_docs import BASELINE, link_targets, names_a_directory, odd_target, raw_html, spaced_angle_targets


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path("docs/releases/LIONG-review-package-v0.1.zip")
UTILITIES = ("check_docs.py", "bundle_docs.py", "test_doc_tools.py")


def payload(root: Path) -> dict[str, bytes]:
    files = [root / name for name in BASELINE]
    files += sorted((root / "docs").glob("*.md"))
    files += sorted((root / "docs" / "decisions").glob("*.md"))
    files += [root / "scripts" / name for name in UTILITIES]
    contents = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(files)
    }
    manifest = {
        "package": "LIONG-review-package",
        "version": "0.1",
        "status": "Draft for review; not an implemented engineering system",
        "sha256": {
            name: hashlib.sha256(data).hexdigest() for name, data in contents.items()
        },
    }
    contents["MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return contents


def broken_links(contents: dict[str, bytes]) -> list[str]:
    """Raw HTML in archived Markdown, and relative links that point at a file the archive lacks.

    Both come from the CommonMark parser, so they are what a reader's renderer shows.
    Raw HTML is refused, so every link is a Markdown link the parser reports.
    A link to the archive itself is allowed: it cannot be inside itself.
    """
    errors = []
    for name, data in sorted(contents.items()):
        if not name.endswith(".md"):
            continue
        text = data.decode("utf-8")
        errors += [f"{name}: raw HTML is not allowed outside code: {tag[:60]}" for tag in raw_html(text)]
        errors += [f"{name}: link target holds whitespace: {target}" for target in spaced_angle_targets(text)]
        for target in link_targets(text):
            parsed = urlsplit(target)
            path = unquote(parsed.path)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            if odd_target(path):
                errors.append(f"{name}: link target holds whitespace or a control character: {unquote(target)!r}")
                continue
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            if names_a_directory(path) or (dest not in contents and dest != OUTPUT.as_posix()):
                errors.append(f"{name}: links to {unquote(target)}, which is not in the archive")
    return errors


def archive_bytes(contents: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return buffer.getvalue()


def matches(path: Path, contents: dict[str, bytes]) -> bool:
    if not path.is_file():
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            if sorted(archive.namelist()) != sorted(contents):
                return False
            return all(archive.read(name) == data for name, data in contents.items())
    except (zipfile.BadZipFile, OSError, RuntimeError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the archive is stale")
    args = parser.parse_args()
    contents = payload(ROOT)
    output = ROOT / OUTPUT
    errors = broken_links(contents)
    if errors:
        print("\n".join(errors))
        return 1
    if args.check:
        if not matches(output, contents):
            print("Archive missing or stale. Run uv run python scripts/bundle_docs.py")
            return 1
        print(f"Archive matches all {len(contents) - 1} source files and its manifest.")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive_bytes(contents))
    print(f"Wrote {OUTPUT} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
