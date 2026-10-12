# DEC-034: R0 is also generated in SmartPlant form, as a test fixture for the two mappings

Status: Decided
Date: 2026-10-11

## Context

[DEC-029](DEC-029-two-canonical-worlds.md) gives each vendor its own world, which
leaves nothing to compare between the two mappings. Q23 asked whether to drop the
fixture that keeps that comparison.

## Decision

The owner kept the cross-check fixture that Q22 and Q23 described: R0 also
emitted in SmartPlant form, only to check that the two mappings agree.

## Alternatives considered

- Drop the fixture and add a cross-check later if the mappings disagree. Without
  it, no automatic test checks that the SmartPlant mapping handles R0's bypass.

## Owner's words

Asked as Q23 of the synthetic-data interview on 2026-10-11:

> The one thing your answer leaves open is the extra test fixture I suggested: R0
> also emitted in SmartPlant form, only to check that the two mappings agree.
>
> Should we drop that fixture and keep exactly two worlds, each in one schema? We
> can add a cross-check later if the two mappings start to disagree.

The recommendation given with it:

> Keep it, but as test data only. It costs one extra run of the generator, needs
> no new expected results, and is the only automatic check that the SmartPlant
> mapping gets R0's bypass right. If you'd rather keep things simple, dropping it
> is fine.

The owner answered:

> Q3: Let us keep the cross check

The answer is labelled Q3, but Q3 had been answered in the first round, and Q23
was the only open question about the cross-check.

## Evidence

- LIONG-006, where R0's expected results are written.
