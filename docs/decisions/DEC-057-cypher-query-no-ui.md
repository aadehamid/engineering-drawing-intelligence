# DEC-057: Step 5 is a parameterized Cypher query run through the official neo4j Python driver, with no UI in the slice

Status: Decided
Date: 2026-10-13

## Context

Step 5 of MILESTONE-001 queries the published graph for the cross-sheet
connection from X1 to X2 with its source evidence. The interface choice between
Dash and FastAPI with Cytoscape.js is open under GATE-TECH-008.

## Decision

Step 5 is a parameterized Cypher query run from Python through the official
`neo4j` driver. A test and a small command-line tool call it, and it returns the
X1 to X2 cross-sheet connection with its source evidence. Any UI stays under
GATE-TECH-008 for later.

## Alternatives considered

- Build a Dash or FastAPI and Cytoscape.js interface now. The slice proves the
  query, and a UI adds work it does not need.

## Owner's words

Asked in rounds 1 and 2 of the GATE-001 and GATE-003 decision round on
2026-10-13. Round 2 asked the owner to answer all thirteen questions together.

The owner answered:

> yes to all. And also will the below work for DEXPI validation

## Evidence

- Question Q3 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
