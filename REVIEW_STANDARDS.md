# Review standards

Judgement rules a reviewer applies to pull requests in this repository, beyond the
shared way-of-working standard. That standard owns the general review rules: owner
words on the record (rule 1), one wording per rule (rule 6), and proving that a
check fails and redesigning one that does not converge (`before-push.md`).
Mechanical rules live in `scripts/check.sh`.

Each rule below names the review finding that taught it. Add a rule only from a
finding a reviewer made in this repository, after reading the commit that shows it.

## Descriptions of this repository's checks keep their boundaries

Text that describes `scripts/check.sh` or its parts claims no more than the
boundaries stated in `AGENTS.md` ("Checks"), the docstring of
`scripts/worktree_guard.py`, and `CLAIMS` and `SWEPT_FILES` in
`scripts/liong_facts.py`. A figure in a document outside `SWEPT_FILES` and not in a
claim is checked by hand against `python3 scripts/liong_facts.py figures`.

Taught by: the Codex review of #7 found `AGENTS.md` said the guard caught any
change while it skipped gitignored paths (fixed in `25ed2ec`). The Codex review of
#8 found `AGENTS.md` promised ID lists the figures tool did not produce (fixed in
`c2cd189`).

## Changes to the figures sweep are tried against every spelling

A change to the patterns in `scripts/liong_facts.py` is tested with each form a
writer could use for a node or edge figure: digits, number words, backticks,
hyphenated compounds such as `17-node/31-edge`, zero padding, wrapped lines, and
several words between the number and "nodes" or "edges".

Taught by: the Codex review of #8 found "15 nodes", "seventeen nodes", and a
backticked number escaping the sweep (redesigned in `d956bd2` and `afc3d7d`). The
Cursor review of #8 then found `17-node/31-edge` in SCN-001 escaping it (fixed in
`55231c3`).
