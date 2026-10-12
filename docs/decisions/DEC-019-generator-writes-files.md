# DEC-019: The generator writes backend files, and a separate loader applies them

Status: Decided
Date: 2026-10-11

## Context

LIONG-006 requires a SHA-256 of every emitted file. LIONG-009 gives the generator
its own identity, which writes input and truth packages and nothing else. The
question named PostgreSQL as the target. [DEC-027](DEC-027-sql-server-on-azure.md)
later replaced that engine. Whether files and a loader carry over to SQL Server is
not recorded; the owner has not said.

## Decision

The owner accepted the recommendation given with Q5:

> Yes, files. LIONG-006 requires a SHA-256 of every emitted file, and file output
> keeps the generator and the source database as separate identities
> (LIONG-009:57).

## Alternatives considered

- The generator writes straight into a live database. The output would have no
  file hashes, and the generator would share an identity with the source database.

## Owner's words

Asked as Q5 of the synthetic-data interview on 2026-10-11:

> Should the generator emit the backend as files, meaning a SQL schema plus data
> scripts and a manifest, that a separate loader then applies to PostgreSQL? The
> alternative is for the generator to write straight into a live database.

The recommendation given with it:

> Yes, files. LIONG-006 requires a SHA-256 of every emitted file, and file output
> keeps the generator and the source database as separate identities
> (LIONG-009:57).

The owner answered:

> Q5. Agreed

DEC-027 later replaced PostgreSQL as the engine.

## Evidence

- LIONG-006, the generation manifest paragraph at line 226.
- `docs/LIONG-009-governance-and-operations.md:57`, the generator identity.
