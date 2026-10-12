# DEC-032: Each backend carries a minimal data dictionary for the classes R0 uses

Status: Decided
Date: 2026-10-11

## Context

Both products describe their own schema in metadata tables. SmartPlant has a data
dictionary with item types and select lists, and Plant 3D has class definitions.

## Decision

The owner accepted the recommendation given with Q19:

> Yes, a minimal version. It's part of what makes these schemas awkward to read,
> and the DEXPI mapping should have to deal with it.

## Alternatives considered

- Leave the metadata out and hard-code classes in the mapping. The backends would
  be easier to read than the real products, and the mapping would skip work it
  must do on real data.

## Owner's words

Asked as Q19 of the synthetic-data interview on 2026-10-11:

> Both tools describe their own schema in metadata tables. SmartPlant has a data
> dictionary with item types and select lists, and Plant 3D has class definitions.
> Should each backend include a small version of that metadata, covering only the
> classes R0 uses?

The recommendation given with it:

> Yes, a minimal version. It's part of what makes these schemas awkward to read,
> and the DEXPI mapping should have to deal with it.

The owner answered:

> Q19: Agreed.

The question predates DEC-029. Which classes the backend of the second world covers
stays open until that world is specified.

## Evidence

- The vendor research run during the interview, on each product's metadata tables.
