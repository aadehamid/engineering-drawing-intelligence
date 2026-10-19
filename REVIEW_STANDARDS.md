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
claim is checked by hand against `uv run python scripts/liong_facts.py figures`.

Taught by: the Codex review of #7 found `AGENTS.md` said the guard caught any
change while it skipped gitignored paths (fixed in `25ed2ec`). The Codex review of
#8 found `AGENTS.md` promised ID lists the figures tool did not produce (fixed in
`c2cd189`).

## Changes to the figures sweep are tried against every spelling

A change to the patterns in `scripts/liong_facts.py` is tested with each form a
writer could use for a node or edge figure: digits, number words, backticks,
hyphenated compounds such as `17-node/31-edge`, zero padding, and several words
between the number and "nodes" or "edges".

Taught by: the Codex review of #8 found the zero-padded pair `018/031` escaping the
pair check (fixed in `c2cd189`), then "15 nodes", "seventeen nodes", a backticked
number, and a long noun phrase escaping the sweep (redesigned in `d956bd2` and
`afc3d7d`). The Cursor review of #8 then found `17-node/31-edge` in SCN-001
escaping it (fixed in `55231c3`).

## Status text and decision records claim only what their tests and sources show

A sentence that says what CI or a run does names the test that does it, or can be
checked against that test, and claims nothing more; two runs stay two runs. A
decision record states only what its cited sources say. For a vendor documentation
portal that renders neighbouring topics on one page, that is the cited topic's own
content.

Taught by: the Cursor review of #50 found LIONG-010 and LIONG-011 joining a snapshot
run published to Neo4j and a SQL Server run into one (fixed in `0b5ad9c` and
`385b0ae`). The Cursor review of #43 found register rows citing section pages and
claims read from neighbouring topics (fixed in `1dfbd99`). The Cursor review of #46
found DEC-083 naming the wrong end item for a vessel (fixed in `40c760c`).
