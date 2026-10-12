# DEC-018: A canonical world is a declarative data file checked against a JSON Schema

Status: Decided
Date: 2026-10-11

## Context

The generator needs the canonical world in a form that a pull request can review,
the manifest can hash, and the scorer can read without running generator code.

## Decision

Each canonical world is a declarative data file, such as YAML, checked against a
JSON Schema in `schemas/`. The file lists aliases, typed objects, attributes, edges,
and revisions as changes from a named base. Code does the work around the file: the
schema rejects a malformed world, a Python generator turns the world into source
representations, and tests check the generator's own output.

## Alternatives considered

- Python code that builds the world. The truth could then be read only by running
  the generator.
- Rows in a database. Harder to review in a pull request and to hash for the
  manifest.

## Owner's words

Asked as Q4 of the synthetic-data interview on 2026-10-11, with three options: a
declarative data file checked against a JSON Schema, Python code that builds the
world, or rows in a database. The recommendation was the data file.

The owner answered:

> Q4. Agreed. What are then going to do with this file. Should we use code here?

The follow-up reply described the three code pieces in the Decision section.

## Evidence

- LIONG-006 requires a generation manifest with a SHA-256 of every emitted file.
