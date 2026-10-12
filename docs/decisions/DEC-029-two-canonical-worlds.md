# DEC-029: There are two canonical worlds, each generated into one vendor's schema

Status: Decided
Date: 2026-10-11

## Context

Q16 recommended generating every canonical world in both vendor schemas, so that
the two mappings could be compared. The owner declined and asked for one world
per vendor. The interview pushed back once: the same world in both schemas is the
only automatic check that the two mappings agree, and every expected result in
LIONG-006 is written against R0. Q22 then proposed R0 as the Autodesk world and a
new world, W-SP, for SmartPlant.

A canonical world is vendor-neutral truth, and the vendor schema belongs to the
source representation generated from it. The reply to the owner's Q22 answer
stated the decision in those terms.

## Decision

The project has two canonical worlds, and each is generated into one vendor's
schema:

- **R0** is the Autodesk world. Its backend uses the Plant 3D-style schema.
- **W-SP** is the SmartPlant world. Its backend uses the SmartPlant-style schema.
  It is built to exercise what only SmartPlant has, such as connectors split at
  inline valves and pipelines derived from matching properties.

Each answer key is written against its world, not against vendor tables, so one
scorer checks both backends. What W-SP contains is still open in the interview.
[DEC-034](DEC-034-r0-smartplant-cross-check.md) adds R0 in SmartPlant form as test
data only.

## Alternatives considered

- Generate every world in both schemas, which Q16 recommended. The owner chose one
  world per vendor, because a real plant is authored in one tool.
- Exactly two worlds with no cross-check fixture. DEC-034 keeps the fixture.

## Owner's words

Asked as Q16 of the synthetic-data interview on 2026-10-11:

> Should every canonical world, R0 first, be generated in both flavours?

The owner answered:

> Q16: No, I don't want each schema to have their own canonical word. I don't think
> it makes sense to recreate the same thing both in Smart Plan and Autodesk, so
> let's have a canonical word that represents Smart Plan and a canonical word that
> represents Autodesk so that we can use that to keep them apart and use that for
> the projects. Let me know if you have any pushback on that.

Asked as Q22 on 2026-10-11:

> Should R0 become the Autodesk world, with a new SmartPlant world, W-SP, and R0
> also emitted in SmartPlant form purely as a mapping test fixture?

The owner wrote:

> Q22. Essesntially what I want two canonical world.. one in SMartplant schema and
> the other in Autodesk schema.

The owner's words do not name which world is which. R0 as the Autodesk world
follows from the Q22 proposal, which the owner did not contest, and from
[DEC-030](DEC-030-plant-3d-backend-first.md), which builds the Plant 3D-style
backend first for MILESTONE-001's R0 slice.

## Evidence

- LIONG-006, where every expected result is written against R0.
