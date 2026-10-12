# DEC-040: The Plant 3D-style schema borrows six patterns from the vendor research, renamed and cited

Status: Decided
Date: 2026-10-12

## Context

Asked as Q28 (The patterns the Plant 3D-style backend borrows) in round 4 of the
synthetic-data interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q28:

> Yes, these six. The SmartPlant-style list comes in a later round, when
> MILESTONE-001b starts.

## Alternatives considered

- The question offered no other pattern list.

## Owner's words

Asked as Q28 in round 4 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> MILESTONE-001 builds this backend first (DEC-030). Should its schema borrow
> these six patterns from the research, each renamed and cited?
> 1. One table per class under a shared base table, with one project-wide key and
>    a GUID on every row.
> 2. Connections as rows of their own: line-to-start-asset, line-to-end-asset, and
>    connector-to-connector.
> 3. A table linking each object to the drawings it appears on, with a drawing
>    handle. Objects carry no drawing ID.
> 4. A table for off-page connector links, which carries R0's cross-sheet pair X1
>    and X2.
> 5. Tags made of format subparts, stored next to the composed tag, which must be
>    unique.
> 6. Class-definition metadata for R0's classes only (DEC-032).

The recommendation given with it:

> Yes, these six. The SmartPlant-style list comes in a later round, when
> MILESTONE-001b starts.

The owner answered:

> Agree on all

The answer covered every question in round 4, Q24 to Q29.

## Evidence

- The vendor research run in round 2 of the interview.
