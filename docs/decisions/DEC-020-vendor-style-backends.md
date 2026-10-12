# DEC-020: Two synthetic backends follow SmartPlant P&ID and AutoCAD Plant 3D storage closely, with original names

Status: Decided
Date: 2026-10-11

## Context

Q6 offered two backend schemas: a minimal schema shaped for the project, or one
that imitates a real authoring product's tables. The owner chose a third option:
base the schema on how SmartPlant P&ID and AutoCAD Plant 3D store objects. A
research agent then read public sources on both products. Q9 asked how closely to
follow them, because vendor schemas are proprietary and `ARCHITECTURE.md` said the
backend was "not a replica of an undisclosed engineering platform".

The research reported patterns such as these. They are findings, not part of this
decision. [DEC-040](DEC-040-plant-3d-patterns.md) selects the six patterns the
Plant 3D-style schema borrows. The SmartPlant-style list waits for MILESTONE-001b.

- **SmartPlant P&ID:** model items kept apart from their drawing representations,
  connectors split at inline components, pipelines derived from matching
  properties, tags stored as parts, and a data dictionary.
- **AutoCAD Plant 3D:** class tables, link tables between objects and drawings,
  line rows that name their start and end assets, and tag formats built from
  subparts.

## Decision

The project has two backend schemas: one modelled on how SmartPlant stores its
objects in the backend, and one on how Autodesk does (Q6). Each borrows its
application's patterns very closely and uses the project's own names. Some
synthetic data is generated using the SmartPlant schema and others using the
Autodesk schema (Q9).

## Alternatives considered

- A minimal schema shaped for the project. Easier to map, but it teaches nothing
  about either product's real data.
- Copying vendor table and column names. Vendor schemas are proprietary.

## Owner's words

Asked as Q6 of the synthetic-data interview on 2026-10-11, with options (a), a
minimal project schema, and (b), a schema that imitates a real product's tables.

The owner answered:

> Q6. I will like Option C. Especially if we can reverse engineer how SmartPlant
> and/or autodesk stores this objects in the backend. That is their schema. Let us
> do a search to find out

Asked as Q9 on 2026-10-11:

> Should we design an original, documented schema that borrows the commercial
> tools' structural patterns without copying their table or column names?

The recommendation given with it:

> Yes. Borrow the patterns, write our own names, and cite the public source for
> each pattern we borrow.

The owner wrote:

> Q9:Borrow the pattersn very closesly and write our names. I do want us to have
> this tow patterns, we generate some of the synthetic data using SMartPlant schema
> and others using autodesk schema. I want this project to match those two
> applications very closely . as close to their reality as possible

## Evidence

- `ARCHITECTURE.md:17`, the sentence that [DEC-033](DEC-033-architecture-wording.md)
  replaces.
- The public-source research on both products' backends, run during the interview.
  Each pattern's citation goes into the schema documentation when the schema is
  written.
