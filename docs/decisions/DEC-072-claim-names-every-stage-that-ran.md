# DEC-072: A DEXPI validity claim names every stage that ran, including the reference checks

Status: Decided
Date: 2026-10-13

Amends DEC-065

## Context

[DEC-065](DEC-065-claim-names-stages-that-ran.md) says a claim names only the
stages that ran, and gives two example claims. Both examples leave out stage 2 of
[DEC-064](DEC-064-four-stage-dexpi-validation.md), the reference checks, although
it ran in both cases. The Cursor bot's review of pull request 32 found the same
omission in the delivery playbook's claim example, which was fixed there. The
record and the playbook then taught two wordings for the same situation.

## Decision

DEC-065's rules stand: a document or report claims only the stages that ran, and
it names each of them. No claim says DEXPI-conformant or certified. The two
examples change to name the reference checks:

1. With all four stages of DEC-064, the claim reads: valid against the DEXPI 2.0.1
   XSD, its reference checks and the 2.0.1 Core and Plant models for the classes
   LIONG uses, and passes LIONG's rules.
2. If stage 3 is not built yet, the claim reads: passes the DEXPI 2.0.1 XML schema,
   its reference checks and LIONG's rules.

## Alternatives considered

- Keep DEC-065's examples. Both are true, because neither claims a check that did
  not run, but a reader would not learn that references were checked.

## Owner's words

Asked on 2026-10-13, after the agent explained the gap: should the agent record
the corrected examples, and add them to pull request 32 or to a follow-up pull
request?

The owner answered:

> yes, add it to #32

## Evidence

- DEC-065's Decision section holds the two original examples.
- The bot's comment on the playbook's claim example, on pull request 32.
