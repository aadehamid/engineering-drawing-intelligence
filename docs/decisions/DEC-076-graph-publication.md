# DEC-076: A graph snapshot is published once to Neo4j under its content hash, and the cross-sheet query reads one snapshot

Status: Decided
Date: 2026-10-14

## Context

MILESTONE-001 steps 4 and 5 publish one immutable engineering graph snapshot and query
a known cross-sheet connection with its source evidence
([the build runbook](../LIONG-011-build-runbook.md)). [DEC-056](DEC-056-neo4j-for-the-slice.md)
chose Neo4j Community 2026.09.0, [DEC-057](DEC-057-cypher-query-no-ui.md) a parameterized
Cypher query, and [DEC-067](DEC-067-exact-pins.md) exact pins. How the snapshot is stored
and named was left open. The agent decided it during the night run of 2026-10-14, under
the owner's delegation in [DEC-073](DEC-073-second-night-delegation.md). The owner can
reverse any of it.

## Decision

1. **Snapshot ID.** A snapshot's ID is the SHA-256 of its content: the source revision,
   every node and every edge, with their evidence, in a fixed order. The same graph
   always gets the same ID.
2. **Published once.** Publishing an ID that already exists changes nothing if the
   stored content still hashes to that ID, and is refused if it does not. A publish is
   one transaction, so a reader sees the whole snapshot or none of it.
3. **Storage.** Each node is an `Entity` with its snapshot ID, its ID, kind, tag or
   name, and its evidence as a JSON string; a uniqueness constraint covers snapshot ID
   plus node ID, which Community supports. Each edge is a relationship typed by its
   kind (FLOW, ON_SHEET, INSTRUMENT_PARENT, CROSS_SHEET_REFERENCE) and carries the
   snapshot ID and evidence. A `Snapshot` node holds the receipt's facts.
4. **Query.** `scripts/graph_publish.py query` runs one Cypher query, parameterized by
   snapshot ID and an optional connector label. It returns each cross-sheet connection
   with both ends' sheets and the evidence of the ends and the link.
5. **Pins.** The `neo4j` driver is 6.3.1, released 2026-09-15, under Apache-2.0 with parts under
   the PSF Python-2.0 license (its metadata: `Apache-2.0 AND Python-2.0`): 6.4.0, of
   2026-10-05, is younger than DEC-067's 14 days. The image is
   `neo4j@sha256:6f3f17e72d69bb6f26b03f6186f5afb15a201f8b460bb69b0cd8030717f9f01a`,
   the multi-architecture index Docker Hub served for `2026.09.0-community` on
   2026-10-14, used in CI as a service container.

## Alternatives considered

- Name snapshots by time or by a counter. A content hash makes "immutable" checkable:
  a changed stored snapshot no longer matches its own name.
- One relationship type with a `kind` property. Typed relationships keep the Cypher
  query plain.

## Owner's words

Given on 2026-10-14 and recorded in [DEC-073](DEC-073-second-night-delegation.md).

The owner answered:

> you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity

## Evidence

- `scripts/test_graph_publish.py`: the stored graph equals the published one, a second
  publish changes nothing, a changed stored snapshot is refused, a failed publish leaves
  nothing, and the query returns R0's cross-sheet connection with its evidence.
- REF-TECH-003 in [LIONG-007](../LIONG-007-stack-and-architecture.md).
- The [delivery playbook](../delivery-playbook.md)'s section 5, added in this decision's
  pull request as DEC-071 requires.
