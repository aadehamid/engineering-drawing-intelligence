# LIONG-REG-001: Decisions, approvals, and open gates

Version: 0.1. Status: Draft register for review.
Recorded: 2026-10-05.
Authority: approval state and rationale, not implementation verification.

## Status meanings

| Status | Meaning |
| --- | --- |
| Confirmed fact | Supported by an identified inspected artifact or repository state |
| User-approved decision | Explicitly accepted by the project owner during discovery |
| Proposed decision | Recommended design awaiting review |
| Working assumption | Temporary planning input, not a requirement |
| Open question | Unresolved choice requiring evidence or owner judgment |
| Implementation gate | Work that must produce specified evidence before dependent implementation or release |

Document approval, configured implementation, executed tests, measured results,
and deployed operation are separate states. None follows automatically from the
state before it. All eleven new substantive documents are drafts.

## User-approved decisions

Approval source for this table is explicit confirmation by project owner
`aadehamid` during project discovery. This is a recorded summary, not a signed
operational approval. The previously merged baseline is commit
`65f7c38ed591e07d1bc2b065973e24de87559101`.
Later provider, independence, role, and drafting confirmations are recorded here.

| ID | Decision | Rationale and consequence | Authoritative location |
| --- | --- | --- | --- |
| DEC-001 | LIONG is independent; PPC is a reference, not a parent or runtime dependency | Reuse relevant patterns without importing enterprise scope or automatic upstream changes | LIONG-001; root REQUIREMENTS |
| DEC-002 | Support backend through DEXPI 2.0 and reviewed flat files through a shared engineering model | Structured and document-derived sources must preserve compatible engineering meaning | LIONG-002, REQ-001–REQ-004 |
| DEC-003 | Declare source authority and retain stable identities independent of tags | Conflicting sources cannot silently overwrite one another or merge assets | REQ-003, REQ-005 |
| DEC-004 | Validate complete revisions, preserve history, and separate proposed states | Invalid partial changes must not alter the accepted graph | REQ-006–REQ-010 |
| DEC-005 | Use one shared graph with typed domain relationships | Demonstrate connected domains without mandatory federation | LIONG-001; root REQUIREMENTS |
| DEC-006 | Demonstrate work orders, document links, measurement samples, and MOC records | Show operational context with public or labeled synthetic examples | REQ-011 |
| DEC-007 | Bound isolation support and export analysis inputs without executing specialist analysis | Avoid implying safety authorization or validated calculations | REQ-012, REQ-013 |
| DEC-008 | Use public and synthetic data; keep evaluation results distinct | Public availability is not reuse permission; generated data does not establish real-world performance | REQ-014, REQ-016 |
| DEC-009 | Permit Cloudflare and Databricks Free Edition as open-source exceptions | Assess their fit without making them mandatory or authorizing spending | LIONG-007 |
| DEC-010 | Reviewer, consumer, and separate engineering-change approver roles | One demonstrator may exercise roles, but actions record the active role and do not authorize isolation | LIONG-002, LIONG-008 |
| DEC-011 | Produce the document sequence in a batch, commit it, and open a PR | Owner will review later; permission to draft is not approval of new technical proposals | LIONG-000 |
| DEC-012 | Exclude authoring and assess modern extraction tools, including Hugging Face options | Backend and existing/synthetic drawing ingestion remain the scope; do not default to a hand-built OpenCV/Tesseract pipeline | LIONG-001, LIONG-007 |
| DEC-013 | Allow assessment of proprietary parsing and model APIs | Comparison design and public-documentation research are allowed; provider selection, uploads, paid calls and custom model-license acceptance require explicit gates | Root REQUIREMENTS; LIONG-007/009 |
| DEC-014 | A question the owner skips in a decision round counts as agreement with the recommendation | Asked on 2026-10-11: "When you don't answer a question in a decision round, should I treat that as agreement with my recommendation?" The owner answered "Q12: yes". A record of a skipped question quotes the round it was asked in | AGENTS.md; [record](decisions/DEC-014-skipped-question-convention.md) |
| DEC-015 | The first generation work builds the R0 backend, its answer key, and one invalid variant | Owner accepted the Q1 recommendation | LIONG-006, LIONG-011; [record](decisions/DEC-015-first-generation-slice.md) |
| DEC-016 | R0 is hand-authored, and seeds apply only to procedurally generated worlds | Owner accepted the Q2 recommendation | LIONG-006; [record](decisions/DEC-016-hand-authored-r0.md) |
| DEC-017 | LIONG-011 calls MILESTONE-001's input the visible R0 development fixture | Owner accepted the Q3 recommendation | LIONG-011; [record](decisions/DEC-017-r0-is-the-visible-fixture.md) |
| DEC-018 | A canonical world is a declarative data file checked against a JSON Schema | Owner accepted the Q4 recommendation | LIONG-006; [record](decisions/DEC-018-canonical-world-data-file.md) |
| DEC-019 | The generator writes backend files, and a separate loader applies them | Owner accepted the Q5 recommendation | LIONG-006, LIONG-009; [record](decisions/DEC-019-generator-writes-files.md) |
| DEC-020 | Two synthetic backends follow SmartPlant P&ID and AutoCAD Plant 3D storage closely, with original names | Owner's Q6 and Q9 answers: reverse engineer how each stores its objects, borrow the patterns very closely, and use the project's own names | ARCHITECTURE.md, LIONG-003, LIONG-006; [record](decisions/DEC-020-vendor-style-backends.md) |
| DEC-021 | The glossary defines canonical world, source representation, and world lineage | Owner accepted the Q7 recommendation | GLOSSARY.md; [record](decisions/DEC-021-synthetic-world-terms.md) |
| DEC-022 | PostgreSQL on Neon hosts the synthetic backend | Superseded by DEC-027 on 2026-10-11 | LIONG-007; [record](decisions/DEC-022-postgresql-on-neon.md) |
| DEC-023 | The way-of-working guardrails land as five pull requests before the synthetic-data work | Owner accepted the Q10 recommendation | AGENTS.md; [record](decisions/DEC-023-guardrails-first.md) |
| DEC-024 | Each decision has its own record, and the register stays the summary | Owner accepted the Q11 recommendation | docs/decisions; [record](decisions/DEC-024-decision-records.md) |
| DEC-025 | The generator uses Python 3.12 with dependencies locked by uv | Owner accepted the Q13 recommendation | LIONG-007; [record](decisions/DEC-025-python-and-uv.md) |
| DEC-026 | The backend database is reachable from any of the owner's machines and runs on the engine closest to both vendors | Owner's Q14 answer: Neon was chosen only for access from any machine; the engine follows the vendors unless that proves really difficult | LIONG-007; [record](decisions/DEC-026-reachable-backend-close-to-vendors.md) |
| DEC-027 | Both backends run on SQL Server, hosted on an Azure SQL Database free-offer database | Owner accepted the Q21 recommendation | LIONG-007; [record](decisions/DEC-027-sql-server-on-azure.md) |
| DEC-028 | Both vendor schemas live in one database | Owner's Q15 answer, in place of the recommended separate databases | LIONG-007; [record](decisions/DEC-028-one-database-two-schemas.md) |
| DEC-029 | There are two canonical worlds, each generated into one vendor's schema | Owner's Q16 and Q22 answers. Which world is which is decided in DEC-035 | LIONG-006; [record](decisions/DEC-029-two-canonical-worlds.md) |
| DEC-030 | MILESTONE-001 builds the Plant 3D-style backend first | Owner accepted the Q17 recommendation | LIONG-011; [record](decisions/DEC-030-plant-3d-backend-first.md) |
| DEC-031 | The backends copy each application's saved data, not its editing behaviour | Owner accepted the Q18 recommendation | LIONG-006; [record](decisions/DEC-031-stored-data-not-behaviour.md) |
| DEC-032 | Each backend carries a minimal data dictionary for the classes R0 uses | Owner accepted the Q19 recommendation | LIONG-006; [record](decisions/DEC-032-minimal-data-dictionary.md) |
| DEC-033 | ARCHITECTURE.md describes two synthetic backends that follow vendor storage patterns | Owner accepted the Q20 recommendation | ARCHITECTURE.md, LIONG-003, LIONG-006; [record](decisions/DEC-033-architecture-wording.md) |
| DEC-034 | R0 is also generated in SmartPlant form, as a test fixture for the two mappings | Owner's answer to Q23: keep the cross check | LIONG-006; [record](decisions/DEC-034-r0-smartplant-cross-check.md) |
| DEC-035 | R0 is the Autodesk world, and a new world W-SP is the SmartPlant world | Owner's answer on 2026-10-12: "yes, R0 is Autodesk and W-SP is SmartPlant" | LIONG-006; [record](decisions/DEC-035-r0-is-the-autodesk-world.md) |
| DEC-036 | W-SP is a new hand-authored plant about R0's size, built around what SmartPlant stores differently | Owner accepted the Q24 recommendation; exact contents in DEC-052, which stands by DEC-054 | [record](decisions/DEC-036-w-sp-new-plant.md) |
| DEC-037 | Each source revision is one complete backend snapshot that fills in the vendor's own revision fields | Owner accepted the Q25 recommendation | [record](decisions/DEC-037-revision-snapshots.md) |
| DEC-038 | MOC records stay a separate source representation, outside both vendor schemas | Owner accepted the Q26 recommendation | [record](decisions/DEC-038-moc-outside-vendor-schemas.md) |
| DEC-039 | Each backend stores the source approval in its vendor's own fields | Owner accepted the Q27 recommendation | [record](decisions/DEC-039-approval-in-vendor-fields.md) |
| DEC-040 | The Plant 3D-style schema borrows six patterns from the vendor research, renamed and cited | Owner accepted the Q28 recommendation | [record](decisions/DEC-040-plant-3d-patterns.md) |
| DEC-041 | The glossary defines vendor-style backend | Owner accepted the Q29 recommendation | [record](decisions/DEC-041-vendor-style-backend-term.md) |
| DEC-042 | W-SP starts with only the SCN-001 equivalent | Owner accepted the Q30 recommendation | [record](decisions/DEC-042-w-sp-scn-001-first.md) |
| DEC-043 | The vendor-style relationship tables have no foreign-key constraints | Owner accepted the Q31 recommendation | [record](decisions/DEC-043-no-foreign-keys.md) |
| DEC-044 | Keys stay the same across a world's snapshots, and the backends never share keys | Owner accepted the Q32 recommendation | [record](decisions/DEC-044-stable-separate-keys.md) |
| DEC-045 | Each revision time comes from the system that records it | Owner accepted the Q33 recommendation | [record](decisions/DEC-045-revision-time-sources.md) |
| DEC-046 | The next pull requests land in a set order | Owner accepted the Q34 recommendation | [record](decisions/DEC-046-next-pr-order.md) |
| DEC-047 | The outbox lives in a third, non-vendor schema in the same SQL Server database | Owner chose option (b) of Q35: "go with b" | [record](decisions/DEC-047-loader-outbox-schema.md) |
| DEC-048 | The agent decides open questions for the owner during the night run of 2026-10-13 | Owner said: "you shpuld decide for me unless it is aboslutely not clear what decisions to make" | [record](decisions/DEC-048-night-delegation.md) |
| DEC-053 | Main's history stays as it is, with four commits authored by a test identity | Owner answered "leave it" | [record](decisions/DEC-053-main-history-stays.md) |
| DEC-054 | DEC-048's delegation takes precedence over DEC-036's reservation, so W-SP's contents stand | Owner answered: "My delegation takes precedence. You can settel it" | [record](decisions/DEC-054-delegation-takes-precedence.md) |
| DEC-055 | This round chooses components for MILESTONE-001's slice only, and a gate closes when a PR lands its closure evidence | Owner answered Q1 with "yes to all" | [record](decisions/DEC-055-slice-choices-close-gates-on-evidence.md) |
| DEC-056 | The slice's graph store is Neo4j Community 2026.09.0, run from a pinned image locally and in CI | Owner answered Q2 with "yes to all" | [record](decisions/DEC-056-neo4j-for-the-slice.md) |
| DEC-057 | Step 5 is a parameterized Cypher query run through the official neo4j Python driver, with no UI in the slice | Owner answered Q3 with "yes to all" | [record](decisions/DEC-057-cypher-query-no-ui.md) |
| DEC-058 | The slice's manifests and publication receipt are JSON files in a run output folder, with no PostgreSQL | Owner answered Q4 with "yes to all" | [record](decisions/DEC-058-json-run-manifests.md) |
| DEC-059 | Step 6 compares the published graph with the answer key and requires an exact match | Owner answered Q5 with "yes to all" | [record](decisions/DEC-059-exact-answer-key-comparison.md) |
| DEC-060 | Each slice step is a plain Python command, chained by one script, with no orchestrator | Owner answered Q6 with "yes to all" | [record](decisions/DEC-060-plain-python-orchestration.md) |
| DEC-061 | The slice targets DEXPI 2.0.1, pinned at the specification's V2.0.1 tag | Owner answered Q7 with "yes to all" | [record](decisions/DEC-061-dexpi-2-0-1.md) |
| DEC-062 | Pinned copies of the DEXPI model files live in the repository, and validation never fetches over the network | Owner answered Q8 with "yes to all" | [record](decisions/DEC-062-vendored-model-files.md) |
| DEC-063 | LIONG writes its own DEXPI 2.0.1 generator and parser for the supported subset, on lxml | Owner answered Q9 with "yes to all" | [record](decisions/DEC-063-own-dexpi-generator-and-parser.md) |
| DEC-064 | A DEXPI file is valid only when it passes four named validation stages and an exact round trip | Owner accepted Q10 and Q14 ("I am good") | [record](decisions/DEC-064-four-stage-dexpi-validation.md) |
| DEC-065 | A DEXPI validity claim names only the stages that ran, never conformance or certification | Superseded by DEC-072 on 2026-10-13 | [record](decisions/DEC-065-claim-names-stages-that-ran.md) |
| DEC-066 | The parser also reads DEXPI's own 2.0.1 reference P&ID and reports what it does not support | Owner answered Q11 with "yes to all" | [record](decisions/DEC-066-reference-pid-parser-test.md) |
| DEC-067 | Every new slice component is pinned exactly, at the latest release at least 14 days old | Owner answered Q12 with "yes to all" | [record](decisions/DEC-067-exact-pins.md) |
| DEC-068 | The glossary defines supported subset | Owner answered Q13 with "yes to all" | [record](decisions/DEC-068-supported-subset-term.md) |
| DEC-069 | bpmn2dexpi is recorded as a candidate validator and kept out of the slice | Owner accepted Q16 ("I am good") | [record](decisions/DEC-069-bpmn2dexpi-recorded-not-used.md) |
| DEC-070 | A general delivery playbook for engineering-data-to-graph projects lives in this repository | Owner accepted Q17 to Q23, with comments that the playbook holds no project-specific items and no pull request references | [record](decisions/DEC-070-delivery-playbook.md) |
| DEC-071 | A pull request that settles an engineering practice updates the playbook in the same pull request | Owner accepted Q19 and Q22, with the comments recorded in the record | [record](decisions/DEC-071-playbook-grows-with-prs.md) |
| DEC-072 | A DEXPI validity claim names every stage that ran, including the reference checks | Owner answered: "yes, add it to #32" | [record](decisions/DEC-072-claim-names-every-stage-that-ran.md) |
| DEC-073 | The agent decides open questions for the owner during the night run of 2026-10-14 | Owner answered: "you have my permission to decide for me using every available data and external search of hgih quality sources to resolve any ambiquity" | [record](decisions/DEC-073-second-night-delegation.md) |

