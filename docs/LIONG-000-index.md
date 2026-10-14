# LIONG-000: Documentation index and review guide

Version: 0.1. Status: Draft package for review.
Date: 2026-10-05.
Authority: document ownership, reading order, and package status.

## Start here

LIONG is independent of PPC. The package adapts relevant PPC documentation and
architecture patterns to the already agreed engineering drawing-to-graph scope.
The owner authorized batch drafting and a PR, not automatic approval of new designs.

Read [LIONG-001](LIONG-001-charter.md) for the purpose and boundaries.
Then review [the decisions](LIONG-REG-001-decisions.md), especially DEC-101 through
DEC-111 and GATE-001 through GATE-008. All eleven substantive documents are version
0.1 drafts. Only MILESTONE-001's structured slice is implemented and tested, on the synthetic
R0 world ([LIONG-010](LIONG-010-evaluation.md#current-evidence-and-implementation-handoff)).

The extraction assessment amendment adds modern parsers, vision-language models,
and optional SAM 3 segmentation. No authoring application is included. Compare
the candidate responsibilities and gates in LIONG-007 before approving selection.
The draft version is identified by its repository commit and archive hashes;
this amendment does not approve the other outstanding design proposals.

## Document map

| ID | Document | Owns | Depends on | Review focus |
| --- | --- | --- | --- | --- |
| LIONG-001 | [Charter](LIONG-001-charter.md) | Problem, outcomes, scope, exclusions | Approved baseline | Preserve scope; review demonstration boundary |
| LIONG-002 | [Users and requirements](LIONG-002-users-and-requirements.md) | OUT, UC, REQ IDs and responsibility trace | 001 | User needs and coverage |
| LIONG-003 | [Sources and ontology](LIONG-003-sources-and-ontology.md) | Source eligibility and proposed vocabulary mappings | 001–002 | Rights, exact versions, semantic fit |
| LIONG-004 | [Domain model](LIONG-004-domain-model.md) | Identity and relationship meaning | 002–003 | Tags, appearances, authority, uncertainty |
| LIONG-005 | [Data contracts](LIONG-005-data-contracts.md) | Logical fields, revisions, publication, export | 003–004 | Temporal behavior and failure boundaries |
| LIONG-006 | [Synthetic data](LIONG-006-synthetic-data.md) | Canonical fixtures, scenario definitions, expected results, and source materialization | 003–005 | Visible development examples versus protected held-out truth |
| LIONG-007 | [Stack and architecture](LIONG-007-stack-and-architecture.md) | Component responsibilities and PPC reuse assessment | 002–006 | Minimum components, licensing, compatibility |
| LIONG-008 | [Interfaces and workflows](LIONG-008-interfaces-and-workflows.md) | User actions, request contracts, review flows | 002, 005, 007 | Role authority and evidence-first interaction |
| LIONG-009 | [Governance and operations](LIONG-009-governance-and-operations.md) | Access, retention, observability, recovery | 005–008 | Enforced controls, not labels alone |
| LIONG-010 | [Evaluation](LIONG-010-evaluation.md) | Scoring, canonical requirement-to-scenario mapping, acceptance evidence | 002–009 | Exact fixtures, denominators, critical gates |
| LIONG-011 | [Build runbook](LIONG-011-build-runbook.md) | Dependency order and first implementation milestone | 001–010 | What must be approved and verified before building |
| LIONG-REG-001 | [Decision register](LIONG-REG-001-decisions.md) | Approvals, proposals, assumptions, gates | All | No silent promotion of drafts |
| LIONG-REF-001 | [Reference register](LIONG-REF-001-reference-register.md) | External evidence and permissions | 003, 007 | Pinned claims and unresolved rights |

The [delivery playbook](delivery-playbook.md) is a general guide for teams on
similar projects, not a LIONG design document. It holds reusable engineering
practice, and LIONG's own documents stay authoritative for LIONG
([DEC-070](decisions/DEC-070-delivery-playbook.md)).

## Authoritative definitions

[GLOSSARY.md](../GLOSSARY.md) owns agreed terminology. The domain document proposes
additional concepts without silently rewriting approved terms.
[REQUIREMENTS.md](../REQUIREMENTS.md) preserves the owner-approved baseline.
LIONG-002 assigns reviewable IDs to that baseline and labels proposed extensions.

The earlier [problem statement](../PROBLEM_STATEMENT.md) and
[architecture overview](../ARCHITECTURE.md) remain baseline summaries. New drafts
do not supersede them until the owner approves an identified version.
For conflicts, preserve the approved requirement and record a proposal to change it.
Do not use the newest file timestamp as authority.

The docs package has one authority for each detailed contract. Other documents
reference that authority rather than creating independent definitions.
OUT → UC → REQ → model/interface responsibility → SCN traces appear in LIONG-002
and LIONG-010. DEC and REF IDs identify decisions and evidence.

## What to review first

1. Confirm that the charter preserves the approved independent LIONG scope.
2. Review DEXPI compatibility and public-data permission findings in LIONG-003.
3. Review PPC reuse, provider constraints, and proposed component selection in LIONG-007.
4. Review proposed identity, publication, authority, and access contracts in 004–005 and 008–009.
5. Review synthetic truth isolation and measurable acceptance in 006 and 010.
6. Approve the first milestone and its gates only when the preceding contracts are ready.

A review may approve some documents or sections and leave others open.
Record qualifications explicitly. Approval of design is not evidence of configured
software, executed tests, measured accuracy, or operational safety.

## Package and reproducibility

Each linked document is a standalone Markdown file. The
[complete review archive](releases/LIONG-review-package-v0.1.zip) contains those
files with the root baseline and a manifest of file hashes.

Run `uv run python scripts/check_docs.py` from the repository root to check local links,
document presence, cross-referenced requirement/scenario IDs, and basic formatting.
Run `uv run python scripts/bundle_docs.py --check` to check archive freshness.
These are documentation checks, not engineering acceptance tests.

## PPC reuse summary

Reuse the distinction between business meaning and computation, explicit source
authority, coherent synthetic generation, inspectable source evidence, versioned
artifacts, and isolated evaluation truth. Adapt them to P&IDs and revision approval.

Do not inherit commercial KPIs, broad source-system simulation, separate analytical
and semantic services without a need, or the assumption that local disk is always
disposable. The exceptions to the open-source condition, and their limits, are listed once, in
[REQUIREMENTS.md](../REQUIREMENTS.md#context). Component choices and gates are in LIONG-007.

## Current evidence

The package documents intended behavior and inspected public references.
It does not claim executed DEXPI interoperability, verified provider-account
capabilities, public-drawing accuracy, runtime performance, or a deployed system.
The PR validation report will state exactly which documentation checks ran.
