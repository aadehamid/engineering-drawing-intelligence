# DEC-023: The way-of-working guardrails land as five pull requests before the synthetic-data work

Status: Decided
Date: 2026-10-11

## Context

The way-of-working standard requires an agent instruction file, a check script
with CI and a pre-push hook, a shared figures tool, a review standards file, and
decision records. The repository had none of them.

## Decision

The owner accepted the recommendation given with Q10:

> Yes, in that order. Each PR is small, and the first two are mostly wiring around
> the doc checks that already exist.

## Alternatives considered

- Build the guardrails alongside the synthetic-data work. Early changes would
  land without the checks that the later ones rely on.

## Owner's words

Asked as Q10 of the synthetic-data interview on 2026-10-11:

> Should I build the five guardrail steps above as five small PRs before the
> glossary PR and the generator work?

The recommendation given with it:

> Yes, in that order. Each PR is small, and the first two are mostly wiring around
> the doc checks that already exist.

The owner answered:

> Q10: Agreed

The five steps were: AGENTS.md; scripts/check.sh with CI and a pre-push hook; a
shared figures tool; a review standards file; and decision records.

## Evidence

- Merged as #6 (`e5866db`), #7 (`fdf0ab1`), #8 (`eca829b`), #9 (`60c188d`), and
  #10 (`4c547a0`).
