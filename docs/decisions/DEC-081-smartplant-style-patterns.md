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
again on 2026-10-19 against Hexagon's own documentation, registered as REF-TECH-019 to
REF-TECH-027 in [the reference register](../LIONG-REF-001-reference-register.md).

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
   items carry no sheet key (REF-TECH-019, REF-TECH-020, REF-TECH-021).
2. **Runs drawn as split line depictions.** A pipe run is one design item. Its drawn
   pieces are line depictions with an end-1 and an end-2 item, and the run holds its
   flow direction against those ends. Each inline valve splits a piece in two, so W-SP's
   run A has three pieces and run B two (REF-TECH-019).
3. **Inline placement rows.** A valve's membership in its run is a row of its own, not
   a column on the valve, and each valve, instrument and nozzle has numbered port
   points (REF-TECH-019).
4. **An implied pipeline.** Each run carries the line-number parts. No row groups runs
   into a pipeline, and the generator writes none: extraction derives line 301 from
   the runs whose parts match (REF-TECH-022).
5. **Sheet links stored on both sides.** Each off-page connector of a pair stores its
   mate and its mate's sheet, with a to or from orientation. The pair is two rows that
   point to each other, and no row stores the flow between them (REF-TECH-019,
   REF-TECH-024).
6. **Tag parts with per-class uniqueness.** Tagged classes store their parts next to
   the composed tag. The composed tag is unique for vessels and instruments, unique
   within its vessel for a nozzle, and may repeat for pipe runs. Valve tags are one
   plain column (REF-TECH-023, REF-TECH-025).
7. **Nozzles.** Piping reaches a vessel through a nozzle, which stores its parent
   vessel. An instrument on a vessel reaches it through a nozzle and a process
   connection. The generator writes nozzle rows W-SP's world file does not list: one on
   each vessel for the pipe end, and one on TK-302 for LT-302. Extraction collapses
   them, so the graph's nodes and edges stay those of the world file (REF-TECH-027).

Each drawing has revision rows, with a major and minor number unique together; W-SP has
one, W0 (REF-TECH-026). Table and column names are LIONG's own. The schema copies no
vendor table, column, class or code-list name, no tag-format string, and no text from
unofficial copies of vendor training material.

## Alternatives considered

- Store LT-302's parent vessel as a key on the instrument, and connect pipes to the
  vessel symbol. Simpler, but the product does neither, and DEC-020 asks for the
  product's patterns. Collapsing nozzles is a mapping problem the real product poses.
- Have the generator write a pipeline row for line 301. The documentation says a
  pipeline row is found or created at publish, which is not saved drawing data; W-SP
  exists so that the pipeline must be derived (DEC-052).
- Relationship rows as the main store of connectivity. The documented connectivity is
  on connector ends and inline placement rows; the relationship table's item columns
  appear in no source found.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md).

The owner wrote:

> Please go ahead until closure. And also pick the next piece of logical batch of work and drive it to closure. Share with me the batch of work you will pick to execute with /night-run and make the /goal after the retor is done

## Evidence

- REF-TECH-019 to REF-TECH-027 in the reference register, each a Hexagon
  documentation page, read on 2026-10-19 through the documentation site's public
  search.
- `worlds/W-SP.yaml` and DEC-052, for the features each pattern must hold.
- Not used: an unlicensed practitioner SQL file and unofficial uploads of vendor
  training material. They pointed the search, and nothing is copied from them.
