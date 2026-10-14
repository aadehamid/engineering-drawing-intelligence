#!/usr/bin/env bash
# Every mechanical check for this repository. CI and the pre-push hook run this script.
# The guard runs this same script with --checks and fails if a check changes tracked
# or non-ignored files, the index, or git status.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [ "${1:-}" != "--checks" ]; then
  exec python3 scripts/worktree_guard.py -- scripts/check.sh --checks
fi

uv run --locked python scripts/bundle_docs.py --check
uv run --locked python scripts/check_docs.py
uv run --locked python scripts/test_doc_tools.py
python3 scripts/test_worktree_guard.py
uv run --locked python scripts/liong_facts.py check
uv run --locked python scripts/test_liong_facts.py
uv run --locked python scripts/world.py check
uv run --locked python scripts/test_world.py
uv run --locked python scripts/test_plant3d_schema.py
uv run --locked python scripts/generate_p3d.py --check
uv run --locked python scripts/test_generate_p3d.py
uv run --locked python scripts/test_load_p3d.py
uv run --locked python scripts/dexpi_pins.py check
uv run --locked python scripts/test_dexpi_pins.py
