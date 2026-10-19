# DEC-082: The SmartPlant-style schema is one T-SQL file for schema sps, with GUID keys on its data tables, label depictions and a per-sheet revision rule

Status: Decided
Date: 2026-10-19

## Context

[DEC-081](DEC-081-smartplant-style-patterns.md) set the seven patterns the
SmartPlant-style schema borrows. Writing the schema left choices that DEC-081 does not
make: how the file is built and tested, the class tables and their columns, where W-SP's
segment tags live, what a line's ends name, the revision's approval columns, the scope of
the revision-number rule, the pipeline row's columns, and the data dictionary that
[DEC-032](DEC-032-minimal-data-dictionary.md) asks each backend to carry. DEC-032 was
asked for R0's classes and left the second world's classes open. The agent
made them during the MILESTONE-001b night run, under the owner's delegation in
[DEC-080](DEC-080-milestone-001b-night-delegation.md). The owner can reverse any of
them.

## Decision

1. **Build method, as for Plant 3D.** The schema is one hand-written T-SQL file,
   `schemas/smartplant-style.sql`, that creates schema `sps` in the same database as
   `p3d` ([DEC-028](DEC-028-one-database-two-schemas.md)).
   `scripts/test_smartplant_schema.py` reads the file on every run and, when
   `LIONG_SQLSERVER` names a server, applies it to a fresh database, as
   [DEC-049](DEC-049-plant-3d-schema-choices.md) does for `p3d`. `scripts/check.sh`
   runs it, so CI applies the schema to SQL Server 2022.
2. **Class tables.** `DesignItem` is the base table: a GUID key, the item's kind and
   its state. Seven class tables share that key: `Vessel`, `Instrument`, `PipeRun`,
   `PipingFitting`, `Nozzle`, `ProcessConnection` and `SheetLink`. The process
   connection that DEC-081 pattern 7 names is a design item drawn as a line, like a
   pipe run.
3. **Data rows are keyed by GUIDs.** Each data table's key is a `UNIQUEIDENTIFIER`,
   with no integer key beside it. DEC-081 pattern 1 takes the GUID form from a
   secondary source only. The three dictionary tables are keyed by name instead
   (choice 10).
4. **Tag parts.** Vessels, instruments and pipe runs store `TagLead`, `TagNumber` and
   `TagTail` next to the composed `ItemTag`. For a pipe run these are the line-number
   parts that DEC-081 pattern 4 matches on. A fitting's tag is one column. As
   DEC-081 pattern 6 says, a nozzle's tag is unique within its vessel: a unique index
   on the nozzle's parent vessel and its tag.
5. **Segment tags are labels.** W-SP gives each pipe segment a tag, such as L-301-1,
   but a pipe segment is a line depiction, not an item. The schema adds
   `LabelDepiction`: a depiction that belongs to no item and holds text placed on
   another depiction. REF-TECH-019 describes the label representation this way.
6. **Line ends name items.** A line depiction stores the design item attached at its
   end 1 and at its end 2, `End1Item` and `End2Item`, as DEC-081 pattern 2 says. A
   pipe end at a vessel names the nozzle, and a free end is NULL.
7. **The approval is an approver and a date.** Each revision row stores `Approver` and
   `ApprovedOn`, the approved-by and approval-date fields that
   [DEC-039](DEC-039-approval-in-vendor-fields.md) names for the SmartPlant-style
   backend. Both are NULL on a revision not yet approved. `RevisedOn` stays the time
   the source recorded the revision ([DEC-045](DEC-045-revision-time-sources.md)).
8. **Revision numbers are unique on their sheet.** The major and minor numbers are
   unique together for one sheet, not across the plant. REF-TECH-026 says "unique in
   the plant", but a plant-wide rule would stop W-SP's two sheets from both holding
   revision W0.
9. **The line group.** `LineGroup` is the pipeline's row. It holds only the line key
   values W-SP uses, the line prefix and number, and no run stores a key to it.
   REF-TECH-022 says the application adds a pipeline entry as runs are drawn and that
   the relationship between pipeline and run is implicit. Which runs belong is found
   by matching their line parts to the group's values. The product gives the
   pipeline a table of its own (REF-TECH-022), but no source found shows that row
   sharing the design items' key or their columns. Keeping the line group outside
   `DesignItem` is the agent's choice: nothing in the item tables can then point to
   it, and it adds no item that extraction could mistake for a graph node.
10. **Data dictionary.** This settles the point DEC-032 left open for the second
    world: the dictionary covers W-SP's classes. `ItemType`, `ItemProperty` and
    `SelectEntry` describe the item types W-SP uses, their columns and tag parts,
    and the select lists for item state, flow sense, link sense and depiction kind.
    The coded columns hold the select-list values as text. These tables are keyed
    by name: `ItemType` by item kind, `ItemProperty` by item kind and property, and
    `SelectEntry` by list and value.

## Alternatives considered

- Put each segment's tag on the line depiction as a column. Shorter, but the product
  keeps label text on separate label representations.
- Leave segment tags out. The extracted graph could then not carry the tags W-SP's
  world file gives the segments.
- No pipeline row at all, so that the pipeline is wholly implied. The pages behind
  REF-TECH-022 say a pipeline entry is added as runs are drawn.
- Make revision numbers unique across the plant, as REF-TECH-026's wording reads. W-SP
  would then need a different revision number on each sheet, and W-SP has one revision.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- REF-TECH-019, REF-TECH-022 and REF-TECH-026 in
  [the reference register](../LIONG-REF-001-reference-register.md).
- `scripts/test_smartplant_schema.py` passed against SQL Server 2022 under OrbStack on
  2026-10-19. It applies the schema to a fresh database and checks the uniqueness rules
  there. A second vessel or instrument with the same tag is refused. Two pipe runs or
  two fittings with the same tag are accepted. A repeated revision number is
  refused on its sheet and accepted on another sheet. A repeated nozzle tag is refused
  on its vessel and accepted on another vessel.
