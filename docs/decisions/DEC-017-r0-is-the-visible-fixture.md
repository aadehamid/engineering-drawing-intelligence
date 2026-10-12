# DEC-017: LIONG-011 calls MILESTONE-001's input the visible R0 development fixture

Status: Decided
Date: 2026-10-11

## Context

`docs/LIONG-011-build-runbook.md:23` says MILESTONE-001 materializes the backend
from "a known private fixture". LIONG-006 says R0 is a public development oracle,
visible to every route and unusable for blind evaluation.

## Decision

LIONG-011 says "the visible R0 development fixture" in place of "a known private
fixture". MILESTONE-001 tests the structured path, not truth isolation. Private
truth starts with the held-out worlds. The edit to LIONG-011 lands in a later pull
request.

## Alternatives considered

- Make R0 private. This contradicts LIONG-006, which publishes R0 as the
  development oracle every document's expected results are written against.

## Owner's words

Asked as Q3 of the synthetic-data interview on 2026-10-11:

> Should LIONG-011:21 say "the visible R0 development fixture" instead of "a known
> private fixture"? The milestone tests the structured path, not truth isolation.

The recommendation given with it:

> Yes. MILESTONE-001 uses the public R0 oracle. Private truth starts with held-
> out worlds.

The owner answered:

> Q3. agreed

The question cited the paragraph's first line, 21. The phrase itself is on line 23.

## Evidence

- `docs/LIONG-011-build-runbook.md:23` and LIONG-006, "R0" as the public
  development oracle.
