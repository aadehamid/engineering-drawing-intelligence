# DEC-067: Every new slice component is pinned exactly, at the latest release at least 14 days old

Status: Decided
Date: 2026-10-13

## Context

GATE-TECH-002 in [LIONG-007](../LIONG-007-stack-and-architecture.md) asks for a locked package set with no floating latest
versions.

## Decision

lxml and the `neo4j` driver are pinned exactly in `pyproject.toml` and
`uv.lock`. The Neo4j image is pinned by digest in CI and local use. Each version is
the latest release at least 14 days old when its pull request lands, and LIONG-007
records it with its license.

## Alternatives considered

- Version ranges. They let a lock refresh change a result without a pull
  request.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q12 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
