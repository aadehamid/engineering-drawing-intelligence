# Review standards

Judgement rules a reviewer applies to every pull request in this repository.
Mechanical rules live in `scripts/check.sh`; the working rules live in
[AGENTS.md](AGENTS.md). Each rule below names the review finding that taught it.
Add a rule only from a finding a reviewer actually made, after reading the commit
that shows it.

## Owner words have a record in the repository

A statement that the owner decided, approved, or said something must point to a
repository record that quotes the owner's words.

Taught by: the Cursor review of #6 held the PR because `AGENTS.md` cited an owner
answer that no repository file contained. Fixed in `9a5f61f`, which recorded it as
DEC-014 in the decision register.

## Restated rules match their authoritative wording

When a document restates a rule owned elsewhere, the restatement keeps the
original's conditions and exceptions. A stricter-sounding version is still wrong.

Taught by: the Codex review of #6 found "a merge approves nothing" contradicted
the register, which lets a merge approve proposals when the owner records that
intent. Fixed in `b7102f6`.

## A documented guarantee is no broader than its check

Each claim a document or comment makes about a check ("fails if any change", "any
shorthand is checked") must match what the code enforces. Narrow the claim or
widen the check, and pin the boundary with a test.

Taught by: the Codex review of #7 found the worktree guard skipped gitignored
paths while `AGENTS.md` said it caught any change. Fixed in `25ed2ec`.

## A check that reads prose is tried against other spellings

When a check finds figures or terms in prose, try the forms a writer could use:
number words, backticks, hyphenated compounds, wrapped lines, zero padding, and
extra words between the number and its noun. When each fix exposes another
spelling, change what the check reads, not just its pattern.

Taught by: the Codex review of #8 found three rounds of escaping spellings
("15 nodes" equal to another figure, "seventeen", a backticked number), redesigned
in `d956bd2` and `afc3d7d`. The Cursor review of #8 then found `17-node/31-edge`
in SCN-001, fixed in `55231c3`.
