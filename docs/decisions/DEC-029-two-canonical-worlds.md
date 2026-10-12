# DEC-029: There are two canonical worlds, each generated into one vendor's schema

Status: Decided
Date: 2026-10-11

## Context

Q16 recommended generating every canonical world in both vendor schemas, so that
the two mappings could be compared. The owner declined and asked for one world
per vendor. The interview pushed back once: the same world in both schemas is the
only automatic check that the two mappings agree, and a second world needs its
own expected results written by hand. Q22 then proposed R0 as the Autodesk world and a
new world, W-SP, for SmartPlant.

A canonical world is vendor-neutral truth, and the vendor schema belongs to the
source representation generated from it. The reply to the owner's Q22 answer
stated the decision in those terms. It added that answer keys written against the world
would let one scorer check both backends. The owner has not confirmed that, so this
record does not decide it.

## Decision

The project has two canonical worlds: one in the SmartPlant-style schema and the
other in the Plant 3D-style schema. Which world is which is decided in
[DEC-035](DEC-035-r0-is-the-autodesk-world.md). What the second world contains is
decided in [DEC-036](DEC-036-w-sp-new-plant.md). [DEC-034](DEC-034-r0-smartplant-cross-check.md) keeps
R0 in SmartPlant form as a cross-check fixture.

## Alternatives considered

- Generate every world in both schemas, which Q16 recommended. The owner chose one
  world per vendor. The interviewer later noted that a real plant is authored in
  one tool, which supports that choice.
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

The owner's words do not name which world is which, so this record does not
decide it. DEC-035 records the owner's later answer.

## Evidence

- LIONG-006, which specifies R0 and the scenarios built on it.
