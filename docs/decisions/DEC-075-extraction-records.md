# DEC-075: Extraction writes LIONG-005's source records from the backend's tables, keyed by the backend's own object IDs

Status: Decided
Date: 2026-10-14

## Context

MILESTONE-001 step 2 extracts source records without reading the hidden scoring
truth ([the build runbook](../LIONG-011-build-runbook.md)). [LIONG-005](../LIONG-005-data-contracts.md)
names the logical records but leaves their files, identifiers and relationship names
open. The agent decided them during the night run of 2026-10-14, under the owner's
delegation in [DEC-073](DEC-073-second-night-delegation.md). The owner can reverse
any of them.

## Decision

1. **Two readers, one result.** `scripts/extract_p3d.py` reads the fifteen p3d tables
   either from SQL Server, as loaded by `scripts/load_p3d.py`, or from a snapshot
   folder after checking it against its manifest. Both give the same records; a CI
   test compares them for R0, R1 and R2.
2. **Records.** One JSON file holds a SourceManifest, a SourceRevision, and the
   EngineeringObject, TagAssignment, EngineeringAssertion and DrawingAppearance
   records the rows state. Every record names the table and row it came from. The
   SourceRevision carries the time the source recorded the revision: the outbox
   event's time from the database, or the manifest's time for a snapshot.
3. **Identity.** An object is `p3d:object:<ObjectId>` and a drawing is
   `p3d:drawing:<DrawingId>`: the backend's own keys, which stay the same across a
   world's snapshots ([DEC-044](DEC-044-stable-separate-keys.md)). No generator-private
   identity is used.
4. **Relationships as stated.** Each relationship row becomes one assertion, named
   for what the row says: `starts_at` and `ends_at` (SegmentStart, SegmentEnd),
   `connects_to` (ConnectorPair), `continues_to` (SheetConnectorLink) and `owned_by`
   (Ownership). Extraction does not turn them into flows and does not judge them: a
   row that names a missing object, as in Rbad, is kept for validation to reject.
5. **Not extracted yet.** WorkHistory and the PlantObject bookkeeping columns belong
   to revision handling in later milestones. So do these LIONG-005 fields, which the
   records leave out: facility and scope IDs, the predecessor revision, artifact
   references, tag validity intervals and drawing page IDs.
6. **No answer key.** A test records every file the extractor opens through Python's
   open functions, for all four revisions, and fails if any is an answer key.

## Alternatives considered

- Read only the snapshot files. The backend is the source the runbook names; the
  files are how it was loaded.
- Derive flow edges during extraction. That moves graph meaning into the step whose
  job is to report what the source says.

## Owner's words

Given on 2026-10-14 and recorded in [DEC-073](DEC-073-second-night-delegation.md).

The owner answered:

> you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity

## Evidence

- `scripts/test_extract_p3d.py`, whose expected records are typed by hand from R0.
