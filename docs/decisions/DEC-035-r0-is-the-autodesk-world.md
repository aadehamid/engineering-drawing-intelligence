# DEC-035: R0 is the Autodesk world, and a new world W-SP is the SmartPlant world

Status: Proposed
Date: 2026-10-12

## Context

[DEC-029](DEC-029-two-canonical-worlds.md) gives the project two canonical worlds,
one per vendor schema, without saying which is which. Q22 proposed R0 as the
Autodesk world and a new world, W-SP, for SmartPlant. The owner's answer kept the
two-world idea and did not name the worlds. Because Q22 was answered, the
skipped-question rule in [DEC-014](DEC-014-skipped-question-convention.md) does not
apply.

## Decision

Proposed: R0 is the Autodesk world, and its backend uses the Plant 3D-style schema.
W-SP is the SmartPlant world, and its backend uses the SmartPlant-style schema. W-SP
is built to exercise what only SmartPlant has, such as connectors split at inline
valves and pipelines derived from matching properties.

## Alternatives considered

- R0 as the SmartPlant world, with a new world for Autodesk. MILESTONE-001 would then
  start on the harder connector model, which
  [DEC-030](DEC-030-plant-3d-backend-first.md) puts second, or wait for a new world.

## Owner's words

Not yet confirmed. The owner's Q22 answer, quoted in DEC-029, asks for two worlds
and does not name them.

## Evidence

- [DEC-015](DEC-015-first-generation-slice.md) builds MILESTONE-001 on R0, and
  DEC-030 builds the Plant 3D-style backend first for MILESTONE-001.
- LIONG-006 writes every expected result against R0.
