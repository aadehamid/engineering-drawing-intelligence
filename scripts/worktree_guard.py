"""Run a command and fail if it changes the working tree, the index, or git status.

Usage: python3 scripts/worktree_guard.py -- <command> [args...]
"""

import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import NamedTuple


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True
    ).stdout


def entry(path: Path) -> tuple:
    """Describe one filesystem entry without following a symlink.

    Reads that fail raise, so an unreadable path aborts the comparison
    instead of dropping out of both snapshots.
    """
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return ("missing",)
    mode = stat.S_IMODE(info.st_mode)
    if stat.S_ISLNK(info.st_mode):
        return ("symlink", mode, os.readlink(os.fsencode(path)))
    if stat.S_ISREG(info.st_mode):
        with open(path, "rb") as handle:
            digest = hashlib.sha256(handle.read()).hexdigest()
        return ("file", mode, digest)
    return ("other", stat.S_IFMT(info.st_mode), mode)


class Snapshot(NamedTuple):
    entries: dict[bytes, tuple]
    index: bytes
    status: bytes


def snapshot(root: Path) -> Snapshot:
    """Capture contents, entries, index blobs, and git status for every non-ignored path."""
    listed = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    names = sorted({name for name in listed.split(b"\0") if name})
    return Snapshot(
        entries={name: entry(root / os.fsdecode(name)) for name in names},
        index=git(root, "ls-files", "-s", "-z"),
        status=git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all"),
    )


def differences(before: Snapshot, after: Snapshot) -> list[str]:
    found: list[str] = []
    old, new = before.entries, after.entries
    for name in sorted(old.keys() | new.keys()):
        if old.get(name) != new.get(name):
            found.append(f"changed entry: {os.fsdecode(name)}")
    if before.index != after.index:
        found.append("changed index")
    if before.status != after.status:
        found.append("changed git status")
    return found


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] != "--":
        print(__doc__.strip(), file=sys.stderr)
        return 2
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
    before = snapshot(root)
    result = subprocess.run(argv[1:], cwd=root)
    found = differences(before, snapshot(root))
    for line in found:
        print(f"worktree guard: {line}", file=sys.stderr)
    if found:
        return 1
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
