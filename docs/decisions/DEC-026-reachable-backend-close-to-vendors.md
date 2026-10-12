# DEC-026: The backend database is reachable from any of the owner's machines and runs on the engine closest to both vendors

Status: Decided
Date: 2026-10-11

## Context

The owner chose Neon in Q8. Q14 asked whether Neon should become a third
exception to the open-source condition, after Cloudflare and Databricks Free
Edition (DEC-009). The vendor research had found that SmartPlant P&ID runs on
Oracle or SQL Server and AutoCAD Plant 3D on SQLite or SQL Server.

## Decision

The backend database meets two requirements:

- It is hosted, so the owner can reach the data from any of the owner's machines.
  The host need not be Neon.
- It runs on the engine closest to what SmartPlant and Autodesk use, unless that
  engine proves really difficult for this project. Either way, the two schemas stay
  very close to each vendor's.

[DEC-027](DEC-027-sql-server-on-azure.md) applies both requirements.

## Alternatives considered

- Neon as a third recorded exception, which Q14 recommended. The owner's reason
  for Neon was access from any machine, not Neon itself.

## Owner's words

Asked as Q14 of the synthetic-data interview on 2026-10-11:

> Should Neon be added as a third permitted exception, on the same terms as
> DEC-009?

The owner answered:

> Q14: The only reason I am chosing Neon
>
> Because I want to be able to host the database so that I can get the data from
> any of my systems. I'm not married to Neon. I just want to make sure that I'm
> able to get the data from any of my machines, not only from this machine. That's
> the only reason why I'm choosing Neon.
>
> On the questions of the backend database that SmartPlant and Autodesk use, I
> think we should also choose the backend that is very close to their backend. For
> example, if SmartPlant is using whatever SmartPlant is using, if SmartPlant is
> using, if Autodesk is using SQL Server, we should also choose to use SQL Server.
> And also if SmartPlant is using, if SmartPlant and Autodesk are using SQL Server,
> we should also use SQL Server, unless SQL Server becomes really difficult for us
> for this specific project. Maybe it's easier to use Postgres, but we must use the
> schema that is very, very close to SmartPlant and also very, very close to
> Autodesk. We should have two of those schemas so that we can learn and work with,
> learn how to work with data, the SmartPlant backend and also the Autodesk
> backend.

## Evidence

- The vendor research run during the interview, summarized in the Context section.
