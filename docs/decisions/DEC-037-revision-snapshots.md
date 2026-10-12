# DEC-037: Each source revision is one complete backend snapshot that fills in the vendor's own revision fields

Status: Decided
Date: 2026-10-12

## Context

Asked as Q25 (How each backend stores a revision) in round 4 of the synthetic-data
interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q25:

> Yes, full snapshots. LIONG-006 already allows a full source snapshot (SCN-004),
> and DEC-031 says we copy saved data. A saved Plant 3D or SmartPlant database
> holds the current state plus its own history, not every past state side by side.

## Alternatives considered

- One database that keeps every revision with deleted-flags, which the question named
  as the alternative.

## Owner's words

Asked as Q25 in round 4 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> R1 renames E2 and R2 deletes the bypass valve VB and its pipe P6. Should the
> generator write one complete backend snapshot per source revision (R0, R1, R2
> each a full file set)? Each snapshot would fill in that vendor's own revision
> fields:
> - SmartPlant-style: a drawing revision record with major and minor numbers, plus
>   status on the drawing.
> - Plant 3D-style: the revision and status columns on each row, plus a work-
>   history row for each change.
>
> A deleted object is missing from the next snapshot, and only the history records
> its removal. The alternative is one database that keeps every revision with
> deleted-flags.

The recommendation given with it:

> Yes, full snapshots. LIONG-006 already allows a full source snapshot (SCN-004),
> and DEC-031 says we copy saved data. A saved Plant 3D or SmartPlant database
> holds the current state plus its own history, not every past state side by side.

The owner answered:

> Agree on all

The answer covered every question in round 4, Q24 to Q29.

## Evidence

- `docs/LIONG-006-synthetic-data.md:183` allows a full source snapshot in SCN-004.
