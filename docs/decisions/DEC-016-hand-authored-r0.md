# DEC-016: R0 is hand-authored, and seeds apply only to procedurally generated worlds

Status: Decided
Date: 2026-10-11

## Context

LIONG-006 proposes integer seed `2701006` for the documented development world.
R0 is written out edge by edge in LIONG-006, so a seed has nothing to choose there.

## Decision

R0 is a hand-authored canonical world file. The generator turns that file into
source representations deterministically. Seeds apply only when the generator
creates worlds procedurally, such as held-out worlds or the scaled worlds for
SCN-016. Seed `2701006` moves from R0 to the first procedural world. The edit to
LIONG-006 lands in a later pull request.

## Alternatives considered

- Keep a seed on R0. The manifest would record a number that changes nothing in
  the output, and a reader could take it for a source of variation.

## Owner's words

Asked as Q2 of the synthetic-data interview on 2026-10-11:

> R0 is written out exactly in LIONG-006, so there is nothing for a seed to
> choose. Should seed 2701006 be removed from the R0 description and kept for the
> first procedural world?

The recommendation given with it:

> Yes. R0 stays deterministic and hand-authored. Seeds belong to procedural
> worlds only.

The owner answered:

> Q2. Aligned

## Evidence

- `docs/LIONG-006-synthetic-data.md:226` proposes the seed for the documented
  development world.
