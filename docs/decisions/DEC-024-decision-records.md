# DEC-024: Each decision has its own record, and the register stays the summary

Status: Decided
Date: 2026-10-11

## Context

Decisions lived only as rows in the `LIONG-REG-001` register, with no quoted owner
words. The way-of-working standard asks for one record per decision.

## Decision

The owner accepted the recommendation given with Q11:

> Yes. Keep the register as the summary and put the evidence in per-decision
> records. Today's answers (Q1–Q9) would become the first records.

## Alternatives considered

- Keep decisions only in the register table. The owner's words would have no
  place, and nothing would check a row against its evidence.

## Owner's words

Asked as Q11 of the synthetic-data interview on 2026-10-11:

> Decisions currently live as rows in the LIONG-REG-001 table. They have no quoted
> owner words and no one-record-per-decision files, which way-of-working asks for.
> Should I add a docs/decisions/ folder with an index, one record per decision
> quoting your words, and have the check script verify the records against the
> index? The register table would stay as the summary, with each row linking to
> its record.

The recommendation given with it:

> Yes. Keep the register as the summary and put the evidence in per-decision
> records. Today's answers (Q1–Q9) would become the first records.

The owner answered:

> Q11: Follow way of working skill recommendation

## Evidence

- Merged in #10 (`4c547a0`). The format is in [the index](README.md).
