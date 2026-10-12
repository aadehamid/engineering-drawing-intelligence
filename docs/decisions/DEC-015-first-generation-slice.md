# DEC-015: The first generation work builds the R0 backend, its answer key, and one invalid variant

Status: Decided
Date: 2026-10-11

## Context

LIONG-006 specifies the canonical world R0 and its revisions. MILESTONE-001 in
LIONG-011 needs only the R0 engineering backend, its answer key, and one
invalid-reference variant, which is part of SCN-005. The other source
representations belong to later milestones in LIONG-011's stage table: the
registers behind SCN-008 in M2, drawings in M3, the operational fixture for SCN-011
in M4, and held-out worlds in M6. The interview question placed the registers in
M4; the stage table puts SCN-008 in M2.

## Decision

The first generation work builds three things: the R0 engineering backend, the R0
answer key with its manifest, and one variant in which a connection points at a
missing object. Each other source representation is built at the milestone that
uses it. [DEC-030](DEC-030-plant-3d-backend-first.md) sets which vendor-style
backend comes first.

## Alternatives considered

- Build every source representation before the first end-to-end test. This delays
  MILESTONE-001, and the later milestones may still change what those
  representations need.

## Owner's words

Asked as Q1 of the synthetic-data interview on 2026-10-11:

> MILESTONE-001 only needs the R0 engineering backend, its answer key, and one
> invalid-reference variant (part of SCN-005). The other representations come
> later: drawings in M3, registers and the operational fixture in M4, held-out
> worlds in M6. Should the first slice be limited to the R0 backend, the R0 answer
> key, and that one invalid variant?

The recommendation given with it:

> Yes. Build only what MILESTONE-001 needs, and add the other representations at
> the milestones that use them.

The owner answered:

> Q1. What excatly are we doing in R0. I do agree with your recommendation

The follow-up reply explained that R0 is the starting revision of the synthetic
plant, from TK-101 to TK-102 through valve XV-101 with a bypass through XV-102.

## Evidence

- LIONG-011, "MILESTONE-001" and its stage table (M1 to M7).
- LIONG-006, SCN-005.
