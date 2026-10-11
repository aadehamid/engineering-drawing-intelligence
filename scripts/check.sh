#!/usr/bin/env bash
# Every mechanical check for this repository. CI and the pre-push hook run this script.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

exec python3 scripts/worktree_guard.py -- bash -euo pipefail -c '
python3 scripts/bundle_docs.py --check
python3 scripts/check_docs.py
python3 scripts/test_doc_tools.py
python3 scripts/test_worktree_guard.py
'
