# DEC-060: Each slice step is a plain Python command, chained by one script, with no orchestrator

Status: Decided
Date: 2026-10-13

## Context

[LIONG-007](../LIONG-007-stack-and-architecture.md) proposes Dagster 1.13.25 as an optional orchestrator, under GATE-TECH-005.

## Decision

Each step of the slice is a plain Python command. One script chains them. Dagster
stays deferred.

## Alternatives considered

- Dagster now. An orchestrator adds nothing for one run of one fixture.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q6 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
