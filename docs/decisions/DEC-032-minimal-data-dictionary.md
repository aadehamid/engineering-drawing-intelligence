# DEC-032: Each backend carries a minimal data dictionary for the classes its world uses

Status: Decided
Date: 2026-10-11

## Context

Both products describe their own schema in metadata tables. SmartPlant has a data
dictionary with item types and select lists, and Plant 3D has class definitions.

## Decision

Each backend includes a small version of its product's metadata layer, covering
only the classes its world uses. The DEXPI mapping has to read that layer.

## Alternatives considered

- Leave the metadata out and hard-code classes in the mapping. The backends would
  be easier to read than the real products, and the mapping would skip work it
  must do on real data.

## Owner's words

Asked as Q19 of the synthetic-data interview on 2026-10-11:

> Should each backend include a small version of that metadata, covering only the
> classes R0 uses?

The owner answered:

> Q19: Agreed.

The question predates [DEC-029](DEC-029-two-canonical-worlds.md). With two worlds,
the SmartPlant-style backend covers the classes W-SP uses.

## Evidence

- The vendor research run during the interview, on each product's metadata tables.
