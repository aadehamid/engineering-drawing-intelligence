# DEC-033: ARCHITECTURE.md describes two synthetic backends that follow vendor storage patterns

Status: Decided
Date: 2026-10-11

## Context

`ARCHITECTURE.md:17` says the backend "is a synthetic test source, not a replica
of an undisclosed engineering platform". [DEC-020](DEC-020-vendor-style-backends.md)
makes the backends follow two named vendors closely.

## Decision

The sentence becomes: "Two synthetic backends follow the documented storage
patterns of SmartPlant P&ID and AutoCAD Plant 3D, using original names. Neither
copies a vendor schema." LIONG-003 and LIONG-006 change to match. The edit changes
an approved baseline document, so it lands in its own pull request.

## Alternatives considered

- Keep the sentence. It would contradict DEC-020.

## Owner's words

Asked as Q20 of the synthetic-data interview on 2026-10-11: should the
ARCHITECTURE.md sentence change to the wording quoted in the Decision section,
with LIONG-003 and LIONG-006 updated to match?

The owner answered:

> Q20. Agreed.

## Evidence

- `ARCHITECTURE.md:17`.
