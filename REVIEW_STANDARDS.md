# Review standards

Judgement rules a reviewer applies to pull requests in this repository, beyond the
shared way-of-working standard. That standard owns the general review rules: owner
words on the record (rule 1), one wording per rule (rule 6), and proving that a
check fails and redesigning one that does not converge (`before-push.md`).
Mechanical rules live in `scripts/check.sh`.

Each rule below names the review finding that taught it. Add a rule only from a
finding a reviewer made in this repository, after reading the commit that shows it.

## Descriptions of this repository's checks keep their boundaries

Text that describes `scripts/check.sh` or its parts states what they cover and no
more. The worktree guard covers tracked files, untracked files that are not
gitignored, the index, and git status. `liong_facts.py check` covers registered
claims, plus every number in a sentence about nodes or edges in LIONG-006 and
LIONG-010. Figures in other documents are outside the sweep; a reviewer checks them
against `python3 scripts/liong_facts.py figures`.

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
