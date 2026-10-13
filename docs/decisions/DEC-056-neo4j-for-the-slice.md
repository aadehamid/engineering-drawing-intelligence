# DEC-056: The slice's graph store is Neo4j Community 2026.09.0, run from a pinned image locally and in CI

Status: Decided
Date: 2026-10-13

## Context

Step 4 of MILESTONE-001 publishes one immutable graph snapshot, and step 5
queries it. [LIONG-007](../LIONG-007-stack-and-architecture.md) names Neo4j Community as the first graph candidate and Apache AGE
as the fallback, under GATE-TECH-001.

## Decision

The slice publishes its graph to Neo4j Community 2026.09.0 (GPLv3), pinned to
an exact image. It runs in a local container and as a CI service container, the
way SQL Server does now. GPLv3 is acceptable for a local baseline that is not
shipped. GATE-TECH-001's full comparison with AGE stays open beyond the slice.

## Alternatives considered

- Apache AGE on PostgreSQL, LIONG-007's fallback. No version has been inspected.
- No database yet: build the graph in memory with networkx and publish it as an
  immutable file with a manifest.
- SQL Server's own graph tables, reusing the database the slice already runs.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q2 of the round, and REF-TECH-003 in LIONG-007.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
