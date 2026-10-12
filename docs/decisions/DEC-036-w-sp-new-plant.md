# DEC-036: W-SP is a new hand-authored plant about R0's size, built around what SmartPlant stores differently

Status: Decided
Date: 2026-10-12

## Context

Asked as Q24 (What W-SP is) in round 4 of the synthetic-data interview, after
DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q24:

> (b). A different layout also tests whether the mapping works beyond one plant.
> The exact contents go in the W-SP world file, which comes to you for review as a
> PR.

The option it chose reads:

> - (b) A new, hand-authored plant about R0's size, under its own facility context (for example `DEMO-LEKKI/UNIT-B`). It would cover what only SmartPlant stores differently:
>   - one pipeline made of several pipe runs that share a line number, so the pipeline must be derived;
>   - several inline components on one run, so the connectors split more than once;
>   - one cross-sheet pair;
>   - one instrument with a parent.
>
>   Its expected graph lives in its own world file, written by hand like R0's.

## Alternatives considered

- W-SP as a copy of R0's layout with new tags, which the question offered as option
  (a).

## Owner's words

Asked as Q24 in round 4 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> W-SP is the SmartPlant world (DEC-035). It could be:
> - (a) A copy of R0's layout with new tags. This is cheap, but it adds little,
>   because the cross-check fixture (DEC-034) already generates R0 in SmartPlant
>   form.
> - (b) A new, hand-authored plant about R0's size, under its own facility context
>   (for example DEMO-LEKKI/UNIT-B). It would cover what only SmartPlant stores
>   differently:
>   - one pipeline made of several pipe runs that share a line number, so the
>     pipeline must be derived;
>   - several inline components on one run, so the connectors split more than
>     once;
>   - one cross-sheet pair;
>   - one instrument with a parent.
>
>   Its expected graph lives in its own world file, written by hand like R0's.

The recommendation given with it:

> (b). A different layout also tests whether the mapping works beyond one plant.
> The exact contents go in the W-SP world file, which comes to you for review as a
> PR.

The owner answered:

> Agree on all

The answer covered every question in round 4, Q24 to Q29.

## Evidence

- The vendor research run in round 2 of the interview, on what SmartPlant stores
  differently.
