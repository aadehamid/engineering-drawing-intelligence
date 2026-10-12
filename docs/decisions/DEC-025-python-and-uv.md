# DEC-025: The generator uses Python 3.12 with dependencies locked by uv

Status: Decided
Date: 2026-10-11

## Context

LIONG-007 proposes a small Python application. The generation manifest records
runtime and dependency lock hashes, so the project needs one runtime and one lock
tool.

## Decision

The owner accepted the recommendation given with Q13:

> Yes.

## Alternatives considered

- Pip with a hand-kept requirements file. It pins only the packages it lists,
  so the lock hash would not cover every transitive dependency.

## Owner's words

Asked as Q13 of the synthetic-data interview on 2026-10-11:

> LIONG-007 proposes "a small Python application". Should the generator use Python
> 3.12 with dependencies locked by uv?

The recommendation given with it:

> Yes.

The owner answered:

> Q13: yes

## Evidence

- LIONG-006, the generation manifest paragraph at line 226.
- CI already runs Python 3.12 (`.github/workflows/check.yml`).
