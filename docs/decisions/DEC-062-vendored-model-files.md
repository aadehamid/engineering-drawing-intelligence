# DEC-062: Pinned copies of the DEXPI model files live in the repository, and validation never fetches over the network

Status: Decided
Date: 2026-10-13

## Context

DEXPI XML files import `Core.xml` and `Plant.xml` from `data.dexpi.org`. That
host failed TLS hostname verification during LIONG-003's inspection and did not
respond on 2026-10-13.

## Decision

The repository keeps pinned copies of the 2.0.1 model files the slice needs,
taken from the V2.0.1 specification repository or DEXPI's published supporting
materials. Each copy carries its SHA-256 and the CC BY 4.0 attribution. Validation
maps each import to its pinned copy and never fetches anything over the network.
TLS verification is never disabled. If neither source has the XML files, the agent
brings that back to the owner rather than generating them.

## Alternatives considered

- Fetch the model files at validation time. The host is unreliable, and a
  network fetch makes the checks depend on it.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- REF-DATA-001's access failure in LIONG-REF-001.
- Question Q8 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
