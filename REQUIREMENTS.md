# LIONG engineering drawing-to-graph requirements

Status: confirmed scope.
This document describes intended behavior, not implemented functionality.

## Context

Lagos Integrated Oil and Gas Company (LIONG) is the reference organization.
The demonstration facility is set in Lekki, Lagos State, Nigeria.
Use publicly available engineering data with suitable usage permissions.
Use clearly labeled synthetic data where public data is unavailable or insufficient.
Do not imply access to actual LIONG records or internal systems.
Use open-source technology, with capabilities verified before final selection.

User-approved exceptions to the open-source condition are Cloudflare services
and Databricks Free Edition. These exceptions permit assessment and selection;
they do not require either provider or authorize deployment or spending.
Verify current free-tier limits, terms, required features, and compatibility
before treating a proposed use as implementation-ready.

P&ID authoring is out of scope. The project consumes backend records and existing
or synthetic drawing files; it does not replace an engineering authoring suite.

Assess modern document parsers and vision-language models for flat-file extraction,
including open-source tools and proprietary parsing/model APIs. This permits
research and comparison design, not paid calls, model-license acceptance, deployment,
or third-party uploads. Named tools remain candidates until their fit and terms
are reviewed. Optional SAM 3 segmentation requires separate custom-license review.

LIONG is an independent project in this repository. PPC is a reference for
documentation practices, architecture patterns, and technology assessment,
not a parent application or a required runtime dependency. PPC changes do not
automatically change LIONG's approved requirements.

## Users

The primary user is an engineering-data reviewer who checks extracted objects
and connections, investigates conflicts, and accepts drawing-derived information
for publication, subject to the required validation gates.

The secondary user is a maintenance or process engineer who explores published
connectivity and candidate isolation boundaries.

Acceptance of extraction results is distinct from approval of an engineering
modification or authorization of isolation. Neither user role implicitly grants
those separate authorities.

A separate engineering-change approver role approves proposed engineering
modifications. Publication still requires validation after approval.
One person may exercise both reviewer and approver roles in the demonstration,
but each action records the role used. Neither role authorizes real-world isolation.
Detailed permission and approval workflows remain to be defined.

## Intended outcome

Build a maintained engineering foundation that supports both ingestion paths,
validated updates, tag consistency, source reconciliation, and historical states.
Include a small isolation-planning example to demonstrate the graph's value.

Demonstrate links to work orders, engineering documents, measurements through
an equipment bridge, and Management of Change records. Synthetic records are
acceptable where suitable public records are unavailable.

Demonstrate extraction of an analysis-ready subgraph and comparison of an
approved engineering state with a proposed state.

Document additional operational domains, including inspections, turnaround
schedules, process flows, and procurement history, as extension points.
Retain relief and flare calculations, process modeling, machine learning,
forecasting, and simulation as potential consumers. Their execution is deferred.
Financial and organizational graphs are outside the initial implementation.

The deferred machine-learning scope concerns downstream analytical applications.
It does not exclude assessed models used to extract or interpret drawing content.
Extraction model outputs remain candidates subject to evidence, validation, and review.

## Ingestion and source authority

The structured path is engineering backend database → DEXPI → graph.
The flat-file path is P&ID files → extraction and validation → shared
engineering model → graph. Both paths use common engineering definitions and
validation rules and feed a shared P&ID data product.

Each dataset declares its authoritative source. Where an approved backend
exists, it governs engineering objects and relationships. Drawing extraction
provides evidence and reports discrepancies without overwriting the backend.
For drawing-only datasets, reviewed extraction results form the accepted baseline.

DEXPI is mandatory for the backend path. Flat-file results may enter the
shared engineering model directly after validation and required review.
DEXPI export is available only for supported, sufficiently complete records,
with validation and explicit reporting of unsupported information.

Target a documented, tested subset of DEXPI 2.0 rather than claiming complete
coverage of the standard.

## Engineering fidelity and identity

The tested minimum includes equipment, valves, instruments, pipe segments,
connection points, tags, engineering attributes, drawing membership, and
cross-sheet references. Preserve flow direction only when the source establishes it.

Every supported object and relationship retains source identity and revision
provenance. Report unsupported source content rather than silently discarding it.

Engineering objects have stable identities independent of display tags.
Tags carry facility context and applicable revisions. Multiple drawing
appearances refer to the same object only when evidence supports the match.
Ambiguous matches require review.

## Change propagation and publication

