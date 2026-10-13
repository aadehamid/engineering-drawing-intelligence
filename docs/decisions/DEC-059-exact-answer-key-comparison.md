# DEC-059: Step 6 compares the published graph with the answer key and requires an exact match

Status: Decided
Date: 2026-10-13

## Context

Step 6 of MILESTONE-001 checks the published graph against the expected result.
The generator writes R0's answer key to `fixtures/answer-keys/p3d-r0.json`.

## Decision

Step 6 is a Python comparison. It normalizes the published graph into the answer
key's node and edge form and requires exact equality: 17 nodes and 31 edges for
R0, and Rbad rejected with its named reason. It writes a JSON report and a short
Markdown report. It runs in the repository's existing `unittest` style, in
`scripts/check.sh` and in CI.

## Alternatives considered

- A tolerance or a score instead of exact equality. The fixture is synthetic
  and fully known, so any difference is a defect.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q5 of the round, and SCN-001 and SCN-005 in [LIONG-006](../LIONG-006-synthetic-data.md).
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
