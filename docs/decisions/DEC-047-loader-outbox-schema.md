# DEC-047: The outbox lives in a third, non-vendor schema in the same SQL Server database

Status: Decided
Date: 2026-10-12

## Context

LIONG-006 and LIONG-007 had the synthetic backend commit each revision and a
pending-event record in one transaction, with an outbox table in the backend.
[DEC-031](DEC-031-stored-data-not-behaviour.md) keeps the vendor-style backends to
the data each application saves, and neither product has an outbox. Q35 asked
where the outbox goes instead. A follow-up reply explained what an outbox is
before the owner answered.

## Decision

The owner chose option (b) of Q35:

> In a third, non-vendor schema in the same SQL Server database. The loader that
> applies a snapshot writes the revision and its pending event in one transaction.
> The two vendor schemas stay pure (DEC-031), and LIONG-006's recovery design stays
> as it is. This adds a third schema to DEC-028's "two schemas inside one database".

## Alternatives considered

- Option (a): the outbox in the pipeline's own control store, outside the backend
  database. The revision and its event would no longer be committed together, and
  LIONG-006's recovery tests would change.

## Owner's words

Asked as Q35 of the synthetic-data interview on 2026-10-12. Markdown formatting is
removed from the quotes below.

> Where the outbox lives:
>
> (a) In the pipeline's own control store, outside the backend database. The
> pipeline finds new revisions by reading each snapshot's own revision fields
> (DEC-037). The revision and its event are no longer committed together, so the
> recovery tests in LIONG-006 change: reconciliation, not an atomic event,
> guarantees nothing is missed.
>
> (b) In a third, non-vendor schema in the same SQL Server database. The loader
> that applies a snapshot writes the revision and its pending event in one
> transaction. The two vendor schemas stay pure (DEC-031), and LIONG-006's
> recovery design stays as it is. This adds a third schema to DEC-028's "two
> schemas inside one database".

The recommendation given with it:

> (b). It keeps the recovery tests LIONG-006 already specifies, without a
> two-phase commit across two databases, and it keeps the outbox out of both
> vendor schemas. Your answer goes into a decision record. The cleanup PR then
> rewrites LIONG-006:209 and LIONG-007:117, :189 and :217 to match.

The owner first asked "what is an outbox?". After the explanation:

The owner answered:

> go with b

## Evidence

- `docs/LIONG-006-synthetic-data.md`, "Recovery fixtures", which this keeps.
- [DEC-028](DEC-028-one-database-two-schemas.md) keeps its two vendor schemas; this
  adds a non-vendor schema beside them.