## Decisions made under delegation

The agent made these during two night runs, under the owner's delegations. Each row's
Basis names its run's delegation: [DEC-048](decisions/DEC-048-night-delegation.md) for
2026-10-13 and [DEC-073](decisions/DEC-073-second-night-delegation.md) for 2026-10-14. The owner has not reviewed them;
each can be reversed by a later owner decision.

| ID | Decision | Basis | Authoritative location |
| --- | --- | --- | --- |
| DEC-049 | The Plant 3D-style schema is one T-SQL file, tested on SQL Server in CI, with tags split as the product splits them | Decided by the agent under DEC-048 | [record](decisions/DEC-049-plant-3d-schema-choices.md) |
| DEC-050 | The Plant 3D-style generator writes one JSON file per table per revision, with a separate answer key | Decided by the agent under DEC-048 | [record](decisions/DEC-050-p3d-generator-choices.md) |
| DEC-051 | The loader replaces the backend's rows with a snapshot and raises one outbox event per revision | Decided by the agent under DEC-048 | [record](decisions/DEC-051-p3d-loader-choices.md) |
| DEC-052 | W-SP is a two-sheet transfer line whose one pipeline is two runs, with three inline valves | Decided by the agent under DEC-048; stands by DEC-054 | [record](decisions/DEC-052-w-sp-contents.md) |
| DEC-074 | The pinned DEXPI 2.0.1 files are the XSD, the Core and Plant models and the reference P&ID, with the models taken from the published specification | Decided by the agent under DEC-073 | [record](decisions/DEC-074-dexpi-2-0-1-pinned-files.md) |

