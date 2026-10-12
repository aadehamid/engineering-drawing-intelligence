# Decision records

One file per owner decision, holding the evidence behind it. The
[decision register](../LIONG-REG-001-decisions.md) stays the summary of approval
state; a register row links here when its decision has a record.

## Index

| ID | Decision | Status | Date |
| --- | --- | --- | --- |
| [DEC-014](DEC-014-skipped-question-convention.md) | A skipped question in a decision round counts as agreement | Decided | 2026-10-11 |

## Record format

What each status means, when a decision is Decided, and how one decision amends
another follow the way-of-working standard (`references/deciding.md`). This
section fixes only the shape that `python3 scripts/liong_facts.py check` verifies.

- **File name** `DEC-NNN-short-slug.md`, first line `# DEC-NNN: <decision>`, then a
  `Status:` line (`Proposed`, `Decided`, or `Superseded`) and a `Date: YYYY-MM-DD`
  line.
- **Sections**, in order and none empty: `## Context`, `## Decision`,
  `## Alternatives considered`, `## Owner's words`, `## Evidence`.
- **Owner's words** in a `Decided` record: a line `The owner answered:` (or
  `said:` or `wrote:`) followed by the quote in a `>` block.
- **Supersession**: the earlier record has `Superseded by DEC-NNN on YYYY-MM-DD`,
  and the later record has a line `Amends DEC-NNN`.
- **Index**: one row per record, with the link, decision, status and date matching
  the record. Any other row in the Index table fails the check.
