# DEC-035: R0 is the Autodesk world, and a new world W-SP is the SmartPlant world

Status: Decided
Date: 2026-10-12

## Context

[DEC-029](DEC-029-two-canonical-worlds.md) gives the project two canonical worlds,
one per vendor schema, without saying which is which. Q22 proposed R0 as the
Autodesk world and a new world, W-SP, for SmartPlant. The owner's Q22 answer kept
the two-world idea and did not name the worlds, so this record stayed Proposed in
#13 until the owner confirmed it.

## Decision

R0 is the Autodesk world, and its backend uses the Plant 3D-style schema. W-SP is
the SmartPlant world, and its backend uses the SmartPlant-style schema. What W-SP
contains is still open in the interview.

## Alternatives considered

- R0 as the SmartPlant world, with a new world for Autodesk. MILESTONE-001 would then
  start on the harder connector model, which
  [DEC-030](DEC-030-plant-3d-backend-first.md) puts second, or wait for a new world.

## Owner's words

Asked on 2026-10-12, while #13 was open:

> The one decision waiting on you is DEC-035: R0 is the Autodesk world, and the new
> world W-SP is the SmartPlant world. It's marked Proposed because your Q22 answer
> didn't say which world is which. Reply "yes" to confirm, or tell me to swap them,
> and I'll record your words.

The owner answered:

> yes, R0 is Autodesk and W-SP is SmartPlant

## Evidence

- [DEC-015](DEC-015-first-generation-slice.md) builds MILESTONE-001 on R0, and
  DEC-030 builds the Plant 3D-style backend first for MILESTONE-001.
- LIONG-006 specifies R0 and the scenarios built on it.