## New proposals

| ID | Proposal and alternative | Recommendation and consequence | Review authority |
| --- | --- | --- | --- |
| DEC-101 | Local baseline versus mandatory hosted operation | Local reproducible baseline; assess hosted services as optional. Requires durable local artifacts rather than copying PPC's “local is scratch” rule unchanged | Project owner, LIONG-007/009 |
| DEC-102 | One canonical synthetic plant versus unrelated plausible tables | Generate coherent truth, then independent source views; isolate scoring keys. More generator discipline, less false confidence | Project owner, LIONG-006/010 |
| DEC-103 | Immutable candidate snapshots versus in-place graph edits | Validate snapshots and atomically activate one publication with expected-base checks. Costs storage but makes replay and history testable | Project owner, LIONG-005/007 |
| DEC-104 | Evidence-bearing assertions versus bare graph facts | Retain source locators, revision, and uncertainty. More metadata, but supports review and contradictions | Project owner, LIONG-004/005 |
| DEC-105 | Explicit action contracts versus free-form graph mutation | Browser/API actions enforce roles, hashes, and stale-base checks. No graph-edit shortcut around source authority | Project owner, LIONG-008/009 |
| DEC-106 | Minimal PPC-derived components versus whole PPC stack | Evaluate PostgreSQL, operational graph, orchestration, review UI, and needed validation first; defer unrelated analytics and agent services | Project owner, LIONG-007 |
| DEC-107 | Exact synthetic checks plus separate public evaluation versus one aggregate score | Critical control failures always block; automatic and reviewed accuracy remain separate | Project owner, LIONG-010 |
| DEC-108 | Bounded standards mapping versus wholesale ontology import | Map only inspected definitions and required dependencies; leave unsupported equivalences unresolved | Project owner, LIONG-003/004 |
| DEC-109 | Drawing-baseline acceptance versus engineering approval | Permit initial publication with engineering decision not applicable; require distinct source approval and a new approved baseline publication before engineering proposals use it as their base. Never relabel historical acceptance as approval | Project owner, LIONG-005/008 |
| DEC-110 | Pluggable parsing and visual interpretation versus OCR-centric custom extraction | Compare LiteParse, hosted parsers, document models and a general vision-language model in their respective roles; treat SAM 3 as an optional segmentation experiment, not a parser or graph generator | Project owner, LIONG-005/007/010 |
| DEC-111 | Evidence-based model admission versus adoption from general benchmarks | Require engineering fixtures, source-region checks, repeat-run records, hardware/cost cohorts and license/data-processing review before selection; no downstream publication authority for model outputs | Project owner, LIONG-007/009/010 |

