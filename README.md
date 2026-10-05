# Engineering drawing-to-graph

An open-source project to convert engineering backend records and flat piping
and instrumentation diagrams (P&IDs) into a maintained engineering knowledge graph.

Lagos Integrated Oil and Gas Company (LIONG) is the reference organization,
with a demonstration facility set in Lekki, Lagos State, Nigeria. The project
will use public and clearly labeled synthetic data, not internal LIONG records.

The structured path converts backend records into DEXPI before graph ingestion.
The flat-file path extracts engineering information from drawings, validates it,
and publishes reviewed results through the same engineering model.

## Documentation

- [Problem statement](PROBLEM_STATEMENT.md): the engineering problem, intended outcome, and scope.
- [Architecture](ARCHITECTURE.md): ingestion paths, source authority, graph domains, and change handling.
- [Requirements](REQUIREMENTS.md): confirmed behavior and acceptance evidence.
- [Glossary](GLOSSARY.md): project terminology.

## Project status

The scope is confirmed. This repository currently contains documentation, not
a working pipeline. Dataset selection, DEXPI compatibility checks, technology
evaluation, and implementation planning remain to be done.
