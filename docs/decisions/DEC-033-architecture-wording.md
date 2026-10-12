# DEC-033: ARCHITECTURE.md describes two synthetic backends that follow vendor storage patterns

Status: Decided
Date: 2026-10-11

## Context

`ARCHITECTURE.md:17` says the backend "is a synthetic test source, not a replica
of an undisclosed engineering platform". [DEC-020](DEC-020-vendor-style-backends.md)
makes the backends follow two named vendors closely.

## Decision

The owner accepted the recommendation given with Q20:

> Yes. This changes an approved baseline document, so it goes in its own PR with a
> decision record quoting your Q9 answer.

The sentence it proposed reads:

> Two synthetic backends follow the documented storage patterns of SmartPlant P&ID
> and AutoCAD Plant 3D, using original names. Neither copies a vendor schema.

## Alternatives considered

- Keep the sentence. It would contradict DEC-020.

## Owner's words

Asked as Q20 of the synthetic-data interview on 2026-10-11:

> ARCHITECTURE.md says the backend "is a synthetic test source, not a replica of
> an undisclosed engineering platform." Should that sentence change to say: "Two
> synthetic backends follow the documented storage patterns of SmartPlant PID and
> AutoCAD Plant 3D, using original names. Neither copies a vendor schema."?
> LIONG-003 and LIONG-006 would be updated to match.

The recommendation given with it:

> Yes. This changes an approved baseline document, so it goes in its own PR with a
> decision record quoting your Q9 answer.

The owner answered:

> Q20. Agreed.

This section cannot hold an ampersand, so the quote above writes the product name
as PID. Evidence gives the question exactly as asked.

## Evidence

- `ARCHITECTURE.md:17`.
- The Q20 question exactly as asked: "ARCHITECTURE.md says the backend "is a
  synthetic test source, not a replica of an undisclosed engineering platform."
  Should that sentence change to say: "Two synthetic backends follow the documented
  storage patterns of SmartPlant P&ID and AutoCAD Plant 3D, using original names.
  Neither copies a vendor schema."? LIONG-003 and LIONG-006 would be updated to
  match."
