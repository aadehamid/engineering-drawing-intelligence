# DEC-061: The slice targets DEXPI 2.0.1, pinned at the specification's V2.0.1 tag

Status: Decided
Date: 2026-10-13

## Context

[LIONG-003](../LIONG-003-sources-and-ontology.md) inspected DEXPI 2.0.0 and left
2.0.0 versus 2.0.1 open. DEXPI released 2.0.1 on 2026-09-30 as a fix release
intended to replace 2.0. Nothing in the repository was built on 2.0.0.

## Decision

The slice targets DEXPI 2.0.1, at the specification repository's V2.0.1 tag.
Its XSD and reference P&ID are pinned by SHA-256 when the GATE-001 work lands.
LIONG-003 and [LIONG-REF-001](../LIONG-REF-001-reference-register.md) move their
target from 2.0.0 to 2.0.1.

## Alternatives considered

- Stay on 2.0.0, the version LIONG-003 inspected. 2.0.1 replaces it and
  corrects the Plant model.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- [DEXPI 2.0.1 announcement](https://dexpi.org/dexpi-2-0-1-specification-published-the-update-replacing-dexpi-2-0/),
  and REF-STD-001 in LIONG-REF-001.
- Question Q7 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
