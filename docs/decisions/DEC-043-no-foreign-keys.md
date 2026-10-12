# DEC-043: The vendor-style relationship tables have no foreign-key constraints

Status: Decided
Date: 2026-10-12

## Context

Asked as Q31 (Foreign keys in the vendor-style schemas) in round 5 of the
synthetic-data interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q31:

> Yes. Both products manage integrity in the application, as far as the research
> shows, and the mandatory checks in LIONG-006 (SCN-005) belong to our pipeline,
> not the database. The schema notes will flag this as an inference.

## Alternatives considered

- Enforce foreign keys, so SQL Server refuses a broken reference at load time.

## Owner's words

Asked as Q31 in round 5 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> DEC-015's invalid variant has a connection that points at a missing object. If
> the schema enforces foreign keys, SQL Server refuses to load that variant, and
> the pipeline never sees the error it must catch. Public sources don't say
> whether either product enforces foreign keys on its relationship tables, so that
> part is my inference. Should the relationship tables have no foreign-key
> constraints, so a broken reference loads and the pipeline's validation must
> reject it?

The recommendation given with it:

> Yes. Both products manage integrity in the application, as far as the research
> shows, and the mandatory checks in LIONG-006 (SCN-005) belong to our pipeline,
> not the database. The schema notes will flag this as an inference.

The owner answered:

> Agree on all

The answer covered every question in round 5, Q30 to Q34.

## Evidence

- LIONG-006, SCN-005 (mandatory checks).
- That neither product enforces foreign keys on its relationship tables is an
  inference; public sources do not say.
