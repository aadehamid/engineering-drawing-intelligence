# DEC-066: The parser also reads DEXPI's own 2.0.1 reference P&ID and reports what it does not support

Status: Decided
Date: 2026-10-13

## Context

Every DEXPI file the slice generates is written by LIONG. DEXPI's 2.0.1
reference P&ID is the one independent 2.0.1 file available.

## Decision

The parser reads DEXPI's 2.0.1 `reference_pid.xml`. It extracts the classes in
the supported subset and reports everything else as unsupported, without failing.
This shows the parser reads a file LIONG did not write.

## Alternatives considered

- Test the parser only on LIONG's own files. That cannot catch a parser that
  only understands its own generator's output.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q11 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
