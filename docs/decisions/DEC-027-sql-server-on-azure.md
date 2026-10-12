# DEC-027: Both backends run on SQL Server, hosted on an Azure SQL Database free-offer database

Status: Decided
Date: 2026-10-11
Amends DEC-022

## Context

SQL Server is the only engine that both SmartPlant P&ID and AutoCAD Plant 3D
support, which [DEC-026](DEC-026-reachable-backend-close-to-vendors.md) makes the
deciding test. It replaces PostgreSQL from
[DEC-022](DEC-022-postgresql-on-neon.md).

## Decision

The owner accepted the recommendation given with Q21:

> (a). It's the only engine both vendors support, it meets your any-machine
> requirement, and the pause setting caps the cost at zero.

Option (a) is "SQL Server on Azure, as just described", where the question quoted
under Owner's words gives the description.

## Alternatives considered

- PostgreSQL on Neon. Easier to run, but neither vendor uses it.

## Owner's words

Asked as Q21 of the synthetic-data interview on 2026-10-11:

> Should both vendor schemas live in one SQL Server database, as two schemas,
> hosted on an Azure SQL Database free-offer database set to pause when it hits a
> limit so it can never bill? A local SQL Server container would serve tests and
> CI, and the decision would be recorded as a new exception to the open-source
> condition. Pick one:
>
> (a) SQL Server on Azure, as just described.
>
> (b) PostgreSQL on Neon, which is easier but further from both vendors.

The recommendation given with it:

> (a). It's the only engine both vendors support, it meets your any-machine
> requirement, and the pause setting caps the cost at zero.

The owner answered:

> Q21: agreed

## Evidence

- Free offer: each database gets 100,000 vCore-seconds of compute a month and
  32 GB of data, and can pause at the limit instead of billing
  ([Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-sql/database/free-offer?view=azuresql)).
- SQL Server 2025 Express is free for production use, and Developer edition is free
  for development and test
  ([SQL Server 2025 editions](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025?view=sql-server-ver17)).
- Not yet verified: whether the SQL Server container runs natively on Apple
  Silicon. It must be checked before the local setup relies on it.
- Not part of the decision: LIONG-007 still proposes PostgreSQL, and the DEC-009
  exception list does not yet name SQL Server or Azure. The author plans to edit
  both in a later pull request. The graph database is not decided.
