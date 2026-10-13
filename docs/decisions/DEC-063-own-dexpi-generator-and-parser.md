# DEC-063: LIONG writes its own DEXPI 2.0.1 generator and parser for the supported subset, on lxml

Status: Decided
Date: 2026-10-13

## Context

No Python library reads or writes DEXPI 2.0. pyDEXPI v1.2.0 supports DEXPI 1.3
only, under AGPL-3.0, and its maintainer gives no date for 2.0. The other Python
tools found are also 1.x.

## Decision

LIONG writes its own small generator and parser for the supported subset, on
lxml. pyDEXPI is excluded for DEXPI 2.0, because it supports only 1.3 and its AGPL
license would apply to LIONG. No part of the slice claims 2.0 support through a
1.x tool, so LIONG-011's stop rule on a silent downgrade does not trigger.

## Alternatives considered

- Wait for pyDEXPI's 2.0 release. It has no date, and its license is AGPL.
- Use pyDEXPI with DEXPI 1.3 now. That is the downgrade LIONG-011 forbids without
  a documented change.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- REF-STD-008 in LIONG-REF-001.
- Question Q9 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
