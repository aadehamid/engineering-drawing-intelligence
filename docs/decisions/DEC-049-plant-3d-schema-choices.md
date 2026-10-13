# DEC-049: The Plant 3D-style schema is one T-SQL file, tested on SQL Server in CI, with tags split as the product splits them

Status: Decided
Date: 2026-10-13

## Context

[DEC-040](DEC-040-plant-3d-patterns.md) set the six patterns the Plant 3D-style
schema borrows. Three questions were left open for the owner before the schema
could be written: how the schema is built and tested, how each class's tag splits
into subparts, and how SQL Server runs on the owner's Apple Silicon machine. The
agent decided them during the night run, under
[DEC-048](DEC-048-night-delegation.md).

## Decision

The agent decided under the owner's delegation:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make

The choices:

1. **Build method.** The schema is one hand-written T-SQL file,
   `schemas/plant3d-style.sql`, that creates schema `p3d`. A test reads the file
   on every run. When `LIONG_SQLSERVER` names a server, the test also applies the
   file to a fresh database and reads it back from SQL Server's catalog. CI runs a
   SQL Server 2022 container for that, so every pull request applies the schema to
   the engine [DEC-027](DEC-027-sql-server-on-azure.md) chose. The Python driver is
   `python-tds`, which needs no ODBC driver.
2. **Tag subparts.** Equipment and valves split into Type and Number, as the
   product's equipment tag format does (REF-TECH-017). An instrument splits into
   its function letters and loop number, as in PI-102. A line segment splits into a
   prefix, a line number and a segment suffix, as in L-101-1. The composed tag is
   stored beside its subparts and is unique within its class table. An off-page
   connector's label, such as TO-S2/A, is a drawing label, not a tag.
3. **SQL Server on Apple Silicon.** Locally, the same SQL Server 2022 image runs
   under OrbStack's x86 emulation. CI is the check that counts; a local run is
   optional.

The schema also adds what the six patterns imply for R0: an `Ownership` table for
I1's parent (the product's AssetOwnership, REF-TECH-016), a `Drawing` table whose
revision and status columns are the drawing's own fields
([DEC-037](DEC-037-revision-snapshots.md), [DEC-039](DEC-039-approval-in-vendor-fields.md)),
and a `WorkHistory` table with one row per change ([DEC-037](DEC-037-revision-snapshots.md)).

## Alternatives considered

- Generate the DDL from the class definitions. A hand-written file is shorter to
  review for one small schema, and the test checks that the definitions describe it.
- Test against SQLite, as the product's default project database is. DEC-027 chose
  SQL Server, and the product supports SQL Server projects too (REF-TECH-016).
- Run Azure SQL Edge, which has an ARM image. Microsoft retired it, and its engine
  differs from SQL Server 2022.

## Owner's words

Given in the session that set the night run, on 2026-10-13, and recorded in
[DEC-048](DEC-048-night-delegation.md).

The owner said:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make.
> Add decisions you made to the log. I dont want ahytning waiting on me while I am
> not here and blocking you

## Evidence

- REF-TECH-016 and REF-TECH-017 in the
  [reference register](../LIONG-REF-001-reference-register.md#vendor-storage-references).
- The live schema tests passed on SQL Server 2022 (16.0, image `2022-latest`)
  under OrbStack on 2026-10-13.
