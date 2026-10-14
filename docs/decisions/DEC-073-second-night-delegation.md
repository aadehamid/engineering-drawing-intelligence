# DEC-073: The agent decides open questions for the owner while building MILESTONE-001's slice

Status: Decided
Date: 2026-10-14

## Context

On 2026-10-14 (UTC) the owner set a second unattended night run: build MILESTONE-001
steps 2 to 6 ([the build runbook](../LIONG-011-build-runbook.md)) on the choices in
DEC-055 to DEC-072, and land the closure evidence for GATE-001 and GATE-003. The
delegation in [DEC-048](DEC-048-night-delegation.md) covered only the night of
2026-10-13, so this run needs its own.

The agent proposed the run's goal, order and stop conditions, and the owner approved
them. The goal: vendor the pinned DEXPI 2.0.1 files; extract source records without
reading the answer key; an lxml generator and parser; the four-stage validation; a
Neo4j publish with the cross-sheet query; an exact comparison with the answer key,
including the Rbad rejection; and the gates' closure evidence. The run stops for a
question the evidence cannot settle, and for anything irreversible outside the
repository: spending money, publishing, deleting remote data, or rewriting main.

How the agent applies the delegation is its own practice, as under DEC-048: it records
each decision as Decided, citing this record, where the question lives, with its
evidence, and lists it in the morning log. The owner can reverse any of them.

## Decision

The owner delegated the run's open questions to the agent, to be settled from the
project's data and from high-quality external sources.

## Alternatives considered

- Reuse DEC-048. Its permission was "for this night's goal", the night of 2026-10-13,
  so it does not cover this run.

## Owner's words

Given on 2026-10-14 (UTC), in answer to the agent's three requests: permission to run
commands and merge pull requests, a delegation of decisions, and approval of the
proposed goal and stop conditions. The owner numbered the answers 1 to 3; the numbers
are left out below so each answer renders as plain text. The words are otherwise quoted
as typed.

The owner answered:

> you have my permission

> you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity

> This is right

## Evidence

- [DEC-048](DEC-048-night-delegation.md): the first night's delegation, limited to that night.
- [DEC-055](DEC-055-slice-choices-close-gates-on-evidence.md): both gates stay open until a pull request
  lands their closure evidence.
