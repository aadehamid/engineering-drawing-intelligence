# DEC-081: The SmartPlant-style schema borrows seven storage patterns from Smart P&ID, renamed, with nozzle rows and an implied pipeline

Status: Decided
Date: 2026-10-19

## Context

[DEC-020](DEC-020-vendor-style-backends.md) has each synthetic backend follow its
product's storage closely, under the project's own names.
[DEC-031](DEC-031-stored-data-not-behaviour.md) copies saved data, not editing
behaviour. [DEC-040](DEC-040-plant-3d-patterns.md) chose the Plant 3D-style patterns
and left the SmartPlant-style list for when MILESTONE-001b starts. The round-2 vendor
research from the synthetic-data interview could not be recovered, so the agent ran it
again on 2026-10-19, mainly against Hexagon's own documentation, registered as
REF-TECH-019 to REF-TECH-029 in [the reference register](../LIONG-REF-001-reference-register.md).
REF-TECH-029 is one administrator's queries, a secondary source.

The world the backend must hold is W-SP ([DEC-052](DEC-052-w-sp-contents.md)): one
line number in two pipe runs on two sheets, inline hand valves that split the runs, one
cross-sheet pair, and one instrument on a vessel. The agent decided this record during
the MILESTONE-001b night run, under the owner's delegation in
[DEC-080](DEC-080-milestone-001b-night-delegation.md). The owner can reverse any of it.

## Decision

The SmartPlant-style backend lives in its own schema, `sps`, in the same SQL Server
database ([DEC-028](DEC-028-one-database-two-schemas.md)), and borrows these patterns:

1. **Design items and depictions.** A base table of design items, one GUID key per row
   and a state for active or deleted, with one table per class sharing that key. A
   separate depiction table records each appearance on a sheet, with the sheet's key;
   items carry no sheet key. Hexagon's documentation states the item and representation
   split and the active or deleted state (REF-TECH-019); the shared key, the GUID form
   and the sheet key's place come from a secondary source only (REF-TECH-029).
2. **Runs drawn as split line depictions.** A pipe run is one design item. Its drawn
   pieces are line depictions with an end-1 and an end-2 item, and the run holds its
   flow direction against those ends. Each inline valve splits a piece in two, so W-SP's
   run A has three pieces and run B two (REF-TECH-019).
3. **Inline placement rows.** A valve's membership in its run is a row of its own, not
   a column on the valve, and each valve, instrument and nozzle has numbered port
   points (REF-TECH-019).
4. **An implied pipeline.** Each run carries the line-number parts. A line-group row
   holds only the line's key values, and no run stores a key to it. A run belongs to
   the group whose key values all match; a run with a missing key value belongs to
   none. The generator writes one line-group row for line 301, and extraction derives
   its runs by matching (REF-TECH-022).
5. **Sheet links stored on both sides.** Each off-page connector of a pair stores its
   mate and its mate's sheet, with a to or from orientation. The pair is two rows that
   point to each other, and no row stores the flow between them (REF-TECH-019,
   REF-TECH-020, REF-TECH-021, REF-TECH-024). The sources disagree on whether the
   mating property holds the mate's drawing ID; the backend stores the mate's sheet
   key, which W-SP's cross-sheet pair needs.
6. **Tag parts with per-class uniqueness.** Tagged classes store their parts next to
   the composed tag. The composed tag is unique for vessels and instruments, unique
   within its vessel for a nozzle, and may repeat for pipe runs. Valve tags are one
   plain column (REF-TECH-019, REF-TECH-022, REF-TECH-025, REF-TECH-027, REF-TECH-028).
7. **Nozzles.** Piping reaches a vessel through a nozzle, which stores its parent
   vessel. An instrument on a vessel reaches it through a nozzle and a process
   connection (REF-TECH-021, REF-TECH-027). The generator writes nozzle rows W-SP's world file does not list: one on
   each vessel for the pipe end, and one on TK-302 for LT-302. Extraction collapses
   them, so the graph's nodes and edges stay those of the world file (REF-TECH-027).

Each drawing has revision rows, with a major and minor number unique together; W-SP has
one, W0 (REF-TECH-019, REF-TECH-026). Table and column names are LIONG's own. The schema copies no
vendor table, column, class or code-list name, no tag-format string, and no text from
unofficial copies of vendor training material.

## Alternatives considered

- Store LT-302's parent vessel as a key on the instrument, and connect pipes to the
  vessel symbol. Simpler, but the product does neither, and DEC-020 asks for the
  product's patterns. Collapsing nozzles is a mapping problem the real product poses.
- Leave the line-group row out, so line 301 exists only as matching run values. The
  Pipelines topic says the application adds a pipeline entry without the user
  creating one, so the product stores the row. Its membership stays implicit, so
  extraction still has to derive the pipeline, as W-SP requires (DEC-052).
- Relationship rows as the main store of connectivity. The documented connectivity is
  on connector ends and inline placement rows; the relationship table's item columns
  appear in no source found.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- REF-TECH-019 to REF-TECH-028 in the reference register, Hexagon documentation pages
  read on 2026-10-19 through the documentation site's public search.
- REF-TECH-029, a secondary source with no licence. Its findings back three clauses of
  pattern 1, as that pattern says; none of its text is copied.
- `worlds/W-SP.yaml` and DEC-052, for the features each pattern must hold.
- Not used: unofficial uploads of vendor training material. They pointed the search,
  and nothing is copied from them.
