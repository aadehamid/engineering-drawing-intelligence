# DEC-045: Each revision time comes from the system that records it

Status: Decided
Date: 2026-10-12

## Context

Asked as Q33 (Where revision times come from) in round 5 of the synthetic-data
interview, after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q33:

> Yes. Each time comes from the system that would really know it. LIONG-006's
> correction C1, which moves R1's effective start, then lives in an MOC-side
> record, not as a rewritten vendor revision.

## Alternatives considered

- The question named no alternative.

## Owner's words

Asked as Q33 in round 5 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> LIONG-006 keeps four times apart. Should they map like this?
> - source_recorded_at comes from each vendor's own field: the drawing revision
>   date in SmartPlant style, and the row timestamp in Plant 3D style.
> - effective_from and effective_to come from the MOC record, because neither
>   product stores when a change applies in engineering history.
> - ingested_at and published_at are written by our pipeline, never by the
>   generator.

The recommendation given with it:

> Yes. Each time comes from the system that would really know it. LIONG-006's
> correction C1, which moves R1's effective start, then lives in an MOC-side
> record, not as a rewritten vendor revision.

The owner answered:

> Agree on all

The answer covered every question in round 5, Q30 to Q34.

## Evidence

- LIONG-006, "Revision and time rules", which defines the four times and correction
  C1.
