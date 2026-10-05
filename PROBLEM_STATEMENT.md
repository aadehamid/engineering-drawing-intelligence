# Problem statement

## Engineering information that can be queried and kept current

Lagos Integrated Oil and Gas Company (LIONG) is the reference organization for
an open-source engineering knowledge graph project. A demonstration facility
in Lekki, Lagos State, Nigeria, provides the setting. Public datasets and
clearly labeled synthetic examples will support the work; the project does
not assume access to LIONG's internal drawings or systems.

Piping and instrumentation diagrams (P&IDs) describe equipment, pipes, valves,
instruments, and their connections. Their engineering information exists both
as structured records in authoring databases and as flat files such as PDFs,
scans, and drawing exports. Engineers need to connect this information with
asset hierarchies, documents, maintenance records, and operational measurements.

These sources do not provide a consistent, directly queryable engineering model.
Database tables require mappings that preserve the meaning of their objects
and relationships. Flat drawings encode that meaning in text, symbols, lines,
and conventions. Recognizing a tag does not establish which equipment it
identifies. Detecting intersecting lines does not establish a pipe connection.

As a result, answering an engineering question can require tracing paths across
several sheets and reconciling records manually. A useful software
representation must preserve connection points, branches, bypasses, and
cross-sheet references. It must also show the evidence for each relationship
and distinguish a confirmed connection from an unresolved interpretation.

A one-time conversion leaves a second problem unsolved. Engineering changes
can make the graph diverge from its source. Tags may change, equipment may be
removed, and connections may be rerouted. Without stable identities and
controlled publication, updates can duplicate assets, lose operational links,
or expose an incomplete revision as accepted information.

## Intended outcome

The project will build a maintained engineering foundation through two paths:

- Extract structured records from an engineering backend database, transform
  them into a documented subset of DEXPI 2.0, and load validated information
  into the graph. DEXPI provides the engineering exchange model.
- Extract objects and relationships from flat P&ID files, validate their
  engineering meaning, and publish reviewed results through the same
  engineering model. DEXPI conversion is optional for this path.

Both paths will feed a shared P&ID data product with stable object identities,
source evidence, revision information, and validation status. Each dataset
will declare its authoritative source. Conflicting records and uncertain
extraction results will require resolution rather than silent merging.

The graph will retain accepted history while approved source changes trigger
validated updates. Failed revisions will leave the last accepted state
available. Proposed engineering states will remain separate from approved
information so users can inspect a change without treating it as installed.

Work orders, document references, measurement samples, and Management of Change
records will connect to the engineering objects they describe. These links
will retain their meaning when an asset's display tag changes.

## Demonstration and limits

Users will explore equipment connectivity, inspect candidate isolation
boundaries, compare revisions, and retrieve the source evidence behind results.
The isolation example will include a bypass and incomplete connectivity. It
will not prescribe operating sequences or declare equipment safe to isolate.

The project will also export a selected engineering subgraph and report
whether it contains the inputs required by a named downstream analysis.
Missing physical parameters will be explicit. Preparing those inputs does
not implement relief or flare calculations, process simulation, forecasting,
or machine-learning execution.

Known synthetic cases will test engineering fidelity, identity, change
handling, and historical reconstruction. Public drawings will be evaluated
separately against independently checked annotations. Results will distinguish
automatic extraction quality from quality achieved through manual review.

Success means that users can query engineering relationships, verify the
answers against their sources, and reproduce the published state behind an
answer. The [requirements](REQUIREMENTS.md) define the acceptance evidence;
the [architecture](ARCHITECTURE.md) describes the proposed system boundaries.
