# DEC-021: The glossary defines canonical world, source representation, and world lineage

Status: Decided
Date: 2026-10-11

## Context

The synthetic-data documents used "canonical world", "source representation", and
"world lineage" without a definition in `GLOSSARY.md`.

## Decision

The owner accepted the recommendation given with Q7:

> Yes, add all three as written.

## Alternatives considered

- Leave the terms undefined and rely on each document's usage. Readers would meet
  three central terms with no single meaning.

## Owner's words

Asked as Q7 of the synthetic-data interview on 2026-10-11:

> The docs use "canonical world", "world lineage" and "source representation"
> without defining them in GLOSSARY.md. Should I add them with these meanings?
>
> Canonical world: the complete engineering truth for one synthetic facility,
> including its revisions and intended errors.
>
> Source representation: one emitted view of a canonical world, such as the
> backend, a drawing set, or a register, with its own keys.
>
> World lineage: a canonical world together with every source representation,
> revision, render and crop derived from it. Data is split into training and
> evaluation partitions by lineage, never by page or file.

The recommendation given with it:

> Yes, add all three as written.

The owner answered:

> Q7. Please add them

The review of #12 changed the world lineage definition twice before it merged: to
match LIONG-006, and to leave the canonical world's truth outside the lineage. The
owner has not confirmed those changes in words. GLOSSARY.md holds the merged
wording.

## Evidence

- Merged in #12 (`fdca6f2`).
