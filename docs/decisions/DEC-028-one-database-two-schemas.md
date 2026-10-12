# DEC-028: Both vendor schemas live in one database

Status: Decided
Date: 2026-10-11

## Context

Q15 recommended one database per simulated application, each with its own keys
and users, so that no key from one could leak into the other.

## Decision

The SmartPlant-style and Plant 3D-style schemas are two schemas inside one
database. [DEC-027](DEC-027-sql-server-on-azure.md) sets the engine.

## Alternatives considered

- A separate database per simulated application, which Q15 recommended. It isolates
  keys more strongly, at the cost of a second hosted database.

## Owner's words

Asked as Q15 of the synthetic-data interview on 2026-10-11:

> Should the SmartPlant-style backend and the Plant 3D-style backend each get its
> own PostgreSQL database, with its own keys and users? The alternative is two
> schemas inside one database.

The owner answered:

> Q15: Those two schemers inside one database, but referred to the answer to my two
> question 14 as well.

## Evidence

- [DEC-047](DEC-047-loader-outbox-schema.md) later adds a third, non-vendor schema
  to the same database, for the loader's outbox.

- Q21, recorded in DEC-027, restated one database with two schemas, and the owner
  agreed.
