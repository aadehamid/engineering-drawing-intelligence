# DEC-055: This round chooses components for MILESTONE-001's slice only, and a gate closes when a PR lands its closure evidence

Status: Decided
Date: 2026-10-13

## Context

GATE-001 (DEXPI artifact, encoding, parser and validation) and GATE-003
(component versions, licenses and interoperability) in [the decision register](../LIONG-REG-001-decisions.md) block MILESTONE-001.
Every component for the milestone's steps 2 to 6 was still only proposed in [LIONG-007](../LIONG-007-stack-and-architecture.md).

## Decision

The decisions in this round (DEC-056 to DEC-069) choose components and versions
for MILESTONE-001's slice only. A decision picks the parts; it does not close a
gate. GATE-001 closes when a pull request lands its closure evidence: pinned
artifacts, a license record, and positive and negative round-trip fixtures. The
slice's part of GATE-003 closes when a pull request lands the dependency lock and
the compatibility tests. The rest of GATE-003 stays open.

## Alternatives considered

- Choose the whole long-term stack now. Nothing beyond the backend generator and
  loader exists yet, so the slice is the first chance to test any choice.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- The register's gate rows, and LIONG-007's proposed components and open gates.
- Question Q1 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
