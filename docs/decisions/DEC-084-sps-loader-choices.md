# DEC-084: The SmartPlant-style loader reuses the Plant 3D loader's code, with the backend and its columns as parameters

Status: Decided
Date: 2026-10-19

## Context

[DEC-051](DEC-051-p3d-loader-choices.md) set how the Plant 3D-style loader applies a
snapshot: a full replace, the rows and the outbox event in one transaction, and every
check before any write. W-SP's snapshot needs a loader for schema `sps` in the same
database ([DEC-028](DEC-028-one-database-two-schemas.md)), sharing the one outbox
([DEC-047](DEC-047-loader-outbox-schema.md)). How to build it was open. The agent
decided during the MILESTONE-001b night run, under the owner's delegation in
[DEC-080](DEC-080-milestone-001b-night-delegation.md). The owner can reverse it.

## Decision

1. **One load routine.** `scripts/load_p3d.py`'s snapshot check and load take the
   backend's schema name and its tables' columns as parameters, with the Plant 3D
   values as defaults. `scripts/load_sps.py` holds the `sps` columns, as
   `schemas/smartplant-style.sql` creates them, and calls the same routine. Every rule
   of DEC-051 therefore holds for both backends in one place.
2. **The manifest names its backend.** A load refuses a snapshot whose manifest is for
   another backend, before any write.
3. **One outbox.** Creating a backend applies `schemas/outbox.sql` only when schema
   `outbox` does not exist yet, so both backends can be created in one database in
   either order. Each event names its backend. A create run prints only the schema
   files it applied.

## Alternatives considered

- A separate copy of the load routine for `sps`. It would let the two loaders drift
  apart on the rules DEC-051 sets.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- `scripts/test_load_sps.py` passed against SQL Server 2022 under OrbStack on
  2026-10-19. It loads W0 with its event, reads every row back unchanged, reloads it
  without a second event, and leaves no rows and no event after an interrupted load,
  a file that differs from the manifest, a crafted column name, a duplicate vessel
  tag, or a Plant 3D snapshot. It also loads R0 and W0 side by side in one database
  with one outbox.
- `scripts/test_load_p3d.py` still passes with the shared routine.
