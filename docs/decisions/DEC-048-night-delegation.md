# DEC-048: The agent decides open questions for the owner during the night run of 2026-10-13

Status: Decided
Date: 2026-10-13

## Context

On 2026-10-13 the owner set an unattended night run: finish every open item, then
complete the synthetic data. Some of that work, such as the Plant 3D-style schema,
had questions still open for the owner. This repository treats a decision as a
proposal until the owner's words are recorded, so without a delegation the run
would stop at the first open question.

## Decision

The owner delegated the open questions of the night run to the agent:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make

The agent records each decision it makes as Decided, citing this record, in the
place the question lives, with its evidence. The agent also lists each one in the
morning log for the owner. The owner can reverse any of them. Where the evidence
leaves a choice absolutely unclear, the agent leaves a note instead of deciding.

The delegation covers the night run of 2026-10-13 only.

## Alternatives considered

- Record each decision as Proposed and build nothing that depends on it. The owner
  rejected this, because it would leave work waiting on the owner overnight.

## Owner's words

Given in the session that set the night run, on 2026-10-13, after the agent said it
would record decisions as Proposed. The words are quoted as typed.

The owner said:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make.
> Add decisions you made to the log. I dont want ahytning waiting on me while I am
> not here and blocking you

The owner also gave the run's permission:

> I am giving you my permision to run commands and merge PR as needed for this
> night's goal

## Evidence

- [DEC-024](DEC-024-decision-records.md): each decision has its own record.
- `AGENTS.md`, "Decisions": decisions are proposals until the owner's words are
  recorded. This record supplies them for the night run.
