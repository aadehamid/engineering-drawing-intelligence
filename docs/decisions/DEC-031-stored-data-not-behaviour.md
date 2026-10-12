# DEC-031: The backends copy each application's saved data, not its editing behaviour

Status: Decided
Date: 2026-10-11

## Context

The backends could match the real applications at two depths: the data each one
saves, or also the behaviour that produces it.

## Decision

Each backend matches how its application stores saved data: tables, keys,
relationship rows, tag parts, revision fields, connector splits, and derived
pipelines. The generator writes the end state the application would have saved.
It does not simulate check-out and check-in, tag reservation, or tag recomputation.

## Alternatives considered

- Also simulate application behaviour, such as check-out and check-in, Plant 3D
  reserving a tag before the drawing is saved, and SmartPlant recomputing tags from
  their parts. The pipeline reads only saved data, and simulating editing would
  mean building an authoring tool, which DEC-012 excludes.

## Owner's words

Asked as Q18 of the synthetic-data interview on 2026-10-11, with option (a), match
how each application stores its saved data, and option (b), also simulate
application behaviour.

The recommendation given with it:

> (a). Our pipeline only reads saved data. Simulating the applications' editing
> behaviour would be building an authoring tool, and that is out of scope
> (DEC-012).

The owner answered:

> Q18: Agreed

## Evidence

- DEC-012 in [the decision register](../LIONG-REG-001-decisions.md) excludes
  authoring.
