# DEC-014: A skipped question in a decision round counts as agreement

Status: Decided
Date: 2026-10-11

## Context

Decision interviews in this repository ask the owner several numbered questions
per round, each with a recommended answer. The way-of-working standard
(`references/deciding.md`) asks for this convention to be agreed with the owner.

## Decision

A question the owner does not answer in a decision round counts as agreement
with the recommendation given for it. The record of that decision quotes the
round in which it was asked.

## Alternatives considered

- An unanswered question stays open until the owner answers it. This is safer
  against silent approval but stalls every round on questions the owner had no
  objection to.

## Owner's words

Asked as Q12 of the synthetic-data interview on 2026-10-11:

> When you don't answer a question in a decision round, should I treat that as
> agreement with my recommendation?

The owner answered:

> Q12: yes

## Evidence

- Recorded as DEC-014 in the [decision register](../LIONG-REG-001-decisions.md)
  in `9a5f61f`, after the Cursor review of #6 asked for a repository record.
- Applied by `AGENTS.md` ("Decisions").
