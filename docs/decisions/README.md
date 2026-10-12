# Decision records

One file per owner decision, holding the evidence behind it. The
[decision register](../LIONG-REG-001-decisions.md) stays the summary of approval
state; a register row links here when its decision has a record.

## Index

| ID | Decision | Status | Date |
| --- | --- | --- | --- |
| [DEC-014](DEC-014-skipped-question-convention.md) | A skipped question in a decision round counts as agreement | Decided | 2026-10-11 |
| [DEC-015](DEC-015-first-generation-slice.md) | The first generation work builds the R0 backend, its answer key, and one invalid variant | Decided | 2026-10-11 |
| [DEC-016](DEC-016-hand-authored-r0.md) | R0 is hand-authored, and seeds apply only to procedurally generated worlds | Decided | 2026-10-11 |
| [DEC-017](DEC-017-r0-is-the-visible-fixture.md) | LIONG-011 calls MILESTONE-001's input the visible R0 development fixture | Decided | 2026-10-11 |
| [DEC-018](DEC-018-canonical-world-data-file.md) | A canonical world is a declarative data file checked against a JSON Schema | Decided | 2026-10-11 |
| [DEC-019](DEC-019-generator-writes-files.md) | The generator writes backend files, and a separate loader applies them | Decided | 2026-10-11 |
| [DEC-020](DEC-020-vendor-style-backends.md) | Two synthetic backends follow SmartPlant P&ID and AutoCAD Plant 3D storage closely, with original names | Decided | 2026-10-11 |
| [DEC-021](DEC-021-synthetic-world-terms.md) | The glossary defines canonical world, source representation, and world lineage | Decided | 2026-10-11 |
| [DEC-022](DEC-022-postgresql-on-neon.md) | PostgreSQL on Neon hosts the synthetic backend | Superseded | 2026-10-11 |
| [DEC-023](DEC-023-guardrails-first.md) | The way-of-working guardrails land as five pull requests before the synthetic-data work | Decided | 2026-10-11 |
| [DEC-024](DEC-024-decision-records.md) | Each decision has its own record, and the register stays the summary | Decided | 2026-10-11 |
| [DEC-025](DEC-025-python-and-uv.md) | The generator uses Python 3.12 with dependencies locked by uv | Decided | 2026-10-11 |
| [DEC-026](DEC-026-reachable-backend-close-to-vendors.md) | The backend database is reachable from any of the owner's machines and runs on the engine closest to both vendors | Decided | 2026-10-11 |
| [DEC-027](DEC-027-sql-server-on-azure.md) | Both backends run on SQL Server, hosted on an Azure SQL Database free-offer database | Decided | 2026-10-11 |
| [DEC-028](DEC-028-one-database-two-schemas.md) | Both vendor schemas live in one database | Decided | 2026-10-11 |
| [DEC-029](DEC-029-two-canonical-worlds.md) | There are two canonical worlds, each generated into one vendor's schema | Decided | 2026-10-11 |
| [DEC-030](DEC-030-plant-3d-backend-first.md) | MILESTONE-001 builds the Plant 3D-style backend first | Decided | 2026-10-11 |
| [DEC-031](DEC-031-stored-data-not-behaviour.md) | The backends copy each application's saved data, not its editing behaviour | Decided | 2026-10-11 |
| [DEC-032](DEC-032-minimal-data-dictionary.md) | Each backend carries a minimal data dictionary for the classes R0 uses | Decided | 2026-10-11 |
| [DEC-033](DEC-033-architecture-wording.md) | ARCHITECTURE.md describes two synthetic backends that follow vendor storage patterns | Decided | 2026-10-11 |
| [DEC-034](DEC-034-r0-smartplant-cross-check.md) | R0 is also generated in SmartPlant form, as a test fixture for the two mappings | Decided | 2026-10-11 |
| [DEC-035](DEC-035-r0-is-the-autodesk-world.md) | R0 is the Autodesk world, and a new world W-SP is the SmartPlant world | Decided | 2026-10-12 |
| [DEC-036](DEC-036-w-sp-new-plant.md) | W-SP is a new hand-authored plant about R0's size, built around what SmartPlant stores differently | Decided | 2026-10-12 |
| [DEC-037](DEC-037-revision-snapshots.md) | Each source revision is one complete backend snapshot that fills in the vendor's own revision fields | Decided | 2026-10-12 |
| [DEC-038](DEC-038-moc-outside-vendor-schemas.md) | MOC records stay a separate source representation, outside both vendor schemas | Decided | 2026-10-12 |
| [DEC-039](DEC-039-approval-in-vendor-fields.md) | Each backend stores the source approval in its vendor's own fields | Decided | 2026-10-12 |
| [DEC-040](DEC-040-plant-3d-patterns.md) | The Plant 3D-style schema borrows six patterns from the vendor research, renamed and cited | Decided | 2026-10-12 |
| [DEC-041](DEC-041-vendor-style-backend-term.md) | The glossary defines vendor-style backend | Decided | 2026-10-12 |
| [DEC-042](DEC-042-w-sp-scn-001-first.md) | W-SP starts with only the SCN-001 equivalent | Decided | 2026-10-12 |
| [DEC-043](DEC-043-no-foreign-keys.md) | The vendor-style relationship tables have no foreign-key constraints | Decided | 2026-10-12 |
| [DEC-044](DEC-044-stable-separate-keys.md) | Keys stay the same across a world's snapshots, and the backends never share keys | Decided | 2026-10-12 |
| [DEC-045](DEC-045-revision-time-sources.md) | Each revision time comes from the system that records it | Decided | 2026-10-12 |
| [DEC-046](DEC-046-next-pr-order.md) | The next pull requests land in a set order | Decided | 2026-10-12 |
| [DEC-047](DEC-047-loader-outbox-schema.md) | The outbox lives in a third, non-vendor schema in the same SQL Server database | Decided | 2026-10-12 |

## Record format

What each status means, when a decision is Decided, and how one decision amends
another follow the way-of-working standard (`references/deciding.md`). This
section fixes only the shape that `python3 scripts/liong_facts.py check` verifies.

- **File name** `DEC-NNN-short-slug.md`, first line `# DEC-NNN: <decision>`, then a
  `Status:` line (`Proposed`, `Decided`, or `Superseded`) and a `Date: YYYY-MM-DD`
  line.
- **No raw HTML or HTML comments** anywhere outside code spans and fences.
- **Sections**, in order and none empty: `## Context`, `## Decision`,
  `## Alternatives considered`, `## Owner's words`, `## Evidence`.
- **Owner's words** in a `Decided` record: a line `The owner answered:` (or
  `said:` or `wrote:`) followed by the quote in a `>` block of plain text: letters,
  digits, spaces and ordinary punctuation. The whole section holds no HTML,
  entities, or code.
- **Supersession**: the earlier record has `Superseded by DEC-NNN on YYYY-MM-DD`,
  and the later record has a line `Amends DEC-NNN`.
- **Index**: one row per record, with the link, decision, status and date matching
  the record. Any other row in the Index table fails the check.
