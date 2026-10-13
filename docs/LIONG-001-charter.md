# LIONG-001: Project charter

Version: 0.1. Status: Draft for review.
Date: 2026-10-05.
Authority: business problem, objectives, scope, and exclusions.
Dependencies: [approved requirements](../REQUIREMENTS.md),
[decision register](LIONG-REG-001-decisions.md).

## Approval boundary

The business scope below carries forward user-approved decisions. This document's
organization and new proposals await document review. Permission to draft, commit,
and open a PR is not approval of all proposed designs or permission to deploy.
The [index](LIONG-000-index.md) identifies the authority for each subject.

## Problem

Lagos Integrated Oil and Gas Company (LIONG) is the reference organization for an
independent engineering drawing-to-graph project. Its demonstration facility is
set in Lekki, Lagos State, Nigeria. Public datasets and labeled synthetic examples
provide the evidence. The project does not claim access to actual LIONG facilities,
records, or internal systems.

Engineering information exists in backend databases, piping and instrumentation
diagrams (P&IDs), asset lists, instrument registers, and operational records. Their identifiers and
representations differ. A database row may describe a valve without identifying
its appearance on a drawing. A drawing may show connectivity that is not available
as queryable data. Optical character recognition can identify tag text while
assigning it to the wrong object.

Engineers therefore need more than digitized text. They need a connected model
that preserves engineering meaning and points back to the evidence for each object
and relationship. The model must distinguish missing information from a confirmed
absence of a connection.

A one-time conversion is insufficient. Approved revisions can rename tags, remove
equipment, or change connections. An incomplete update can create a misleading
state even when each imported row is individually valid. The graph must preserve
stable identities, publish validated revisions, and reconstruct what users saw
before a later correction.

## Outcomes

| ID | Intended outcome | Evidence of success |
| --- | --- | --- |
| OUT-001 | Query trustworthy engineering connectivity from structured and flat sources | Supported objects and relationships match known examples and resolve to source evidence |
| OUT-002 | Maintain the graph through approved changes without corrupting accepted history | Replays, rejected revisions, proposed states, and historical reconstruction behave as specified |
| OUT-003 | Support bounded engineering investigation with operational context | Users find asset-linked records, inspect candidate isolation boundaries, and export inputs with explicit gaps |

These are intended outcomes, not measured benefits. No reduction in engineering
effort, incident rate, or maintenance cost is claimed. The evaluation design must
measure extraction quality and review effort before asserting improvements.

## Scope

The structured ingestion path reads a representative engineering backend,
maps its supported content to DEXPI 2.0, validates it, and publishes a graph.
The flat-file path extracts information from P&ID files, validates and reviews it,
and feeds the same engineering model. DEXPI is not mandatory for flat-file input.

Both paths retain stable identity, provenance, drawing context, and revisions.
The graph connects equipment to work orders, document references, measurement
samples, and Management of Change records. Separate asset and instrumentation
registers provide cross-system checks.

The demonstration includes event-triggered processing, reconciliation, complete
revision publication, proposed-state review, and reconstruction of historical
published states. One shared graph represents connected domains.

The users are an engineering-data reviewer, a maintenance or process engineer,
and an engineering-change approver. A person may exercise both reviewer and
approver roles in the demonstration, with the role recorded for each action.
Neither role authorizes real-world isolation.

## Constraints and exclusions

Use open-source technology, with the exceptions and limits listed once, in
[REQUIREMENTS.md](../REQUIREMENTS.md#context).

The owner also permits assessment of proprietary document parsing and model APIs
alongside local tools. Provider choice, uploads, spending, and custom model licenses
require their own gates. Assessing an extraction model does not authorize a
downstream analytical application.

PPC is a reference for documentation and design patterns. LIONG has no automatic
dependency on PPC or its upstream EPM/ECE repositories. Its commercial models,
financial policies, provider arrangements, and model choices are not inherited.

The initial scope excludes P&ID authoring, live facility integration, operational control,
valve-operating procedures, declarations that equipment is safe to isolate,
calculation engines, downstream ML analytics, forecasting, and simulation. Inspection,
turnaround, process-flow, and procurement integrations remain extension points.
Financial and organizational graphs are outside the initial implementation.

Subgraph export prepares inputs and checks completeness. It does not prove a
relief calculation or process model is valid. Measurement examples are static or
replayed; live telemetry infrastructure is not required.

## Proposed demonstration boundary

Start with the small, cross-sheet engineering fixture in
[LIONG-006](LIONG-006-synthetic-data.md), then evaluate separately on suitable public
drawings. This is a proposed build boundary, not an approved production workload.
Do not inflate the demonstration by deploying every component named in PPC.

The default proposal is a locally runnable baseline. Optional hosted components
must pass the [technology gates](LIONG-007-stack-and-architecture.md).
There is no committed delivery date, production availability target, or capacity claim.

## Review checkpoint

Review OUT-001 through OUT-003, the proposed demonstration boundary, and any
differences from the original [problem statement](../PROBLEM_STATEMENT.md).
Detailed contracts and thresholds remain proposals in their owning documents.
Approval of this charter does not approve a later technology or safety-policy change.