These are proposal groups. Document-local gate IDs retain finer-grained evidence
requirements. Approval must identify which groups or sections it covers.

## Facts and assumptions

| ID | Classification | Statement | Evidence or boundary |
| --- | --- | --- | --- |
| FACT-001 | Confirmed fact | PPC at `01027a84be5d453cbb4e2ea091e4884729918b15` provides documentation and placeholders, not runnable pipeline code | REF-PPC-001 and the inspected tree |
| FACT-002 | Confirmed fact | LIONG's original documentation PR was merged before this package | Baseline commit above |
| ASM-001 | Working assumption | One operator can demonstrate the user roles locally | Not a production identity or segregation-of-duties control |
| ASM-002 | Working assumption | A bounded multi-sheet synthetic case is sufficient to start engineering-fidelity tests | Public-data generalization still requires separate evidence |
| ASM-003 | Working assumption | No delivery deadline or production workload has been specified | Do not invent an SLA or infer performance from a free tier |

## Open questions and package-level gates

| ID | Decision or evidence needed | What it blocks | Closure evidence |
| --- | --- | --- | --- |
| GATE-001 | Exact DEXPI 2.0 artifact, encoding, parser, and validation compatibility | Claiming standards-compliant structured ingestion | Pinned artifacts, license record, positive/negative round-trip fixtures |
| GATE-002 | Rights and suitability of selected public drawings and structured examples | Redistributing datasets or reporting representative public evaluation | Exact files, usage terms, attribution, independent annotation protocol |
| GATE-003 | Component versions, editions, licenses, dependencies, and interoperability | Declaring the technology selection implementation-ready | Reproducible dependency lock and bounded compatibility tests |
| GATE-004 | Cloudflare/Databricks account-specific limits and permissions | Provisioning or relying on hosted durability/connectivity | Owner authorization, current terms, limit/cost model, connectivity and export test |
| GATE-005 | Snapshot publication and recovery mechanics in selected storage | Claiming atomic updates or reproducible history | Reader-consistency, failure-injection, restore, and replay results |
| GATE-006 | Named downstream analysis and its required inputs | Claiming analysis-ready export for a particular calculation | Versioned analysis profile, required quantities/units, completeness fixtures |
| GATE-007 | Public evaluation thresholds and workload budgets | Declaring public accuracy or performance acceptance | Frozen datasets, baseline measures, hardware/workload definition, owner-approved targets |
| GATE-008 | Review of all new design proposals and document versions | Treating the package as an approved implementation specification | Document/section approvals with version and unresolved exceptions |

