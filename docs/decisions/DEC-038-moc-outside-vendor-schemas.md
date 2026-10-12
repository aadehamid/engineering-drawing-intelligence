# DEC-038: MOC records stay a separate source representation, outside both vendor schemas

Status: Decided
Date: 2026-10-12

## Context

Asked as Q26 (Where MOC records live) in round 4 of the synthetic-data interview,
after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q26:

> Yes. Putting MOC tables into the vendor schemas would make them less like the
> real products.

## Alternatives considered

- MOC tables inside the vendor schemas.

## Owner's words

Asked as Q26 in round 4 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> Neither product stores MOC records. Should MOC-1, MOC-2 and the rest stay a
> separate source representation with their own keys, as LIONG-006 already lists
> them, and stay out of both vendor schemas?

The recommendation given with it:

> Yes. Putting MOC tables into the vendor schemas would make them less like the
> real products.

The owner answered:

> Agree on all

The answer covered every question in round 4, Q24 to Q29.

## Evidence

- LIONG-006 lists Management of Change records as their own representation.
