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
