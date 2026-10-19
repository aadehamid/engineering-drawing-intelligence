# DEC-083: The SmartPlant-style generator writes W-SP's W0 as one JSON file per table, keyed by name-based GUIDs, with nozzle rows and one run drawn against its flow

Status: Decided
Date: 2026-10-19

## Context

[DEC-050](DEC-050-p3d-generator-choices.md) set how the Plant 3D-style generator writes
its files. The SmartPlant-style generator, `scripts/generate_sps.py`, writes W-SP's
backend in the shape [DEC-081](DEC-081-smartplant-style-patterns.md) sets. That shape
differs from the world file: pipe segments become line depictions of runs, and nozzle
rows appear that the world file does not list. Choices that DEC-050 and DEC-081 leave
open were still to make. The agent made them during the MILESTONE-001b night run, under
the owner's delegation in [DEC-080](DEC-080-milestone-001b-night-delegation.md). The
owner can reverse any of them.

## Decision

1. **Format and location, as for Plant 3D.** W0 is one folder,
   `fixtures/sps-wsp/W0/`, with one JSON file per `sps` data table and a
   `manifest.json` beside it. The answer key is
   `fixtures/answer-keys/sps-wsp.json`, outside the snapshot folder, in the same
   shape as `p3d-r0.json`. `scripts/check.sh` fails when the committed files differ
   from a fresh generation.
2. **Keys.** Every GUID is a UUIDv5 value from a fixed namespace and the world's
   name, the row's role and the alias it comes from, such as `item/E1` or `line/P1`.
   The same world always gives the same GUIDs. The answer key maps each item alias to
   its item GUID, each pipe segment to its line depiction's GUID, and each drawing to
   its sheet's GUID.
3. **Runs.** The segments that share a `run` attribute form one pipe run. The run's
   tag parts come from the segments' tags and line number, which must agree, and so
   must their sizes. Each segment becomes one line depiction whose ends are the marks
   of the items the world's flow edges join it to. Each line carries a label
   depiction with the segment's tag. Each distinct line key gets one line group row
   holding the line prefix and number, `L` and `301` for W-SP, and no run points to
   it.
4. **One run drawn against its flow.** Run A is drawn from its upstream end and run
   B from its downstream end, so their flow senses differ. Extraction then has to read
   the flow sense to get the direction right.
5. **Nozzles and the process connection.** Each pipe end at a vessel gets its own
   nozzle on that vessel. An instrument with a parent vessel gets one more nozzle on
   the vessel and a process connection drawn from the instrument's mark to that
   nozzle's mark. Nozzle tags count up per vessel: N1 and N2 on TK-302.
6. **Fittings and sheet links.** A fitting's inline placement names the run whose
   segments it joins, and the generator refuses a fitting between two runs. Each
   sheet link stores its mate and its mate's sheet. The world's flow between the two
   connectors is not stored, and the generator refuses a cross-sheet pair without
   that flow.
7. **Revision rows.** Each sheet has one revision row for W0: major `W0`, minor `0`,
   state `Approved`.
8. **W0's time.** LIONG-006 gives W-SP no time. W0 is recorded at 08:00 on
   2030-02-01, after R0's revisions.
9. **The Plant 3D generator's check.** `generate_p3d.py --check` now counts only
   its own answer key in `fixtures/answer-keys/`, so the folder can hold W-SP's key
   too. A test in `scripts/test_generate_sps.py` owns the folder: it fails when the
   folder holds any file besides the two generators' keys.

## Alternatives considered

- Draw both runs with their flow. The fixture would then not test whether extraction
  reads the flow sense.
- One nozzle per vessel shared by all its connections. Fewer rows, but the shared
  nozzle would hide which connection reaches the vessel, and DEC-081 pattern 7 names
  one nozzle for the pipe end and one for LT-302.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- `scripts/test_generate_sps.py`. Its expected rows are written by hand from
  `worlds/W-SP.yaml` and this record. It follows each GUID through the rows to a tag,
  label or sheet number and compares those with the hand-written values: every item
  and its kind, the tagged rows, both runs, each line depiction's ends, marks and
  labels, inline placements, port points, the sheet links, the revision rows, and the
  answer key's view of W0. It also checks that one line group holds line 301's key and
  no other row names it, that no snapshot row names an alias, and that the generator
  refuses three broken worlds.
