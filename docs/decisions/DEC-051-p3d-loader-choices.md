# DEC-051: The loader replaces the backend's rows with a snapshot and raises one outbox event per revision

Status: Decided
Date: 2026-10-13

## Context

[DEC-019](DEC-019-generator-writes-files.md) has a separate loader apply the
generator's files, and [DEC-047](DEC-047-loader-outbox-schema.md) has it write each
revision and its pending event in one transaction, in a third, non-vendor schema.
How the loader applies a snapshot, what the outbox row holds, and what the loader
refuses were still open. The agent decided them during the night run, under
[DEC-048](DEC-048-night-delegation.md).

## Decision

The agent decided under the owner's delegation:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make

The choices:

1. **Replace, not merge.** A load deletes every row of the `p3d` data tables and
   inserts the snapshot's rows, because each snapshot is complete
   ([DEC-037](DEC-037-revision-snapshots.md)). The class definitions are part of the
   schema and stay.
2. **One transaction.** The rows and the event commit together. An interruption
   before the commit leaves the previous revision and no new event, as LIONG-006's
   first recovery row requires.
3. **The outbox row.** Schema `outbox`, table `PendingEvent`: an event ID, a load
   sequence, the backend, world and revision, a SHA-256 digest of the snapshot's
   files, the source's recorded time, the commit time, and a status that starts as
   Pending. Delivery attempts and outcomes belong to the pipeline's own records.
4. **One event per revision.** A unique key on backend, world and revision stops a
   reload from raising a second event. Reloading the same files changes nothing;
   reloading different files for a loaded revision is refused.
5. **Checks before any write.** Every file must match the manifest's SHA-256, and
   every row's columns must be exactly its table's, as the schema file creates them;
   the loader never takes a column name from a file. A snapshot loads only on top of
   its base revision, so a backend holds one line of revisions, as a saved project
   database does.

## Alternatives considered

- Apply only the differences between snapshots. The product saves its current
  state, and a full replace keeps the loader simple and the snapshot authoritative.

## Owner's words

Given in the session that set the night run, on 2026-10-13, and recorded in
[DEC-048](DEC-048-night-delegation.md).

The owner said:

> you shpuld decide for me unless it is aboslutely not clear what decisions to make.
> Add decisions you made to the log. I dont want ahytning waiting on me while I am
> not here and blocking you

## Evidence

- `docs/LIONG-006-synthetic-data.md`, "Recovery fixtures".
- `scripts/test_load_p3d.py` passed on SQL Server 2022 on 2026-10-13: the loads in
  order, the base check, the unchanged reload, the refused file, the interrupted
  load, and Rbad loading with its dangling rows.
