# DEC-058: The slice's manifests and publication receipt are JSON files in a run output folder, with no PostgreSQL

Status: Decided
Date: 2026-10-13

## Context

The slice needs a source manifest, an exchange manifest, a graph manifest and a
publication receipt. [LIONG-007](../LIONG-007-stack-and-architecture.md) proposes PostgreSQL as the control store.

## Decision

One run writes one output folder holding the four records as JSON files.
PostgreSQL stays out of the slice until later work needs revision history.

## Alternatives considered

- PostgreSQL 18.6 as the control store now, as LIONG-007 proposes. The slice
  has one run of one fixture and no history to keep.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q4 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
