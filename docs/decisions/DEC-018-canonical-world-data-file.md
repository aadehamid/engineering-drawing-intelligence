# DEC-018: A canonical world is a declarative data file checked against a JSON Schema

Status: Decided
Date: 2026-10-11

## Context

The generator needs the canonical world in a form that a pull request can review,
the manifest can hash, and the scorer can read without running generator code.

## Decision

The owner accepted the recommendation given with Q4:

> (a). A data file is easy to review in a PR and easy to hash for the manifest. It
> also lets the scorer read the truth without running generator code.

The option it chose reads:

> (a) A declarative data file, such as YAML, checked against a JSON Schema in
> schemas/. It would list aliases, typed objects, attributes, edges, and revisions
> as changes from a named base.

## Alternatives considered

- Python code that builds the world. The truth could then be read only by running
  the generator.
- Rows in a database. Harder to review in a pull request and to hash for the
  manifest.

## Owner's words

Asked as Q4 of the synthetic-data interview on 2026-10-11:

> How should the canonical world be written down?
>
> (a) A declarative data file, such as YAML, checked against a JSON Schema in
> schemas/. It would list aliases, typed objects, attributes, edges, and revisions
> as changes from a named base.
>
> (b) Python code that builds the world.
>
> (c) Rows in a database.

The recommendation given with it:

> (a). A data file is easy to review in a PR and easy to hash for the manifest. It
> also lets the scorer read the truth without running generator code.

The owner answered:

> Q4. Agreed. What are then going to do with this file. Should we use code here?

The follow-up reply answered the owner's question by proposing three pieces of code
around the file: the JSON Schema that rejects a malformed world, a Python generator
that turns the world into source representations, and tests of the generator's own
output. The owner has not confirmed that proposal in words, so this record does not
decide it.

## Evidence

- LIONG-006 requires a generation manifest with a SHA-256 of every emitted file.
