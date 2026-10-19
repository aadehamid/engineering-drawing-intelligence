# DEC-086: W-SP's records map to DEXPI 2.0.1 through DEC-077's mapping, with sps identifier contexts, hand valves as OperatedValve and LT as category L

Status: Decided
Date: 2026-10-19

## Context

MILESTONE-001b takes W-SP through the same slice as MILESTONE-001
([DEC-042](DEC-042-w-sp-scn-001-first.md)), so the records `scripts/extract_sps.py`
writes ([DEC-085](DEC-085-sps-extraction-records.md)) must become DEXPI 2.0.1 files that
pass [DEC-064](DEC-064-four-stage-dexpi-validation.md)'s four stages, round-trip to
identical bytes, and parse back to W-SP's answer-key graph.
[DEC-077](DEC-077-dexpi-mapping.md) mapped only the Plant 3D-style records. W-SP adds
what R0 lacks: hand valves (HV), a level transmitter (LT), one line number drawn as two
runs on two drawings, GUID keys instead of whole-number object IDs, and attribute
predicates named as the SmartPlant-style rows name them (`tag_lead`, `link_sense`). The
agent decided the extension during the MILESTONE-001b night run, under the owner's
delegation in [DEC-080](DEC-080-milestone-001b-night-delegation.md). The owner can
reverse any of it.

## Decision

1. **One mapping, two backends.** `scripts/dexpi_generate.py` keeps DEC-077's mapping
   and holds what differs between the backends' records in a table, `BACKENDS`, chosen
   by the records' `source_id`. A source with no entry is refused. R0's output is
   byte-for-byte what it was before.
2. **Identity.** An item carries its GUID in a `PersistentIdentifier` with context
   `sps/DesignItem.ItemGuid`, a pipe segment with `sps/LineDepiction.DepictionGuid`,
   and a drawing's `PlantMetaData` with `sps/Sheet.SheetGuid`, following DEC-077's
   `table.column` form. The parser rebuilds `sps:item:<GUID>`, `sps:line:<GUID>` and
   `sps:sheet:<GUID>` from the context and value. File-local ids are the sps table
   and the GUID, with hyphens made underscores, such as `Vessel_4E781C49_...` and
   `LineDepiction_A80BEDD0_...`, as DEC-077 item 4 builds `Equipment_101`.
3. **Hand valves.** An HV valve is `Plant/Piping.OperatedValve` with its tag in
   `PipingComponentNumber` and no `ActuatingSystem`. The pinned Plant model has no
   class for a manually operated valve. It defines OperatedValve as a valve with "an
   external means of operation", naming a handwheel or lever as examples, and
   its subclasses, such as `BallValve` and `GateValve`, each name a valve body type.
   W-SP stores no body type. The sps fitting rows store no tag parts, so a valve's
   letters are the part of its tag before the first hyphen; letters outside the table
   are refused, as DEC-077 refuses an unknown XV-style tag type.
4. **Level transmitter.** LT is a `ProcessInstrumentationFunction` with category "L"
   and functions "T", added to PI's fixed table. Its number is the row's tag number,
   and its parent is a sensing location on an `InstrumentNozzle` of the vessel, as for
   PI in DEC-077.
5. **Line 301 across two drawings.** DEC-077 groups the segments on a drawing into one
   `PipingNetworkSystem` per line prefix and number. Run A's three segments therefore
   sit in `PipingNetworkSystem_L_301` in DEMO-PID-101's file, and run B's two in the
   system of the same id in DEMO-PID-102's file, each with `LineNumber` 301. DEXPI 2.0.1
   has no level between a system and its segments, so the runs and the derived
   `pipeline` value L-301 stay in the sidecar, with their evidence status.
6. **The backend's own words.** DEXPI properties carry the sps attributes under their
   sps names: `tag_lead` and `tag_number` as `TagNamePrefix` and
   `TagNameSequenceNumber`, and `link_sense` "To" and "From" as the Out and In
   connector classes. The parser reads a file's backend from its drawing identifier's
   context and gives the attributes back under that backend's names, so the round trip
   gives the same records. A file LIONG did not write gets the p3d names, as before.
7. **Unknown instrument letters.** In a file LIONG wrote, an instrument whose letter
   pair is outside the table fails the liong_rules stage instead of breaking the round
   trip. The negative case `liong_rules-instrument-letters` plants one in R0's output.

## Alternatives considered

- A specific valve class, such as `GateValve`, for HV. It would state a body type the
  source does not hold.
- An `ActuatingSystem` with a manual actuator for each HV valve. The source stores no
  actuator data, and DEC-077 declined one for XV on the same ground.
- One `PipingNetworkSystem` per run, or per derived pipeline. Per run splits line 301
  where DEXPI has no run level; per pipeline makes the grouping depend on a derived
  value that a run with a NULL line part does not get.
- A separate generator for the SmartPlant-style records. Two copies of one mapping
  would drift apart; the differences fit in one table.
- The p3d identifier context for sps objects. It would name a table the SmartPlant-style
  backend does not have.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- `scripts/test_dexpi_generate.py`: W-SP's W0 gives one file per drawing; each object
  has its class and its sps identifier; the hand valves carry their tags and no
  actuating system; LT-302 is category L, functions T, number 302; both runs of line
  301 sit in `PipingNetworkSystem_L_301`; segments run with the flow; the sheet links
  refer to each other by drawing and number. A valve or instrument outside the tables,
  an unknown link sense, an unmapped source and an object whose key is not its ID are
  refused.
- `scripts/test_dexpi_validate.py`: W0 passes all four stages and round-trips to
  identical bytes; each negative fixture, `liong_rules-instrument-letters` among them,
  fails in its named stage.
- `scripts/test_dexpi_parse.py`: W0 parses back to the records it was written from, and
  `scripts/compare_answer_key.py` scores its graph an exact match with W-SP's answer key.
- R0, R1 and R2 generate the same bytes as before the change; the R0 tests pass unchanged.
- `standards/dexpi/2.0.1/Plant.xml`, the pinned model, for `OperatedValve`'s definition
  and its subclasses.
