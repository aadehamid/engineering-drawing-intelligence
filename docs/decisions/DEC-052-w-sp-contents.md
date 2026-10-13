# DEC-052: W-SP is a two-sheet transfer line whose one pipeline is two runs, with three inline valves

Status: Decided
Date: 2026-10-13

## Context

[DEC-036](DEC-036-w-sp-new-plant.md) makes W-SP a new hand-authored plant about
R0's size, under its own facility context, covering what only SmartPlant stores
differently. It left the exact contents to the W-SP world file, to come to the
owner as a pull request. [DEC-042](DEC-042-w-sp-scn-001-first.md) limits W-SP to
the SCN-001 equivalent. The agent chose the contents during the night run, under
[DEC-048](DEC-048-night-delegation.md).

## Decision

The agent decided under the owner's delegation:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make

`worlds/W-SP.yaml` holds the contents:

- **Facility.** `DEMO-LEKKI/UNIT-B`, on drawings DEMO-PID-101 and DEMO-PID-102.
- **One derived pipeline.** Five pipe segments carry line number 301 in two runs:
  run A on the first sheet and run B on the second. Only the shared line number
  makes them one pipeline.
- **Inline components that split a run more than once.** Run A carries HV-301 and
  HV-302, and run B carries HV-303.
- **One cross-sheet pair.** TO-S2/B on the first sheet and FROM-S1/B on the second.
- **One instrument with a parent.** LT-302, level transmission, on vessel TK-302.
- **Size and scope.** 15 nodes and 26 edges in one baseline revision, W0. Flow runs
  as one path from TK-301 to TK-302.

Line number and run are node attributes, so the world schema needs no change.

## Alternatives considered

- Give run B a different line number. The pipeline would then not need deriving,
  which is the point of DEC-036's first feature.
- Add a branch like R0's bypass. R0 already tests branches, and DEC-036 lists none
  for W-SP.

## Owner's words

Given in the session that set the night run, on 2026-10-13, and recorded in
[DEC-048](DEC-048-night-delegation.md).

The owner said:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make.
> Add decisions you made to the log. I dont want ahytning waiting on me while I am
> not here and blocking you

## Evidence

- `scripts/test_world.py`, class `WspHasWhatSmartPlantStoresDifferently`, checks
  each feature above.
