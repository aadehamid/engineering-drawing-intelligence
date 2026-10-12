# DEC-030: MILESTONE-001 builds the Plant 3D-style backend first

Status: Decided
Date: 2026-10-11

## Context

Building both vendor-style backends at once doubles the first slice. Plant 3D
stores connections as explicit rows, such as line-to-start-asset and
line-to-end-asset. SmartPlant stores them as graphic connectors that split around
each inline valve, which is harder to map.

## Decision

The owner accepted the recommendation given with Q17:

> Yes. Do Plant 3D-style first to prove the route, then add SmartPlant-style as
> MILESTONE-001b.

## Alternatives considered

- Build both backends in MILESTONE-001. The first end-to-end test would wait for
  the harder mapping.
- Build the SmartPlant-style backend first. Its connector splits would be the first
  mapping problem, before the route itself is proven.

## Owner's words

Asked as Q17 of the synthetic-data interview on 2026-10-11:

> Building both at once doubles the first slice. Plant 3D stores connections as
> explicit rows, such as line-to-start-asset and line-to-end-asset. SmartPlant
> stores them as graphic connectors that split around each inline valve, which is
> harder to map. Should MILESTONE-001 build the Plant 3D-style backend first, with
> SmartPlant-style as the next step?

The recommendation given with it:

> Yes. Do Plant 3D-style first to prove the route, then add SmartPlant-style as
> MILESTONE-001b.

The owner answered:

> Q17: Agreed.

## Evidence

- The vendor research run during the interview, on how each product stores
  connections.
- MILESTONE-001b is a new milestone ID. LIONG-011 does not define it yet.
- Not part of the decision: MILESTONE-001b is a new milestone ID. LIONG-011 does not
  define it yet.
