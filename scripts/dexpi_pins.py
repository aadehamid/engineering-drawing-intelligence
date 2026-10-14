#!/usr/bin/env python3
"""The pinned DEXPI 2.0.1 files (DEC-061, DEC-062) and the import table that maps to them.

`standards/dexpi/2.0.1/MANIFEST.json` lists each pinned file with its SHA-256 and source.
`check` fails unless the folder holds exactly the manifest's files, plus MANIFEST.json and
NOTICE.md, and each file's hash matches. `local_path` maps an import URI to its pinned
copy, so no DEXPI check ever reads the network. A URI the manifest records as not
published, or that it does not list at all, has no local copy and raises UnpinnedImport.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN_DIR = ROOT / "standards" / "dexpi" / "2.0.1"
OWN_FILES = {"MANIFEST.json", "NOTICE.md"}


class UnpinnedImport(LookupError):
    """An import URI with no pinned local copy."""


def manifest(pin_dir: Path = PIN_DIR) -> dict:
    return json.loads((pin_dir / "MANIFEST.json").read_text(encoding="utf-8"))


def errors(pin_dir: Path = PIN_DIR) -> list[str]:
    """Every way the pinned folder differs from its manifest."""
    files = manifest(pin_dir)["files"]
    found = {path.name for path in pin_dir.iterdir()} - OWN_FILES
    problems = [f"{name}: not listed in MANIFEST.json" for name in sorted(found - set(files))]
    problems += [f"{name}: listed in MANIFEST.json but missing" for name in sorted(set(files) - found)]
    for name in sorted(set(files) & found):
        digest = hashlib.sha256((pin_dir / name).read_bytes()).hexdigest()
        if digest != files[name]["sha256"]:
            problems.append(f"{name}: SHA-256 {digest} does not match the manifest's {files[name]['sha256']}")
    return problems


def import_table(pin_dir: Path = PIN_DIR) -> dict[str, Path]:
    """Each model URI the manifest pins, mapped to its local copy."""
    return {entry["uri"]: pin_dir / name for name, entry in manifest(pin_dir)["files"].items() if "uri" in entry}


def local_path(uri: str, pin_dir: Path = PIN_DIR) -> Path:
    table = import_table(pin_dir)
    if uri in table:
        return table[uri]
    reason = manifest(pin_dir).get("not_published", {}).get(uri, "it is not in MANIFEST.json")
    raise UnpinnedImport(f"{uri} has no pinned copy: {reason}")


def main(argv: list[str]) -> int:
    if argv != ["check"]:
        print("usage: dexpi_pins.py check", file=sys.stderr)
        return 2
    problems = errors()
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print(f"DEXPI 2.0.1 pins match MANIFEST.json: {len(manifest()['files'])} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