DEC-055 to DEC-069 choose the components for MILESTONE-001's slice under GATE-001
and GATE-003. Both gates stay open until a pull request lands their closure
evidence ([DEC-055](decisions/DEC-055-slice-choices-close-gates-on-evidence.md)).

Source-specific gates in LIONG-003, technology gates in LIONG-007, and operational
gates in LIONG-009 refine this list. Closing one gate does not close the others.

## Approval and change procedure

Record document ID, version, reviewed commit or checksum, approving role, explicit
scope, qualifications, and recorded date. If the document changes before approval,
do not apply an earlier approval to materially different content.

“Reviewed and approved” approves that identified document and its clearly marked
proposals, subject to stated qualifications. It does not certify code or executed
tests. A PR merge alone must not be interpreted as approval of every draft proposal
unless the owner says that is the merge's intent.

New proposals become approved only through that record. Material amendments to an
approved decision create a new decision entry with a supersedes link and a clear
review request. Link corrections and status maintenance need no new design decision.

## Current package review record

| Artifact | Version | State | Approval scope |
| --- | --- | --- | --- |
| Root REQUIREMENTS and GLOSSARY | Baseline plus accepted discovery amendments | User-approved decisions recorded | DEC-001 through DEC-010 and DEC-012 through DEC-013; no pipeline implementation |
| LIONG-001 through LIONG-011 | 0.1 | Draft for review | None yet |
| Index, reference register, this register | 0.1 | Review aids | Not approval of referenced tools or external artifacts |