A synthetic backend emits an event when an approved revision is committed.
The event triggers extraction, DEXPI generation, validation, and graph publication.
A submitted flat-file revision triggers extraction and review.
A full reconciliation operation detects changes missed by event processing.

Each declared source revision is a publication unit. Validate the complete
candidate update before publication. If validation fails, retain the last
accepted graph state and report the rejected revision and its errors.
Reprocessing a revision must not create duplicates.
Required human review is a publication gate for drawing-only inputs.

## Proposed states and history

A proposed state is based on a named approved revision and remains separate
from normal queries of approved information. Users can inspect its additions,
removals, and changed connections without altering the approved graph.
Promotion requires explicit approval recorded in the demonstration workflow.
Synthetic approval is not authorization to modify a real facility.

Retain source revisions, transformation versions, validation results,
publication records, and changes to objects and relationships. Reconstruct any
previously published state and explain differences between published revisions.
The storage design remains undecided.

## Management of Change

Each demonstrated engineering modification links to a synthetic Management
of Change record containing its reason, affected assets, proposed revision,
approval status, and approval history.

Technical ingestion logs remain separate and link to the change record.
An initial baseline import may exist without a change record.
Subsequent demonstrated engineering modifications require one.

## Cross-system validation

Validate engineering information against a separate asset hierarchy and
instrumentation register. Synthetic records are acceptable.
Check tag uniqueness within its defined context, object type, parent equipment
or functional location, and required attributes.

Each dataset declares mandatory checks. A failed mandatory check blocks
publication of the affected source revision. Missing optional context is a
reported gap. Matching must not silently invent or repair engineering relationships.

## Isolation-planning support

For selected equipment, inspect connected paths, branches, bypasses, and
candidate boundary valves within a declared analysis boundary. Results include
the graph revision and supporting source evidence.

Include bypass and incomplete-connectivity cases. Distinguish absence of a
path in the validated model from insufficient information to establish a path.
Do not recommend valve-operating sequences or declare equipment safe to isolate.
Valve suitability, operating conditions, and approved procedures remain outside
this demonstration.

## Connected domains

Use one shared graph for the demonstration with distinct domain objects and
relationships. Connect work orders, documents, measurements, and change records
to the engineering foundation through stable asset identities.

Define an explicit shared vocabulary and source-to-graph mappings. Distinguish
relationship meanings, such as a work order targeting equipment and a document
mentioning its tag. Do not treat all asset links as interchangeable.

Represent the graph-of-graphs concept through connected domains and queryable
domain-specific subgraphs. Separate graph databases and federation are not required.

## Operational demonstrations

For selected equipment, retrieve work orders and their recorded status, open
document references at the relevant page or drawing region, and display
associated measurement tags with example readings, units, and timestamps.
Trace engineering modifications to Management of Change records and approval history.

Include ambiguous asset matches and tag renaming. Ambiguous records remain
unresolved for review. Accepted links continue to identify the same equipment
after a tag change. Use static or replayed measurements; live telemetry
infrastructure is not required.

## Subgraph export

Export selected engineering objects and relationships with stable identifiers,
available attributes and units, source evidence, graph revision, and selection
criteria. Include a completeness report against the input requirements of one
named downstream analysis example.

Report missing physical parameters explicitly. The export demonstrates input
assembly and checking, not execution or validation of an engineering calculation.
Select the analysis example after examining available data and open-source tooling.

## Acceptance evidence

- Verify exact expected objects and relationships for documented synthetic
  structured-data cases through backend database, DEXPI, and graph.
- Verify equivalent engineering meaning from both ingestion paths where they
  describe the same test system.
- Test duplicate processing, missed-event reconciliation, rejected revisions,
  historical reconstruction, and separation of proposed and approved states.
- Test duplicate tags, ambiguous matches, bypasses, and incomplete connectivity.
- Retain traceable evidence for every published engineering object and relationship.
- Evaluate public drawings separately against independently checked annotations,
  reporting extraction errors and manual-review effort.

Report automatic extraction quality separately from results corrected through
review. Propose public-data accuracy targets after dataset inspection and
baseline measurement, rather than setting unsupported targets now.

## Research and implementation decisions deferred

- Select datasets and verify usage and redistribution permissions.
- Verify technology suitability, including support for the selected DEXPI subset.
- Select the downstream analysis example and define its required inputs.
- Establish public-data evaluation targets from dataset inspection and baseline results.
- Choose storage, event delivery, and interface designs during implementation planning.
