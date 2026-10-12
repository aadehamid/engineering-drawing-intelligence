# DEC-022: PostgreSQL on Neon hosts the synthetic backend

Status: Superseded
Date: 2026-10-11
Superseded by DEC-027 on 2026-10-11

## Context

LIONG-007 proposes PostgreSQL for the synthetic backend, and that proposal
(DEC-106) is not approved. Because the generator writes SQL files
([DEC-019](DEC-019-generator-writes-files.md)), it has to target one SQL dialect.

## Decision

PostgreSQL is the synthetic backend engine, hosted on Neon. The question also
proposed deciding the graph database later; the owner's answer did not address
that, so this record does not decide it.

## Alternatives considered

- Leave the backend engine open. The generator cannot write SQL without a dialect.

## Owner's words

Asked as Q8 of the synthetic-data interview on 2026-10-11:

> Should we confirm PostgreSQL for the backend now, and leave the graph database
> choice until MILESTONE-001's graph step?

The recommendation given with it:

> Yes. Confirm PostgreSQL for the backend now. Decide the graph database later,
> from the same R0 tests.

The owner answered:

> Q8: Postgressql confirmed. Let us host it on https://neon.com/

## Evidence

- LIONG-007, the proposed backend database.
- [DEC-027](DEC-027-sql-server-on-azure.md) replaced this decision after the
  vendor research showed neither SmartPlant P&ID nor AutoCAD Plant 3D runs on
  PostgreSQL.
