# LIONG-002: Users, workflows, and requirements

Version: 0.1. Status: Draft for review.
Date: 2026-10-05.
Authority: outcome, use-case, and requirement identifiers.
Dependencies: [LIONG-001](LIONG-001-charter.md), [glossary](../GLOSSARY.md).

## Users and questions

| User | Question | Boundary |
| --- | --- | --- |
| Engineering-data reviewer | Does this extracted tag, object, or connection agree with the source? | Accepts extraction, not engineering intent |
| Maintenance or process engineer | What connects to this asset, which records concern it, and what is unknown? | Investigates; does not authorize isolation |
| Engineering-change approver | Is this proposed engineering modification approved for the demonstration? | Approves intent; validation still gates publication |

The roles are user-approved. The interaction and permission details in
[LIONG-008](LIONG-008-interfaces-and-workflows.md) are proposals.
The publisher is a system responsibility, not another engineering approval role.

## Use cases

| ID | Outcome | Trigger and workflow | Result and exception |
| --- | --- | --- | --- |
| UC-001 | OUT-001 | Approved backend revision arrives; extract, encode supported DEXPI, validate, stage | Candidate revision or explicit findings; no silent loss of unsupported content |
| UC-002 | OUT-001 | Drawing revision arrives; extract candidates, inspect source regions, resolve ambiguity | Accepted extraction or unresolved review queue; uncertainty is not a confirmed edge |
| UC-003 | OUT-002 | Source event or reconciliation detects a change; check dependencies and publish | Complete new published state; failure preserves the previous state |
| UC-004 | OUT-002 | Engineer submits proposed modification based on a named baseline; approver reviews | Recorded approval or rejection; stale baseline needs reconsideration |
| UC-005 | OUT-003 | Engineer selects an asset in a published snapshot | Connectivity, contextual records, evidence, candidate boundary valves, and known gaps |
| UC-006 | OUT-003 | Engineer selects a bounded analysis and subgraph | Versioned export and input-completeness report; no calculation result |

Example: UC-002 reports a suspected pipe crossing as unresolved. UC-005 must not
later display it as a confirmed path merely because the graph loader accepted
the candidate's syntax.

## Requirement catalog

REQ-001 through REQ-014 restate the confirmed baseline in
[REQUIREMENTS.md](../REQUIREMENTS.md). The isolation of scoring truth in REQ-015
is a new design proposal. REQ-016 preserves approved evaluation separation;
its numerical measures are proposed in LIONG-010. REQ-017 expands the accepted
role distinction into proposed access and recovery controls. REQ-018 implements
the user's documentation and traceability request. The IDs themselves are new.

| ID | Requirement | Use cases | Owning contract |
| --- | --- | --- | --- |
| REQ-001 | Convert backend records through a tested DEXPI 2.0 subset before graph publication | UC-001 | LIONG-005 |
| REQ-002 | Validate and review flat-file extraction through the shared model | UC-002 | LIONG-005, LIONG-008 |
| REQ-003 | Declare source authority and expose conflicting assertions | UC-001, UC-002 | LIONG-004 |
| REQ-004 | Preserve supported objects, connectivity, cross-sheet context, and evidence; report loss | UC-001, UC-002 | LIONG-005 |
| REQ-005 | Maintain identity through retagging and multiple appearances | UC-002, UC-003 | LIONG-004 |
| REQ-006 | Validate tags, types, parents, and mandatory attributes against declared registers | UC-003 | LIONG-005 |
| REQ-007 | Process events, reconcile missed changes, and replay without duplication | UC-003 | LIONG-005 |
| REQ-008 | Publish a complete valid revision or retain the previous published state | UC-003 | LIONG-005 |
| REQ-009 | Separate proposed states and engineering approval from published states | UC-004 | LIONG-005, LIONG-008 |
| REQ-010 | Reconstruct published history and link modifications to MOC records | UC-003, UC-004 | LIONG-005 |
| REQ-011 | Connect work orders, document locators, and measurement samples to stable assets | UC-005 | LIONG-005 |
| REQ-012 | Bound isolation support and distinguish absence of a path from insufficient evidence | UC-005 | LIONG-008 |
| REQ-013 | Export a selected subgraph with provenance and missing-input information | UC-006 | LIONG-005 |
| REQ-014 | Label public and synthetic sources and verify reuse permissions | UC-001, UC-002 | LIONG-003 |
| REQ-015 | Keep generator truth and hidden evaluation keys out of evaluated ingestion and review inputs | UC-001, UC-002 | LIONG-006, LIONG-009 |
| REQ-016 | Report automatic and reviewed extraction separately with defined denominators | UC-001, UC-002 | LIONG-010 |
| REQ-017 | Enforce scoped actions, retain audit evidence, and demonstrate recovery | UC-003, UC-004, UC-005 | LIONG-009 |
| REQ-018 | Trace approved outcomes and proposed designs through a versioned documentation package | All | LIONG-000 |

[LIONG-006](LIONG-006-synthetic-data.md#scenario-catalogue) owns scenario fixtures
and expected results. [LIONG-010](LIONG-010-evaluation.md#acceptance-matrix) owns
metrics, acceptance criteria, and the sole requirement-to-scenario mapping.
Owning contract IDs refer to documents in the [index](LIONG-000-index.md),
not deployed services.

## Responsibility mapping

| Responsibility | Requirements | Model or interface | Expected evidence |
| --- | --- | --- | --- |
| Source adapter and DEXPI mapper | REQ-001, REQ-003, REQ-004 | SourceRevision, EngineeringAssertion | Input manifest, mapping report, validated exchange artifact |
| Drawing extractor and review interface | REQ-002, REQ-004, REQ-005 | DrawingAppearance, ReviewDecision | Candidate evidence regions, decisions, identity crosswalk |
| Validator and publisher | REQ-006–REQ-010 | ValidationReport, Publication, Approval | Rejection report or complete snapshot receipt |
| Graph query and context service | REQ-011, REQ-012 | AssetLink, QueryResult | Snapshot-pinned result and source locators |
| Export service | REQ-013 | ExportManifest | Included objects, required inputs, completeness findings |
| Intake and evaluation controls | REQ-014–REQ-017 | SourceManifest, EvaluationManifest | Rights record, access test, independent score report |
| Documentation checks | REQ-018 | Document and decision IDs | Link, coverage, archive, and review results |

## Open questions

No business scope expansion is required to draft the package. Exact public-data
accuracy targets, runtime performance, dataset permissions, DEXPI tooling, and
deployment selections remain implementation gates. They cannot be closed by
approving this requirement catalog alone.
