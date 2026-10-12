# DEC-044: Keys stay the same across a world's snapshots, and the backends never share keys

Status: Decided
Date: 2026-10-12

## Context

Asked as Q32 (Keys across revisions and across backends) in round 5 of the
synthetic-data interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q32:

> Yes to both. Stable keys within a backend copy the real products. Separate key
> spaces across backends are what LIONG-006 requires ("each generated
> representation receives a separate source-local key space").

## Alternatives considered

- The question named no alternative.

## Owner's words

Asked as Q32 in round 5 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> Should an object keep the same source-local key in every snapshot of its world?
> E2 would have one key in R0, R1 and R2, the way a real database keeps the row
> when you rename a tag. And should the two backends never share keys, so R0's
> SmartPlant-form fixture (DEC-034) gets its own independent key space?

The recommendation given with it:

> Yes to both. Stable keys within a backend copy the real products. Separate key
> spaces across backends are what LIONG-006 requires ("each generated
> representation receives a separate source-local key space").

The owner answered:

> Agree on all

The answer covered every question in round 5, Q30 to Q34.

## Evidence

- `docs/LIONG-006-synthetic-data.md:41`: each generated representation receives a
  separate source-local key space.
