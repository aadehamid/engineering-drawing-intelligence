# DEC-019: The generator writes backend files, and a separate loader applies them

Status: Decided
Date: 2026-10-11

## Context

LIONG-006 requires a SHA-256 of every emitted file. LIONG-009 gives the generator
its own identity, which writes input and truth packages and nothing else. The
question named PostgreSQL as the target. [DEC-027](DEC-027-sql-server-on-azure.md)
later replaced that engine; this decision holds for any engine.

## Decision

The generator emits the backend as files: a SQL schema, data scripts, and a
manifest. A separate loader applies them to the backend database. The generator
never writes into a live database.

## Alternatives considered

- The generator writes straight into a live database. The output would have no
  file hashes, and the generator would share an identity with the source database.

## Owner's words

Asked as Q5 of the synthetic-data interview on 2026-10-11:

> Should the generator emit the backend as files, meaning a SQL schema plus data
> scripts and a manifest, that a separate loader then applies to PostgreSQL? The
> alternative is for the generator to write straight into a live database.

The owner answered:

> Q5. Agreed

## Evidence

- LIONG-006, the generation manifest paragraph at line 226.
- `docs/LIONG-009-governance-and-operations.md:57`, the generator identity.
