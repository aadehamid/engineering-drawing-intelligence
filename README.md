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

- [Review package and reading order](docs/LIONG-000-index.md): eleven draft documents, decisions, references, and implementation gates.
- [Download the complete Markdown package](docs/releases/LIONG-review-package-v0.1.zip): individual files with a SHA-256 manifest.

The original approved baseline remains available:

- [Problem statement](PROBLEM_STATEMENT.md): the engineering problem, intended outcome, and scope.
- [Architecture](ARCHITECTURE.md): ingestion paths, source authority, graph domains, and change handling.
- [Requirements](REQUIREMENTS.md): confirmed behavior and acceptance evidence.
- [Glossary](GLOSSARY.md): project terminology.

## Project status

The scope is confirmed. The expanded version 0.1 package is a draft for review;
new technical proposals are not automatically approved. On 2026-11-26 this
repository was renamed from `aadehamid/Engineering_Drawing_to_Graph` to
`aadehamid/engineering-drawing-intelligence`. LIONG remains independent of PPC,
which is a documentation and architecture reference. PPC reconciled its baseline
on 2026-11-26 (`ADR-0040` through `ADR-0056`), replacing DuckLake, Kafka,
Jena/Fuseki, and Cloudflare D1 with Delta Lake on R2, NATS JetStream with a
transactional outbox, Git Turtle with `pyshacl` projected to Neo4j Community,
and PostgreSQL workflow state; see
[LIONG-007](docs/LIONG-007-stack-and-architecture.md#2026-11-26-ppc-baseline-update).

This repository contains documentation and documentation-checking utilities, not
a working engineering pipeline. Public-source research and a PPC stack assessment
are recorded in the package. Dataset admission, DEXPI interoperability, component locks
and deployment are implementation gates;
[the decision register](docs/LIONG-REG-001-decisions.md#open-questions-and-package-level-gates) holds each one's state.

Cloudflare services and Databricks Free Edition are permitted exceptions to the
open-source condition. Their use is optional and requires verified fit and separate
authorization before provisioning or spending. SQL Server, hosted on an Azure SQL
Database free-offer database, is a further exception: both synthetic vendor-style
backends run on it (DEC-027).

The [drawing extraction assessment](docs/LIONG-007-stack-and-architecture.md#modern-drawing-extraction-candidates)
covers LiteParse, LlamaParse, Firecrawl Parse, document and vision-language models
on Hugging Face, and optional SAM 3 segmentation. These are candidates, not selected
dependencies. Proprietary API assessment does not authorize uploads or paid calls;
SAM 3 also requires custom-license review. P&ID authoring remains out of scope.

## Check and rebuild the documentation package

Requires Python 3.12 and `uv`, which installs the locked dependencies in `uv.lock`,
including the CommonMark parser the checks use.

```sh
uv run python scripts/bundle_docs.py
uv run python scripts/check_docs.py
uv run python scripts/test_doc_tools.py
uv run python scripts/bundle_docs.py --check
```

Build the archive first when working from an extracted copy. The archive does
not contain another copy of itself.

These checks validate documentation and archive integrity. They do not execute
engineering acceptance scenarios or establish standards compliance.
