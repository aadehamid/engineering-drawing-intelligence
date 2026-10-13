# DEC-068: The glossary defines supported subset

Status: Decided
Date: 2026-10-13

## Context

Several documents use "supported subset" without defining it.

## Decision

GLOSSARY.md defines supported subset as the DEXPI classes and properties LIONG
generates and reads. Anything outside it is reported as unsupported, never dropped
silently.

## Alternatives considered

- Leave the term undefined. Readers would each read their own meaning into it.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q13 of the round, and ARCHITECTURE.md's description of the subset.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
