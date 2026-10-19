# LIONG-011: Implementation roadmap and build runbook

Version: 0.1. Status: Draft for review.
Date: 2026-10-05.
Authority: proposed build order, prerequisites, and verification checkpoints.
Dependencies: LIONG-001 through LIONG-010 and
[decision register](LIONG-REG-001-decisions.md).

## Current state

The repository contains documentation, documentation-checking utilities, and the
first synthetic backend: R0's canonical world file, the Plant 3D-style schema, a
generator that writes R0's backend snapshots and answer key, and a loader that applies
a snapshot and its outbox event to SQL Server. CI applies the schema and loads the
snapshots on a SQL Server container. MILESTONE-001's structured slice is built:
`scripts/run_slice.py` runs steps 2 to 6 below on R0 to R2, publishing each to a Neo4j
service in CI, and rejects Rbad before publication ([LIONG-010](LIONG-010-evaluation.md#current-evidence-and-implementation-handoff)).
Step 1 runs in CI too, as the schema and snapshot loads on a throwaway SQL Server
database. Nothing else here is built, and no hosted database has been provisioned. The
stages after MILESTONE-001 are future implementation work, not commands already executed.

Document approval and gate closure precede dependent build work. No step here
authorizes cloud provisioning, charges, sensitive data, or publishing datasets.

## First concrete milestone

MILESTONE-001 is a verified structured vertical slice:

1. Materialize a small synthetic engineering backend from the visible R0 development fixture.
2. Extract source records without reading the hidden scoring truth.
3. Generate the selected DEXPI 2.0 representation and validate its supported subset.
4. Parse and publish one immutable engineering graph snapshot.
5. Query a known cross-sheet connection and return its source evidence.
6. Compare the output to the independent expected model and publish a test report.

The milestone includes SCN-001 and a minimal invalid-reference rejection from
SCN-005. It does not establish flat-file accuracy, live synchronization,
production readiness, or safe isolation.

Before starting, close GATE-001 and the component subset of GATE-003 needed for
this slice. GATE-001 is closed, and so is the slice's part of GATE-003
([DEC-079](decisions/DEC-079-gate-001-003-closed-for-slice.md)). If available tooling supports only older DEXPI formats, stop that
compatibility claim and propose a documented change; do not silently downgrade.

## Build sequence

| Stage | Inputs and work | Exit evidence | Stop or recovery condition |
| --- | --- | --- | --- |
| M0: approve contracts | Review model, source policies, provider exceptions, and required tests | Approved sections/versions and unresolved-gate register | Unapproved substantive designs remain proposals |
| M1: structured slice | Implement MILESTONE-001 | Source/exchange/graph manifests and independent exact comparison | Unsupported DEXPI stops the slice, not the standards requirement |
| M2: controlled publication | Add revision events, reconciliation, candidate activation, and history | SCN-003 through SCN-008; duplicate, stale, and failure-injection reports | Failed candidate retains previous publication |
| M3: drawing review | Integrate adapters and review on visible, licensed development fixtures only | Development SCN-002 results and the candidate comparison plan; no held-out or provider benchmark admission | Uncertain edges remain unresolved; no private evaluation material or unauthorized uploads |
| M4: engineering context | Add work orders, measurement samples, documents, and MOC links | SCN-009 through SCN-012 with source locators | Missing required context is explicit |
| M5: access and recovery | Enforce roles, isolate truth, restore and replay; test protection using sacrificial canaries rather than held-out answers | SCN-013 through SCN-015 control evidence; extraction principal cannot read protected storage or leaked outputs | Critical control failure blocks release of held-out inputs to any extraction route |
| M6: bounded evaluation | After M5, freeze workload, truth, partitions, parser adapters, and metrics; run authorized candidate comparisons | SCN-002/009/010/015/016 comparison results with separate development, held-out, public, and synthetic reports | No held-out execution before controls pass; no acceptance claim without frozen measures and required authorizations |
| M7: optional hosted comparison | Assess selected Cloudflare/Databricks functions after authorization | Reproducible data movement, limits, cost boundary, export/recovery report | Hosted failure does not corrupt authoritative source or erase local evidence |

This is dependency order, not a staffing or calendar plan. No delivery date is
implied. Public data research can proceed alongside synthetic-contract work.

M3 can develop the comparison harness using the visible R0 oracle and permitted
development files. It does not satisfy blind-evaluation, isolation, or comparative
performance gates. M5 establishes the access boundary before M6 admits held-out
inputs. In M6, first freeze partitions, annotations, matching rules, and resource
cohorts; then execute comparisons. Hosted routes also require upload and spend
authorization regardless of stage. M7 is a separate optional storage/analytics
comparison, not a prerequisite that can waive M6 parsing-provider controls.

## Repository responsibilities

Proposed implementation locations, not folders that prove code exists:

| Location | Intended content |
| --- | --- |
| `schemas/` | Logical contracts, selected exchange profiles, migrations |
| `src/ingestion/` | Backend and drawing adapters |
| `src/validation/` | Cross-register, topology, provenance, and publication checks |
| `src/publication/` | Snapshot activation and revision receipts |
| `src/query/` | Snapshot-pinned traversal and export contracts |
| `apps/review/` | Evidence inspection, review, and proposal interfaces |
| `tests/` | Unit, integration, and scenario tests using visible fixtures |
| `fixtures/` | Small licensed development fixtures; not blind scoring keys |
| `docs/` | Requirements, designs, decisions, references, and review evidence |

Hidden evaluation truth belongs outside evaluated users' and services' accessible
workspace, not merely in a differently named directory. Storage and credential
boundaries are defined in [LIONG-009](LIONG-009-governance-and-operations.md).

## Build and verification procedure

When implementation begins, select supported component versions and record their
licenses, transitive dependencies, image/package hashes, and runtime requirements.
Create an environment lock only after a compatibility test. Do not substitute
“latest” for a reproducible build contract.

For each change, identify affected REQ and SCN IDs, run relevant tests, record
inputs and outputs, and update the manifest. Report test failures rather than
weakening expected results to match the implementation.

Before replay, verify source checksums and mapping/profile versions. Stage the
reconstructed candidate and compare it with the target receipt before activation.
Before restore, back up current state and verify the intended snapshot. Never
repair accepted history by editing it in place.

Rollback selects a previously published graph view with a recorded reason.
It does not reverse an authoritative engineering change. Report any difference
between source approval state and the graph's currently served publication.

## Proposed extraction assessment procedure

This procedure is not executed. [LIONG-007](LIONG-007-stack-and-architecture.md) owns the unselected LiteParse, LlamaParse, Firecrawl Parse, Docling/Granite-Docling-258M, PaddleOCR-VL-1.6, Qwen3-VL-8B-Instruct, and optional SAM3 candidates. Prefer simple pluggable adapters and retain the baseline. PPC services and model orchestration are not required. The scope remains extraction and review, not drawing authoring. The downstream forecasting/ML analytics exclusion does not exclude extraction models.

1. Close applicable technology, license, and dataset gates. Review SAM3's custom license specifically before adoption. Complete M5 isolation/access checks before any M6 held-out inference; M3 work uses visible development fixtures only.
2. Obtain separate authorization for third-party processing and spend before uploading documents or making paid calls. Apply [LIONG-009](LIONG-009-governance-and-operations.md#proposed-extraction-api-and-model-controls), including provider terms, secrets, caps, quotas, and disabled-route behavior.
3. At M6, freeze the licensed input set, held-out partition, parser truth and matching/scoring rules, prompts, versions/tiers, decoding, full-page/tile transforms, merge rules, and paired with/without-SAM3 configurations. Keep answer keys outside all extraction requests.
4. Record the CPU baseline, GPU, and hosted cohorts separately. Do not force the official CUDA-based SAM3 route into the no-GPU baseline or claim cross-cohort performance parity.
5. Execute only authorized SCN-002/009/010/015/016 subcases using the [evaluation protocol](LIONG-010-evaluation.md#proposed-extraction-candidate-comparison). Capture artifact and response hashes, parsing and topology results, review effort, and total measured cost.
6. Test bounded rate-limit recovery with stable input/request identities and recorded attempt outcomes. A disabled route hard-fails unless an explicit approved fallback is identified in the report.
7. Report repeated live inference separately from captured-response offline replay. Preserve raw candidates, review decisions, and existing publication authority. Record blocked or unexecuted comparisons rather than claiming success.

## Documentation package commands

The following utilities concern documents only:

```sh
uv run python scripts/bundle_docs.py
uv run python scripts/check_docs.py
uv run python scripts/bundle_docs.py --check
```

The bundle contains individual Markdown documents, the documentation utilities,
and a SHA-256 manifest. It excludes credentials, datasets, and its own output.
Running these commands does not validate DEXPI, execute engineering scenarios,
or deploy a service.

## Review checkpoints

First review the summary and proposed decisions in LIONG-000 and LIONG-REG-001.
Then review domain and temporal contracts before approving technology-dependent
schemas. Approve scenarios before implementation uses them as acceptance tests.

The first implementation request should name MILESTONE-001, its approved contracts,
and closed gates. This package supplies a build path but intentionally preserves
unresolved evidence requirements.
