# DEC-077: The p3d records map to DEXPI 2.0.1 as one file per drawing, with a LIONG sidecar for what DEXPI cannot carry

Status: Decided
Date: 2026-10-14

## Context

MILESTONE-001 step 3 writes the extracted records as DEXPI 2.0.1, validates them in
[DEC-064](DEC-064-four-stage-dexpi-validation.md)'s four stages, and parses them back
into the graph ([the build runbook](../LIONG-011-build-runbook.md)).
[DEC-063](DEC-063-own-dexpi-generator-and-parser.md) has LIONG write its own generator
and parser on lxml, but no record says which DEXPI class each source object becomes,
how relationships and sheets are expressed, or where the data DEXPI has no property
for goes. The agent decided the mapping during the night run of 2026-10-14, under the
owner's delegation in [DEC-073](DEC-073-second-night-delegation.md), after a design
checked against the pinned Core and Plant models and the reference P&ID. The owner
can reverse any of it.

## Decision

1. **Classes.** TK equipment is `Plant/ProcessEquipment.Tank`, with `TagName`,
   `TagNamePrefix`, `TagNameSequenceNumber` and `EquipmentDescription`. An XV valve
   is `Plant/Piping.OperatedValve`, with its tag in `PipingComponentNumber`. A PI
   instrument is `Plant/Instrumentation.ProcessInstrumentationFunction`, with
   category "P", functions "I" and the loop number. A pipe segment is
   `Plant/Piping.PipingNetworkSegment` holding one `Pipe`, with its tag in
   `SegmentNumber` and its nominal size as "DN" representation strings; segments
   are grouped into a `PipingNetworkSystem` per line. A junction is
   `Plant/Piping.PipeTee`. A sheet connector is a `FlowOutPipeOffPageConnector`
   or `FlowInPipeOffPageConnector`, with its label in `PipeConnectorNumber`. A tag
   type outside these tables is refused as unsupported.
2. **Relationships.** `starts_at` and `ends_at` are the segment's source and target
   items. `connects_to` is a segment without an identifier that holds one
   `DirectPipingConnection`. `continues_to` is a `ConnectorReference` on each
   connector, by drawing and number across drawings, by object on one drawing.
   `owned_by` is a `ProcessSignalGeneratingFunction` whose `SensingLocation` is an
   `InstrumentNozzle` of the owner. Equipment ends are `ProcessNozzle`s, and every
   connection end has its own `PipingNode`.
3. **Sheets.** Each drawing is one DEXPI file, because an `EngineeringModel` holds
   at most one diagram. Its `Diagram` holds one `RepresentationGroup` per object on
   the drawing, with no geometry; the frame values the model requires are fixed.
   A segment, direct connection or ownership that crosses drawings is refused.
4. **Identity.** Each object carries its ID in a `PersistentIdentifier` with context
   `p3d/PlantObject.ObjectId`, and each drawing's `PlantMetaData` one with context
   `p3d/Drawing.DrawingId`. File-local ids are the source table and key, such as
   `Equipment_101`; objects the source lacks get ids built from those, so ids stay
   the same across revisions.
5. **Sidecar.** `sidecar.json` holds the values DEXPI has no property for (units,
   the descriptions of valves, junctions and instruments, tag parts, drawing status)
   and every record's source locator, keyed by ID. It is a LIONG manifest and does
   not claim to be DEXPI. The parser takes the graph's facts from the DEXPI files
   and only evidence and those values from the sidecar.
6. **Refusals.** A relationship that names a missing object is refused with the
   edge it would have made, such as `FLOW p3d:object:114->p3d:object:104 has
   missing endpoint p3d:object:104` for Rbad. The generator writes no file then.
7. **Fifteen design choices.**
   1. One file per drawing, as item 3 says.
   2. The drawing number is the drawing's file name; the source has no other.
   3. A junction is a tee, because only a component can be a branch end; a junction
      with more than three ends is refused.
   4. An XV valve is an `OperatedValve` with its tag in `PipingComponentNumber`,
      because the source stores no actuator data that an `ActuatingSystem` could hold.
   5. TK is `Tank`.
   6. PI splits into category "P" and functions "I" through a fixed table.
   7. Ownership is a sensing location on an `InstrumentNozzle`, as in the
      reference P&ID's TT4750.03.
   8. A direct connection gets its own segment, so a pipe segment's target stays
      the item it ends at.
   9. Nominal size is written as representation strings, without a
      `NominalDiameterStandard` literal the source does not state.
   10. `ExportDateTime` is the source revision's recorded time, so output never
       depends on the clock.
   11. The diagram frame is the reference P&ID's: 420 by 297, white.
   12. The generator refuses a dangling relationship instead of writing a dangling
       reference; the references stage has its own hand-built negative.
   13. `EquipmentDescription` is marked English.
   14. The identifier contexts are `p3d/PlantObject.ObjectId` and
       `p3d/Drawing.DrawingId`.
   15. No `MeasuringLineFunction` is written; the graph does not need one.
8. **Validation.** `scripts/dexpi_validate.py` runs DEC-064's stages in order, then
   a round trip that must give identical bytes. Stage 4 checks the supported
   subset, the shapes the parser reads, unique tags, and a sidecar entry for every
   node, drawing, appearance and relationship. The XSD is read with only its own
   internal entities resolved, because its patterns are built from them; DEXPI
   files are read with no entity resolution and no network, and may not have a DTD.
   Each SCN-005 negative case in `fixtures/dexpi-negative/cases.json` is one fault
   planted in R0's generated output, and is named for the stage it must fail in.

## Alternatives considered

- One file for all drawings, with sheet membership in the sidecar. DEXPI 2.0.1 has
  no place for a second diagram, so the sheets would leave DEXPI entirely.
- Cross-file object references between drawings. They need the drawing files to
  import each other, and DEC-062 maps imports only to pinned model files.
- An `ActuatingSystem` for each XV valve, as the reference P&ID does for its control
  valves. The source has no actuator data to put in it.

## Owner's words

Given on 2026-10-14 and recorded in [DEC-073](DEC-073-second-night-delegation.md).

The owner answered:

> you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity

## Evidence

- `scripts/test_dexpi_generate.py`, `scripts/test_dexpi_validate.py` and
  `scripts/test_dexpi_parse.py`: R0, R1 and R2 pass all four stages and round-trip
  to identical bytes, parse to their answer-key graphs, Rbad is refused with the
  message above, each negative fixture fails in its named stage, and the reference
  P&ID parses with its supported classes extracted and the rest reported.
- Section 3 of [the delivery playbook](../delivery-playbook.md), marked Proven and given
  practice 6 on reading the XSD.
- REF-TECH-018 in [LIONG-007](../LIONG-007-stack-and-architecture.md), for lxml 6.1.3.
