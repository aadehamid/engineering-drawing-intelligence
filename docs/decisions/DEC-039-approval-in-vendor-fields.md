# DEC-039: Each backend stores the source approval in its vendor's own fields

Status: Decided
Date: 2026-10-12

## Context

Asked as Q27 (Where the source approval lives) in round 4 of the synthetic-data
interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q27:

> Yes. The DEXPI mapping then has to find approval where each product keeps it. A
> custom approval table would hide that work.

## Alternatives considered

- An approval table the project invents.

## Owner's words

Asked as Q27 in round 4 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> LIONG-006 says the backend R0 includes "an explicit synthetic source-approval
> record". Should each backend store that approval in its vendor's own fields
> instead of a table we invent?
> - SmartPlant-style: the approved-by and approval-date fields on the drawing
>   revision.
> - Plant 3D-style: an approved status value on the rows and the drawing.

The recommendation given with it:

> Yes. The DEXPI mapping then has to find approval where each product keeps it. A
> custom approval table would hide that work.

The owner answered:

> Agree on all

The answer covered every question in round 4, Q24 to Q29.

## Evidence

- LIONG-006 says the backend R0 fixture includes an explicit synthetic
  source-approval record.
