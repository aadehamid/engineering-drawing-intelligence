# DEC-050: The Plant 3D-style generator writes one JSON file per table per revision, with a separate answer key

Status: Decided
Date: 2026-10-13

## Context

[DEC-019](DEC-019-generator-writes-files.md) has the generator write backend files
that a separate loader applies, and [DEC-037](DEC-037-revision-snapshots.md) makes
each revision one complete snapshot. The generator for the Plant 3D-style backend
needed choices the earlier records left open: the file format, where the files and
the answer key go, how keys are assigned, how R0's edges map to the schema's tables,
and when Rbad was recorded. The agent decided them during the night run, under
[DEC-048](DEC-048-night-delegation.md).

## Decision

The agent decided under the owner's delegation:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make

The choices:

1. **Format.** Each revision of a world is one folder holding one JSON file per
   `p3d` data table, each a list of rows. The class definitions are part of the
   schema file, not of a snapshot. JSON keeps column names and nulls, and a loader
   inserts it without parsing rules of its own.
2. **Location.** R0's snapshots go in `fixtures/p3d-r0/`, with a `manifest.json`.
   The answer key goes in `fixtures/answer-keys/p3d-r0.json`, outside the snapshot
   folder, and no snapshot file holds an alias. R0 is the public development oracle
   ([DEC-017](DEC-017-r0-is-the-visible-fixture.md)), so its answer key can be in the
   repository; a held-out world's never is.
3. **Committed and checked.** The files are committed, and `scripts/check.sh` fails
   when they differ from a fresh generation, as it does for the review archive.
4. **Keys.** Plant objects are numbered from 101 and drawings from 901, in the
   world file's order. Every alias keeps its key in every snapshot, deleted ones
   included ([DEC-044](DEC-044-stable-separate-keys.md)). GUIDs are UUIDv5 values
   from a fixed namespace, so they are reproducible.
5. **Edges to tables.** A flow into a pipe segment is a `SegmentStart` row, and a
   flow out of one is a `SegmentEnd` row. A flow between two sheet connectors is one
   `SheetConnectorLink` row, which is also the cross-sheet reference; the generator
   refuses a world where those two differ. Any other direct flow, R0's VB to J2, is
   a `ConnectorPair` row. An instrument's parent is an `Ownership` row, and each
   ON_SHEET edge is a `DrawingAppearance` row.
6. **History.** Each change along a revision's ancestry is one work-history row: a
   created object, a tag change, a deleted object, or a removed connection, whose
   detail names the two keys. A change the backend cannot record stops generation.
7. **Rbad's time.** LIONG-006 gives Rbad no time. It is recorded at 12:00 on R0's
   day, 2030-01-01, after R0 and before R1.
8. **Manifest.** In place of the generator commit, which a committed file cannot
   contain, the manifest records the SHA-256 of the world file, the schema, the
   generator and `uv.lock`, then the SHA-256 of every snapshot file.

## Alternatives considered

- CSV per table. It loses the difference between an empty string and a null.
- Generate into an ignored folder at check time. Reviewers could not then read the
  rows a change produces in its pull request.

## Owner's words

Given in the session that set the night run, on 2026-10-13, and recorded in
[DEC-048](DEC-048-night-delegation.md).

The owner said:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make.
> Add decisions you made to the log. I dont want ahytning waiting on me while I am
> not here and blocking you

## Evidence

- `docs/LIONG-006-synthetic-data.md`, "Exact baseline R0", "Revision and time rules"
  and "Reproducibility and separation".
- `scripts/test_generate_p3d.py` projects each snapshot back into the comparison
  view and matches LIONG-006's published counts for R0 and R2; Rbad keeps the two
  flows that name the deleted valve. It also pins every key, the values of every R0
  object and drawing row, the connection rows of R0, R2 and Rbad, the history of R0
  and R2, and R1's revision columns. Generated identifiers (GUIDs, row IDs, drawing
  handles and row stamps) are checked only for freshness and determinism.
