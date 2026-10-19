"""Record every file a pipeline step opens, from before its import to the end of its run.

The extraction and slice tests use this to prove that a step never opens an answer key.
It runs the step's code in a fresh Python process with an audit hook installed first,
so a read at import time, by any of Python's open functions or pathlib, is recorded
too, not only a read during the run.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

SCRIPTS = Path(__file__).resolve().parent

CHILD = """
import json, sys
opened = []
sys.addaudithook(lambda event, args: opened.append(str(args[0])) if event == "open" else None)
sys.path.insert(0, sys.argv[1])
exec(sys.argv[2])
print(json.dumps(opened))
"""


def files_opened(code: str) -> list[str]:
    """Every path opened while `code` runs, imports included, in a fresh process."""
    result = subprocess.run([sys.executable, "-c", CHILD, str(SCRIPTS), code],
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout.splitlines()[-1])


def extraction(module: str, folders: list[Path]) -> str:
    """Code that imports an extractor and extracts each snapshot folder."""
    return (f"import {module} as extractor\nfrom pathlib import Path\n"
            f"for folder in {[str(f) for f in folders]!r}:\n"
            "    revision, rows = extractor.rows_from_snapshot(Path(folder))\n"
            "    extractor.extract(revision, rows, 'guard', '2026-01-01T00:00:00+00:00')\n")
