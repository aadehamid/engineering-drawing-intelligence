# Decision records

One file per owner decision, holding the evidence behind it. The
[decision register](../LIONG-REG-001-decisions.md) stays the summary of approval
state; a register row links here when its decision has a record.

## Index

| ID | Decision | Status | Date |
| --- | --- | --- | --- |
| [DEC-014](DEC-014-skipped-question-convention.md) | A skipped question in a decision round counts as agreement | Decided | 2026-10-11 |

## Record format

Name each file `DEC-NNN-short-slug.md`. It starts with `# DEC-NNN: <decision>`,
then a `Status:` line and a `Date:` line, then these sections in order:
`## Context`, `## Decision`, `## Alternatives considered`, `## Owner's words`, and
`## Evidence`.

- **Status** is `Proposed`, `Decided`, or `Superseded`. A decision the agent
  inferred, rather than one the owner stated, stays `Proposed` until the owner
  confirms it in words.
- **Owner's words** quotes the owner exactly, in a `>` block, with the question
  it answered. A `Decided` record needs one.
- **Superseded** records keep their text and add a line `Superseded by DEC-NNN`
  with the date. The later record names the one it amends.

`python3 scripts/liong_facts.py check` verifies that the index and the records
agree and that each record has this shape.
