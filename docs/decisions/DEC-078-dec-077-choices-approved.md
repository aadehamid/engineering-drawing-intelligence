# DEC-078: The owner approves DEC-077's three least-settled mapping choices

Status: Decided
Date: 2026-10-18

## Context

The agent made [DEC-077](DEC-077-dexpi-mapping.md)'s DEXPI mapping during the night
run of 2026-10-14, under the owner's delegation in
[DEC-073](DEC-073-second-night-delegation.md). That run's summary asked the owner to
review the three choices the backend's data settled least. In each, DEXPI 2.0.1 can
hold data that the Plant 3D-style backend does not store:

1. An XV valve is an `OperatedValve` with its tag in `PipingComponentNumber`, with no
   `ActuatingSystem`, because the backend stores no actuator data (DEC-077, choice 4).
2. A drawing's number is its file name, because the backend has no other drawing
   number (DEC-077, choice 2).
3. Each diagram is written without geometry, because the backend has no coordinates
   (DEC-077, item 3). A DEXPI viewer shows an empty sheet; the graph does not change.

## Decision

The owner approves all three choices as DEC-077 states them. The rest of DEC-077
stays a decision made under DEC-073's delegation.

## Alternatives considered

- Add an `ActuatingSystem` to each XV valve. The backend has no actuator data to put
  in it.
- Leave out the drawing number, which Core's `DrawingNumber` allows. The file name is
  the only name the source gives a drawing, so writing it keeps that name in the file.
- Invent geometry for each diagram. No source states it, so the files would carry
  positions nobody recorded.

## Owner's words

Asked on 2026-10-18, after the agent explained the three choices again: accept all
three, with the agent's recommendation to accept them because each is the only option
the backend's current data supports.

The owner answered:

> yes to all three

## Evidence

- DEC-077, items 3 and 7 and its Alternatives considered.
- `scripts/test_dexpi_generate.py`, `scripts/test_dexpi_validate.py` and
  `scripts/test_dexpi_parse.py`, which pass with these choices.
