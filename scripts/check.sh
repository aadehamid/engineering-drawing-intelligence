#!/usr/bin/env bash
# Every mechanical check for this repository. CI and the pre-push hook run this script.
# The guard runs this same script with --checks and fails if any check changes the tree.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [ "${1:-}" != "--checks" ]; then
  exec python3 scripts/worktree_guard.py -- scripts/check.sh --checks
fi

python3 scripts/bundle_docs.py --check
python3 scripts/check_docs.py
python3 scripts/test_doc_tools.py
python3 scripts/test_worktree_guard.py
