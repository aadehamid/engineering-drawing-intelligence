# LIONG-REF-001 Reference register

| Document control | Value |
| --- | --- |
| Status | Draft for review |
| Version | 0.1 |
| Inspection date | 2026-10-05 UTC |
| Dependencies | [LIONG-001 charter](LIONG-001-charter.md), [LIONG-002 users and requirements](LIONG-002-users-and-requirements.md) |
| Authority | Consolidated evidence register for sources, ontology mappings, and technology assessment |
| Vocabulary authority | [GLOSSARY.md](../GLOSSARY.md) |

## Scope and evidence rules

All entries were accessed on 2026-10-05 UTC unless stated otherwise. Public HTTP requests inspected publisher pages, raw artifacts, and repository metadata. No paid-credit API, private-code submission, deployment, or implementation was used.

An inspected source supports only the claims listed in its entry. A live URL is not an immutable release pin. A license observation is not clearance of every file or imported dependency. All proposed reuse remains pending review under LIONG-003. Record adoption decisions in [LIONG-REG-001](LIONG-REG-001-decisions.md).

Local baseline documents read were [REQUIREMENTS.md](../REQUIREMENTS.md), [GLOSSARY.md](../GLOSSARY.md), [PROBLEM_STATEMENT.md](../PROBLEM_STATEMENT.md), and [ARCHITECTURE.md](../ARCHITECTURE.md). These govern LIONG scope; external sources do not amend them.

The package index resolves related documents. Their inclusion does not approve their proposals.

## REF-PPC-001: PPC documentation reference

- Source: [pinned repository](https://github.com/aadehamid/pearland-petroleum-corporation/tree/01027a84be5d453cbb4e2ea091e4884729918b15).
- Version inspected: commit `01027a84be5d453cbb4e2ea091e4884729918b15`.
- Paths inspected: recursive repository tree and [`docs/PPC-019_Public_Ontology_Reuse_and_Implementation_Guide.md`](https://github.com/aadehamid/pearland-petroleum-corporation/blob/01027a84be5d453cbb4e2ea091e4884729918b15/docs/PPC-019_Public_Ontology_Reuse_and_Implementation_Guide.md).
- Supported claims: PPC-019 version 0.1 calls its recommendations proposed and states that no ontology adoption is asserted. Implementation areas, including `semantic/ontology`, `semantic/mappings`, `schemas`, and `tests`, contain `.gitkeep` placeholders.
- Reuse/license status: reference for documentation patterns only. No license file found in the inspected tree. No copied prose, ontology files, or code authorized by this assessment.
- Unresolved gates: permission before copying any material; independent LIONG approval before adopting a pattern. PPC's EPM/ECE dependency and authority structure do not apply automatically.

## Standards, vocabularies, and compatibility references

### REF-STD-001: DEXPI specification and native XML

- Source: [official specifications](https://dexpi.org/specifications/), [2.0 HTML](https://dexpi.org/specification/2.0/html/), and [DEXPI XML definitions](https://dexpi.org/specification/2.0/html/basics/metamodel_and_exchange_format.html).
- Version inspected: 2.0 HTML identifies release 2.0.0 dated 2025-10-10. Landing page inspected live on the access date.
- Artifact inspected: [`_static/DEXPI_XML_Schema.xsd`](https://dexpi.org/specification/2.0/html/_static/DEXPI_XML_Schema.xsd). SHA-256 `0bd6568b7c52fd59ac4ef6d8547ab2b2aa890c009a3a1bfbc5d7cc18c53b36e6`. Its schema `version` is `1.0.0`; the linking page calls the download `DEXPI_XML_Schema_RC_1.xsd`.
- Supported claims: 2.0 uses DEXPI XML for models and instances, without requiring Proteus XML schema. The root is `Model`. File-local IDs and imported name references have distinct syntax. Model classes and properties require more than generic XML parsing.
- Additional observation: the landing page recommends 2.0.1 as a fix release replacing 2.0 and links [2.0.1 HTML](https://dexpi.org/specification/2.0.1/html/). The linked 2.0.1 artifacts were not inspected on that date; the 2026-10-14 point below records them.
- 2.0.1 observations, accessed 2026-10-13: the [release announcement](https://dexpi.org/dexpi-2-0-1-specification-published-the-update-replacing-dexpi-2-0/) dates 2.0.1 to 2026-09-30 and calls it the update replacing 2.0. It says 2.0.1 fixes a small number of issues in the Plant model and improves the Process model. The [specification repository](https://gitlab.com/dexpi/Specification) has a V2.0.1 tag holding the XSD and a 2.0.1 reference P&ID. The specification defines DEXPI XML as its exchange encoding; no other encoding was found. No official 2.0 validator was found. LIONG targets 2.0.1 ([DEC-061](decisions/DEC-061-dexpi-2-0-1.md)); its pinned artifacts are listed in the next point.
- 2.0.1 pins, retrieved 2026-10-14 ([DEC-074](decisions/DEC-074-dexpi-2-0-1-pinned-files.md)): the V2.0.1 tag is commit `eef0f0c6e8edfe84582e7a45d109c396bdc544f8`. From the tag, `DEXPI_XML_Schema.xsd` (SHA-256 `0bd6568b7c52fd59ac4ef6d8547ab2b2aa890c009a3a1bfbc5d7cc18c53b36e6`, the same bytes as the 2.0.0 download) and `reference_pid.xml` (`acd39c74292aef3f6f00581fc78b05814acf2318815abd28c14ebefba12fdd94`). The tag holds the models only as source for `dexpi.specificator`. From the [published 2.0.1 specification](https://dexpi.org/specification/2.0.1/html/)'s `_static` folder, `Core.xml` (`7136f8440c08c8bf7759c4e9eb614b046cc3196f2f45695122629a2020e61e4a`) and `Plant.xml` (`0a5175535c1263464fee653c7b99f38eb810c15824f84155748eac165f50edbf`). Building the tag's source with `dexpi.specificator` 1.0.1 (PyPI, MIT, wheel SHA-256 `410be144920a8039a6da4b71263755e184466a27fd9a2a00d8c1a1d7835de67c`) gave byte-identical `Core.xml`, `Plant.xml` and `Process.xml`. All three models import `MetaData.xml`, which DEXPI does not publish; the tool defines it in code. The 2.0.1 site states CC BY 4.0 for the specification. The copies are in `standards/dexpi/2.0.1` with their manifest.
- Reuse/license status: 2.0 specification explicitly states [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Confirm scope for separately packaged downloads and preserve attribution and modification notices.
- Unresolved gates: reconcile schema label versus artifact name; test syntax, schema, semantic rules, and engineering fidelity separately. No conformance test was run. Settled: the exact release is 2.0.1 ([DEC-061](decisions/DEC-061-dexpi-2-0-1.md)), and its imported models are pinned with their hashes, except `MetaData.xml`, which DEXPI does not publish ([DEC-074](decisions/DEC-074-dexpi-2-0-1-pinned-files.md)).

### REF-STD-002: QUDT

- Source: [official schema](https://qudt.org/schema/qudt/), fetched as RDF text.
- Version inspected: live schema labels itself `QUDT Schema - Version 3.5.2`. Its `owl:versionIRI` is the unversioned `http://qudt.org/schema/qudt`, so the response is not an immutable pin.
- Supported claims: `qudt:Unit` defines the scale used to measure quantities; schema includes quantity, unit, dimensional, and conversion concepts. The inspected `qudt:QuantityValue` description is minimal and does not establish a complete mapping.
- Reuse/license status: embedded rights metadata states CC BY 4.0, with attribution to QUDT.org. Separate embedded metadata identifies UCUM-derived material and its license conditions.
- Unresolved gates: select immutable schema and unit/quantity vocabulary releases; inspect selected unit definitions, dependency licenses, and UCUM conditions; specify gauge/absolute and reference-condition semantics. No blanket unit equivalence or conversion correctness claim is made.

### REF-STD-003: PROV-O

- Source/version: [W3C Recommendation, 2013-04-30](https://www.w3.org/TR/2013/REC-prov-o-20130430/), especially sections 3.1 and 4.
- Supported claims: PROV-O defines entities, activities, agents, and derivation/usage relationships. It supports bounded provenance mappings, not LIONG publication or approval policy.
- Reuse/license status: specification carries W3C copyright and document-use rules. It is publicly readable; no copy of the ontology is included in this task.
- Unresolved gates: pin the OWL artifact, inspect its exact license and imports, and check the selected terms' restrictions. Historical reconstruction remains a local design obligation.

### REF-STD-004: SOSA/SSN

- Source/version: [W3C/OGC Recommendation, 2017-10-19](https://www.w3.org/TR/2017/REC-vocab-ssn-20171019/), especially observation, feature-of-interest, phenomenon-time, and result-time definitions.
- Additional artifact: live [SOSA namespace RDF](https://www.w3.org/ns/sosa/), inspected for license declarations, not pinned as the 2017 serialization.
- Supported claims: an observation is an act of estimating or calculating a property's value. Its result, feature of interest, and times are distinct. These support a candidate measurement model through the equipment bridge.
- Reuse/license status: recommendation has W3C/OGC document notices. Live RDF lists `http://www.w3.org/Consortium/Legal/2015/copyright-software-and-document` and `http://www.opengeospatial.org/ogc/Software`.
- Access note: the fetch tool rejected the large recommendation response; direct public HTTP retrieval supplied the relevant definitions.
- Unresolved gates: freeze the desired recommendation and matching RDF artifacts; inspect dependency closure and notices; choose a bounded subset rather than importing all SSN axioms.

### REF-STD-005: Web Annotation Data Model

- Source/version: [W3C Recommendation, 2017-02-23](https://www.w3.org/TR/2017/REC-annotation-model-20170223/).
- Supported claims: annotations relate bodies and targets. Selectors can address resource segments, but supported selector/media combinations vary. This supports an evidence-locator pattern, not inferred engineering connectivity.
- Reuse/license status: W3C document-use notice. The [2015 W3C document license](https://www.w3.org/Consortium/Legal/2015/doc-license) was also inspected. It distinguishes document copying, limited implementation-oriented derivatives, and code components.
- Unresolved gates: inspect the exact vocabulary and JSON-LD context licenses if redistributed. Define immutable artifact IDs, page addressing, coordinate frames, rasterization, rotation, and crop transforms locally.

### REF-STD-006: IOF Core and Maintenance

- Source/version: [IOF release browser 202603](https://spec.industrialontologies.org/portal/release/202603/) and [maintenance work order record](https://spec.industrialontologies.org/portal/release/202603/maintenance/MaintenanceWorkOrderRecord.html).
- Supported claims: the portal uses BFO-based industrial concepts. The inspected term IRI is `https://spec.industrialontologies.org/ontology/construct/MaintenanceWorkOrderRecord`, defined in `https://spec.industrialontologies.org/ontology/maintenance/Maintenance/`.
- Definition evidence: the term describes a maintenance process and is input to such a process. The page calls its definition provisional because purely supporting maintenance activities do not satisfy it.
- Reuse/license status: portal and inspected term page state MIT. Exact RDF/OWL artifacts and imported BFO/Core dependency licenses were not inspected.
- Unresolved gates: evaluate foundation compatibility, term maturity, imports, and work-order mismatch before any subclass or equivalence assertion. Proposal is limited reference/mapping assessment, not foundational adoption.

### REF-STD-007: IDO/POSC Caesar

- Source attempted: [POSC Caesar reference data service](https://rds.posccaesar.org/) and [`ontology/lis14/ont/core`](https://rds.posccaesar.org/ontology/lis14/ont/core).
- Version inspected: none. Both public requests returned HTTP 403.
- Supported claims: this entry records a candidate and the access failure only. The PPC shortlist identifies IDO/POSC Caesar as an industrial asset/property reference, but this inspection did not independently verify term definitions.
- Reuse/license status: unverified. Public reference data access would not establish reuse rights for ISO publications or every related ontology.
- Unresolved gates: obtain a primary accessible artifact, release/version IRI, license, definitions, and imports. Do not implement an IDO mapping from this entry.

### REF-STD-008: pyDEXPI compatibility

- Source/version: [`README.md`](https://github.com/process-intelligence-research/pyDEXPI/blob/83e5a11c4af3635ad12290a4dbe310480eb6d7a3/README.md) and [`LICENSE`](https://github.com/process-intelligence-research/pyDEXPI/blob/83e5a11c4af3635ad12290a4dbe310480eb6d7a3/LICENSE), inspected on `master` at `83e5a11c4af3635ad12290a4dbe310480eb6d7a3`.
- Supported claims: README explicitly supports DEXPI 1.3 and describes loading Proteus XML through `ProteusSerializer`. Its conversion and graph utilities are candidate legacy tooling, not proof of DEXPI 2.0 support.
- Reuse/license status: AGPL version 3 or later, as stated in the license's program notice. No software copied or executed.
- Unresolved gates: assess copyleft obligations for intended use and any bundled data separately; verify exact input/output formats and fidelity. No native 2.0 reader/writer claim is supported.
- Access note: an initial `main` URL returned 404; repository metadata identified `master`.
- 2.0 support, accessed 2026-10-13: the latest release, v1.2.0 (2026-04-14), still supports DEXPI 1.3. In [issue 6](https://github.com/process-intelligence-research/pyDEXPI/issues/6), on 2.0 support, the maintainer wrote on 2026-07-28 that it would come in the upcoming months, with no date.

### REF-STD-009: DEXPI GraphicBuilder

- Source/version: [GitHub README](https://github.com/DEXPI/GraphicBuilder/blob/dbbca4555f9438bbef851d62851dd7e7f07a0911/README.md), `master` at `dbbca4555f9438bbef851d62851dd7e7f07a0911`.
- Supported claims: deprecated GitHub repository points to [GitLab GraphicBuilder](https://gitlab.com/dexpi/GraphicBuilder).
- Reuse/license status: current GitLab code and license unverified.
- Unresolved gates: inspect current release, accepted encoding, renderer fidelity, and license before use. No native DEXPI 2.0 compatibility claim is made.

### REF-STD-010: bpmn2dexpi

- Source/version: [GitHub repository](https://github.com/skhella/bpmn2dexpi), README on `main` at `f198a5b0b5ee90a829895b728beebd8c05903c03`, inspected 2026-10-13.
- Supported claims: README states that `--validate` checks existing DEXPI 2.0 Process and Plant files against the XSD and five information-model checks: property names and kinds, data types, reference targets, cardinality, and class existence. It ships DEXPI 2.0 copies of `Core.xml`, `Plant.xml` and `Process.xml`. It targets 2.0, not 2.0.1. It runs on Node.js.
- Reuse/license status: README states MIT. No software copied or executed.
- Unresolved gates: 2.0.1 support. Kept out of the slice ([DEC-069](decisions/DEC-069-bpmn2dexpi-recorded-not-used.md)).

### REF-STD-011: Brick

- Source/version: [brickschema.org](https://brickschema.org/), [GitHub releases](https://github.com/BrickSchema/Brick/releases), and [repository](https://github.com/BrickSchema/Brick), inspected 2026-11-08 UTC.
- Version inspected: v1.5.0, released 2026-10-29 by gtfierro, tagged at commit `3fdb57060a520d333910eb3902eb02ac25c5cf86` (also the current nightly tip). A nightly build 2026-11-07 continued from the same commit.
- Inspected paths: the site's introduction page; the v1.5.0 release notes; the tagged tree's README (`README.md` calls Brick an open-source, BSD-licensed development effort), `LICENSE` (BSD-3-Clause, copyright "Brick Consortium, Inc. 2016-2026"), tree listing, and `bricksrc/`; the ontology's releases history from v1.4.0 to v1.5.0. The repository generates the ontology serializations with `generate_brick.py`; the tree inspected carries no generated `Brick.ttl`.
- Model observed from the release notes and history: Brick describes building assets as `brick:Equipment`, `brick:Location`, and `brick:Point` entities, linked by relationships such as `hasPoint`/`isPointOf`, `hasLocation`/`isLocationOf`, `hasPart`/`isPartOf`, and `isFedBy`. Since v1.4.0 relationships use SHACL property shapes instead of RDFS domain/range. Point entity properties resolve quantities through QUDT quantity kinds: v1.4.4 deprecated home-grown Brick quantity classes in favor of `qudt:` quantity kinds, and v1.4.2 to v1.5.0 update them (v1.5.0 moved to QUDT 3.3.0). v1.4.0 began phasing Brick location classes out in favor of RealEstateCore (REC); v1.5.0 makes Brick collection classes subclasses of `rec:Collection` and adds controllers with `controls`/`isControlledBy` and `hosts`/`isHostedBy` relationships, plus SHACL shapes for plant composition via `rec:includes`; it removes `brick:connectedTo` and aligns lighting classes with the REC working group.
- Supported claims: an actively maintained metadata schema (releases in October 2026) for building physical, logical, and virtual assets, with equipment, point, and location entities linked by relationships such as `hasPoint`/`isPointOf`, `hasLocation`/`isLocationOf`, `hasPart`/`isPartOf`, and `isFedBy`; relationships validated by SHACL property shapes since v1.4.0; point quantities resolved through QUDT quantity kinds (v1.4.4 deprecated Brick's own quantity classes for QUDT ones; v1.5.0 depends on QUDT 3.3.0). A point attaches to equipment, carries a quantity kind, and sits at a location, with sensors, setpoints, alarms, and commands as point subclasses. LIONG reading, not a register position: this model is precedent for the instrument-point pattern the SOSA/SSN entry (REF-STD-004) calls a candidate measurement model through the equipment bridge, and a bounded Brick-based mapping is a candidate to try against W-SP's LT and PI records.
- Reuse/license status: the repository is BSD-3-Clause (Brick Consortium, Inc.); the README describes the whole effort as BSD-licensed. No ontology serialization was copied or vendored in this task.
- Unresolved gates: Brick's domain is building automation (HVAC, lighting, fire, security), not process plants; it has no classes for LIONG's process equipment, nozzles, pipe runs, or P&ID instrument loops, so its classes cannot be the published graph's core vocabulary. Any use is a bounded mapping bridge for instrument-point semantics, pending an owner decision record. Gates before any reuse: pin and hash the generated v1.5.0 serialization; confirm the serialization's own license and attribution strings (the deprecation tables name REC at `w3id.org/rec` and BACnet at `data.ashrae.org/bacnet/`, so any vendored file imports those dependencies and their licenses); choose the bounded subset; test a mapping against W-SP's LT and PI records ([DEC-086](decisions/DEC-086-sps-dexpi-mapping.md)) before asserting one. Recorded as a candidate for the owner's review, not an adoption.

## Data references

### REF-DATA-001: DEXPI 2.0 reference P&ID

- Source/version: [official 2.0 appendix](https://dexpi.org/specification/2.0/html/appendix/reference_pid.html), [XML](https://dexpi.org/specification/2.0/html/_static/reference_pid.xml), and linked [SVG](https://dexpi.org/specification/2.0/html/_images/reference_pid.svg).
- Artifact inspected: XML SHA-256 `f068ad94a18dd089afa3fc224d92056b08ee0059bd06686c68190c0b789ae2b1`. Its root is `Model`, with name `example` and URI `http://www.example.org`.
- Supported claims: XML uses Core and Plant imports under `/models/2.0.0/` and contains a `Core/EngineeringModel`. The appendix presents it as an illustration of the Plant model. The SVG link was inspected, not its visual content.
- Reuse/license status: governing specification page states CC BY 4.0. No independent per-download license notice was established for XML/SVG. Confirm coverage and attribution before redistribution.
- Access failure: `https://data.dexpi.org/models/2.0.0/Core.xml` and `https://data.dexpi.org/models/2.0.0/Plant.xml` failed TLS certificate hostname verification. Verification was not disabled. On 2026-10-13 `data.dexpi.org` did not respond. [DEC-062](decisions/DEC-062-vendored-model-files.md) has LIONG keep pinned copies of the model files instead. On 2026-10-14 `data.dexpi.org` served a certificate for `my.exacon.cloud`. The 2.0.1 copies are pinned in `standards/dexpi/2.0.1` ([DEC-074](decisions/DEC-074-dexpi-2-0-1-pinned-files.md)).
- Unresolved gates: acquire authentic imported artifacts through a trusted source; check complete dependency closure, SVG content, notices, and engineering completeness. XML well-formedness was checked, not XSD or semantic conformance.

### REF-DATA-002: DEXPI TrainingTestCases

- Source/version: [GitLab repository](https://gitlab.com/dexpi/TrainingTestCases), inspected `master` at `a23d61e2e089eb2ca464cd552f9ae580a2785963`.
- License evidence: [`LICENSE` at the pin](https://gitlab.com/dexpi/TrainingTestCases/-/blob/a23d61e2e089eb2ca464cd552f9ae580a2785963/LICENSE), retrieved through the public GitLab repository-files API, contains CC BY 4.0.
- Inspected paths: root tree, `dexpi 1.3/example pids`, and `dexpi 1.3/example pids/C01 DEXPI Reference P&ID`. C01 contains `C01V04-VER.EX01.xml`, `.svg`, `.html`, and `C01V04.pptx`. The XML was fetched at the pin and parsed; its root is `PlantModel`.
- Supported claims: repository separates DEXPI 1.2 and 1.3; example directories include equipment/nozzles, control, off-page connection, and intersection cases. File content and correctness were not audited across the collection.
- Reuse/license status: concrete CC BY 4.0 repository license supports reuse assessment beyond mere public access. Retain source attribution, license link, and change notices; inspect selected artifacts for exclusions or third-party rights.
- Migration evidence: [old GitHub TestCases README](https://github.com/DEXPI/TestCases/blob/09e9eddcb9da510ca6c103a01816b2629e903745/README.md) redirects to GitLab. Initial guessed GitHub `DEXPI/TrainingTestCases` returned 404; this is not evidence that the dataset is unavailable.
- Unresolved gates: choose and hash files, assess drawing quality and ground truth, confirm notices, and define explicit legacy-to-2.0 conversion tests. Do not report legacy input coverage as native 2.0 coverage.

### REF-DATA-003: proposed LIONG synthetic corpus

- Source/version: future project-authored artifacts under [LIONG-006](LIONG-006-synthetic-data.md); no release or files exist from this task.
- Supported claims: approved requirements permit clearly labeled synthetic data and require known structured cases. This entry proposes a provenance category, not a completed dataset.
- Reuse/license status: pending original creation and repository licensing decision. Reused symbols, templates, or public drawings retain applicable source obligations.
- Unresolved gates: specify generation rules, authorship, expected graphs, seeded revisions, attribution, review evidence, and public-versus-synthetic evaluation separation.

## Technology references

These entries consolidate the technology inspection in
[LIONG-007](LIONG-007-stack-and-architecture.md#version-and-source-evidence).
Access date: 2026-10-05 UTC. Candidate versions are not dependency locks.
Provider documentation is rolling and must be rechecked before use.

| ID | Primary source and inspected state | Supported claim and remaining gate |
| --- | --- | --- |
| REF-TECH-001 | [PPC technology baseline at the pinned commit](https://github.com/aadehamid/pearland-petroleum-corporation/blob/01027a84be5d453cbb4e2ea091e4884729918b15/docs/PPC-002_Enterprise_Architecture_and_Technology_Stack.md) | Documented responsibilities, not runnable components; same repository evidence as REF-PPC-001 |
| REF-TECH-002 | PostgreSQL [version policy](https://www.postgresql.org/support/versioning/) and [license](https://www.postgresql.org/about/licence/); 18.6 observed | PostgreSQL License and supported release information; server/driver/image and recovery compatibility remain unlocked |
| REF-TECH-003 | Neo4j [edition documentation](https://neo4j.com/docs/operations-manual/current/introduction/), [licensing](https://neo4j.com/licensing/), [2026.09.0 license](https://github.com/neo4j/neo4j/blob/2026.09.0/LICENSE.txt) | Community GPLv3; edition-specific constraints, driver/runtime, backup, packaging obligations, and snapshot behavior require verification |
| REF-TECH-004 | Dagster [OSS deployment](https://docs.dagster.io/deployment/oss), [1.13.25 release](https://github.com/dagster-io/dagster/releases/tag/1.13.25), [tagged license](https://github.com/dagster-io/dagster/blob/1.13.25/LICENSE) | Apache-2.0; optional orchestration, not yet selected or integrated |
| REF-TECH-005 | Cloudflare [R2 pricing](https://developers.cloudflare.com/r2/pricing/), rolling page | Tier-specific allowances and operations pricing; free allowance is not a spending cap, retention policy, or authorization |
| REF-TECH-006 | Databricks [Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition) and [limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations), rolling pages | Edition limits and usage conditions; numeric account quota, runtime, persistence, and required connectivity remain unverified |
| REF-TECH-007 | Databricks [general connection documentation](https://docs.databricks.com/aws/en/connect/), rolling page | General platform capability only; does not certify R2/S3 connectivity in Free Edition |
| REF-TECH-018 | lxml [6.1.3 on PyPI](https://pypi.org/project/lxml/6.1.3/) and its [license](https://github.com/lxml/lxml/blob/lxml-6.1.3/LICENSE.txt), inspected 2026-10-14 | BSD-3-Clause, released 2026-09-02; pinned for the DEXPI scripts (DEC-067). The bundled libxml2 and libxslt versions are not recorded |

Referenced software/service names do not waive licensing or provider terms.
No third-party packages, specifications, or example datasets are redistributed
in this documentation archive. New LIONG code/data licensing remains an owner decision.

## Vendor storage references

REF-TECH-015 to REF-TECH-017 support the Plant 3D-style backend in
`schemas/plant3d-style.sql` ([DEC-040](decisions/DEC-040-plant-3d-patterns.md),
[DEC-049](decisions/DEC-049-plant-3d-schema-choices.md)), accessed 2026-10-13 UTC.
REF-TECH-019 to REF-TECH-029 support the SmartPlant-style backend
in `schemas/smartplant-style.sql` ([DEC-081](decisions/DEC-081-smartplant-style-patterns.md),
[DEC-082](decisions/DEC-082-smartplant-style-schema-choices.md)), accessed 2026-10-19 UTC;
Hexagon's pages were read through its documentation site's public search.
They describe how the products store saved data; the backend copies the patterns
under its own names and copies no vendor schema.

| ID | Primary source and inspected state | Supported claim and remaining gate |
| --- | --- | --- |
| REF-TECH-015 | Autodesk support article [Understanding PnPDatabase structure using DCF files in AutoCAD Plant 3D](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Understanding-PnPDatabase-structure-using-DCF-files-in-AutoCAD-Plant-3D.html), rolling page | The Plant 3D and P&ID project database stores project data, object properties and relationships. Table-level detail comes from REF-TECH-016. |
| REF-TECH-016 | Carsten Beinecke, [AutoCAD P&ID and AutoCAD Plant 3D: Hidden Treasures in Your Databases](https://static.au-uw2-prd.autodesk.com/handout_5740_PD5740.pdf), Autodesk University handout PD5740, version 1.0; SHA-256 `7900432bb4cdbf196178dad0e91341e22aa19fb4590f20cb796a20874c117701` | A project database can be SQLite or SQL Server. Each class has its own table; system tables start with PnP, including PnPBase (PnPID, PnPClassName, PnPStatus, PnPGuid, PnPTimestamp), PnPDataLinks and PnPColumnAttributes. Relationship tables include LineStartAsset and LineEndAsset (Line, Asset), ConnectorsRelationship (Connector1, Connector2), LineOffPageConnector and AssetOwnership. Equipment rows carry Tag, Type and Number. The column lists come from the handout's screenshots; the product's current release was not inspected. |
| REF-TECH-017 | Autodesk Plant 3D Help, [To set up a tag format](https://help.autodesk.com/view/PLNT3D/2017/ENU/?caas=caas/CloudHelp/cloudhelp/2017/ENU/Plant3D-UserGuide/files/project-create-tags-wrkflw-htm.html), 2017 user guide | A class's tag format is built from subparts, for example "Equipment Tag [Type-Number]". Later releases were not compared. |
| REF-TECH-019 | Hexagon, Data Dictionary Manager Help, version 13 Update 8, published 2026-09-23: item-type topics [Representation](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211243), [ModelItem](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211169), [PlantItem](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/847697), [Pipe Run](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211204), [Connector](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/847686), [InlineComp](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211078), [PipingComp](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211208), [PipingPoint](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/878916), [OPC](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211186) and [Revision](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211249); property topics [PipingPointNumber](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211215), [FlowDirection](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/847696), [MatingOPCPath](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211163), [ItemStatus](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211130), [ItemTag](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211131), [TagPrefix](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211315), [TagSequenceNo](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211317) and [TagSuffix](https://docs.hexagonppm.com/r/en-US/Data-Dictionary-Manager-Help/13/211318). Each claim is read from its topic's own content. | Model item is the superclass for all but the most ancillary physical components, and a representation is associated with a drawing. A plant item is derived from model item. A pipe run is "a contiguous set of connectors and components having the same set of properties". A connector has End 1 and End 2, and placing an inline component deletes it and replaces it with two connectors. A pipe run's flow direction is set relative to its connectors' geometry. An inline-component item ties a piping component to its run. Piping points are numbered. An off-page connector may be associated with one other, on the drawing that holds the continuation. When different symbols are used for each connector of a pair, the mating property holds a path to the mating symbol. A status property says whether an item is active or deleted. Tag prefix, sequence number and suffix are properties beside the item tag. A revision relates many-to-one to a drawing, with major and minor numbers, a date, and creation, checked and approval information. Column lists per table are not given. |
| REF-TECH-020 | Hexagon, [Clean Data Utility](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Utilities-Help/10/1418601), Smart P&ID Utilities Help, version 10 | The utility deletes model items with no representation, repairs off-page connectors that lost their mate's identity, and reports broken relationships. |
| REF-TECH-021 | Hexagon, [Constraint utilities](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-Engineering-Manager-Installation-and-Upgrade/On-premises/13/161338), Smart Engineering Manager Installation and Upgrade, version 13 | A nozzle repair sets the nozzle's stockpile flag, or its parent equipment key, from the drawing. Another check finds off-page connectors whose partner does not exist. |
| REF-TECH-022 | Hexagon, SmartPlant Enterprise Adapter for Smart P&ID, version 12 Update 7, published 2026-10-07: [Pipelines](https://docs.hexagonppm.com/r/en-US/Intergraph-SmartPlant-Enterprise-Adapter-for-Smart-P-ID/12/293405), [Pipeline Key Attributes](https://docs.hexagonppm.com/r/en-US/Intergraph-SmartPlant-Enterprise-Adapter-for-Smart-P-ID/12/293406), [Publishing Pipelines](https://docs.hexagonppm.com/r/en-US/Intergraph-SmartPlant-Enterprise-Adapter-for-Smart-P-ID/12/293407) and [Special Cases](https://docs.hexagonppm.com/r/en-US/Intergraph-SmartPlant-Enterprise-Adapter-for-Smart-P-ID/12/293410) | Pipelines: the application "adds a pipeline entry in the T_Pipeline table" without the user creating one, and the relationship between pipeline and pipe run is implicit. Key attributes define implied pipelines. At publish, each group of runs with the same key values is matched to a pipeline, or one is created; a run with a missing key value belongs to none. Special Cases: a nozzle's item tag is unique only within its equipment. |
| REF-TECH-023 | Hexagon, [Understanding Reference Data Settings](https://docs.hexagonppm.com/r/en-US/SmartPlant-P-ID-Options-Manager-Help/Version-2014-R1-7.1/743507), Options Manager Help, 2014 R1 (7.1) | Reference-data settings; a pipeline can be named from run properties such as the tag sequence number and fluid code. |
| REF-TECH-024 | Hexagon, [Using Off-Page and Utility Connectors](https://docs.hexagonppm.com/r/en-US/SmartPlant-P-ID-Help/2014-R1-7.1/175461), SmartPlant P&ID Help, 2014 R1 (7.1), and [Out-of-Date Drawing Criteria Dialog](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Drawing-Manager/12/172966), Drawing Manager, version 12 | An off-page connector pair represents continuation, not flow, and each side has a to or from orientation. In the Drawing Manager topic, the mating property holds the mate's drawing ID; REF-TECH-019's MatingOPCPath topic describes the same property as a path to the mating symbol, for pairs drawn with different symbols, so the two sources describe it differently. |
| REF-TECH-025 | Hexagon, [Default Item Tag Configurations](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Help/12/833021), version 12, and [Configure an item tag's format](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Support-Utilities/2019-9.0/829716), 2019 (9.0) | Equipment may not share an item tag. Calculated item tag values are read-only, and item tag validation covers listed item types only; piping components are not among them. |
| REF-TECH-026 | Hexagon, [Revising Documents](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Drawing-Manager-Help/2019-9.0/947499), Drawing Manager Help, 2019 (9.0) | The combination of a revision's major and minor values must be unique in the plant. |
| REF-TECH-027 | Hexagon, [Tool Requirements for Integrating Smart P&ID](https://docs.hexagonppm.com/r/en-US/Smart-P-ID-Integration-Help/12/161445), version 12 Update 7, and [Using the SmartPlant Migrator](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Help/11/175875), version 11 | Piping connects to equipment through nozzles; an offline instrument reaches its vessel through a nozzle and a connect-to-process signal line. By default, item tag validation does not allow duplicate tags for loops or instruments. |
| REF-TECH-028 | Hexagon, [Transformation Programs Dialog](https://docs.hexagonppm.com/r/en-US/Intergraph-Smart-P-ID-Drawing-Manager/12/173035), Smart P&ID Drawing Manager, version 12 | Duplicate item tags are allowed in the plant only for some item types, pipe runs among them. |
| REF-TECH-029 | abdullahserour, [sppid-oracle-queries](https://github.com/abdullahserour/sppid-oracle-queries/blob/e1ae443f16e1bc033f7ef5fecb5f54bccd8a599e/sppid_oracle_queries.sql), commit `e1ae443f`; one administrator's queries against real Smart P&ID databases, with no licence | Secondary only. Class tables share one key with the base tables; keys are 32-character GUID strings; a representation row carries the drawing's key and the model item does not. Its findings are cited; none of its text is copied. |

## Drawing extraction references

Accessed 2026-10-05 UTC. These are documentation and model-card inspections, not
P&ID benchmarks or installed dependencies. Model weights were not downloaded.
Pinned source revisions aid review; runtime compatibility and complete dependency
licenses remain separate gates.

| ID | Inspected primary source | Supported claim | Limits and outstanding checks |
| --- | --- | --- | --- |
| REF-TECH-008 | [LiteParse README](https://github.com/run-llama/liteparse/blob/b2a87350e5a40638d8e39d47875a6b8f4e4a0faf/README.md), commit `b2a87350e5a40638d8e39d47875a6b8f4e4a0faf`; repository metadata identifies Apache-2.0 | Local PDF parsing, bounding boxes, screenshots, JSON, bundled Tesseract and replaceable OCR; not an LLM | Pin a package release and platform dependencies; verify evidence coordinates and scans; its document benchmarks do not establish P&ID topology accuracy |
| REF-TECH-009 | [LlamaParse overview](https://developers.llamaindex.ai/python/cloud/llamaparse/), rolling service documentation | Hosted generative parsing, diagram support, structured output, custom instructions and versioned tiers | No tier selected or request executed; verify current prices, tier limits, grounding fields, retention/training terms, regions and upload permission |
| REF-TECH-010 | [Firecrawl Parse documentation](https://docs.firecrawl.dev/features/parse), also inspected via its [Markdown representation](https://docs.firecrawl.dev/features/parse.md) | PDF pages and typed layout blocks include bounding boxes and Markdown-span grounding; JSON extraction and OCR fallback are documented | Service features are not proof of self-hosted parity; verify truncation, pricing, effective retention mode, third-party processing, and P&ID results |
| REF-TECH-011 | [Granite-Docling-258M model card](https://huggingface.co/ibm-granite/granite-docling-258M/blob/982fe3b40f2fa73c365bdb1bcacf6c81b7184bfe/README.md), revision `982fe3b40f2fa73c365bdb1bcacf6c81b7184bfe` | Apache-2.0 model-card declaration; document conversion, Docling integration, full-page and bounding-box-guided inference | Card says not intended for general image understanding; inspect Docling/runtime packages and all model dependencies before adoption |
| REF-TECH-012 | [PaddleOCR-VL-1.6 model card](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6/blob/c5630abae1d940eafe0697512a0325494b02ab42/README.md), revision `c5630abae1d940eafe0697512a0325494b02ab42` | Apache-2.0 model-card declaration; multimodal document parsing, text spotting, table/formula/chart recognition | General benchmark results are publisher claims, not LIONG measurements; pin runtime, preprocessing and additional models; test hardware fit |
| REF-TECH-013 | [Qwen3-VL-8B-Instruct model card](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/README.md), revision `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b` | Apache-2.0 model-card declaration; visual interpretation, spatial grounding and OCR | No engineering accuracy established; pin compatible runtime and decoding settings, verify image limits, memory and source grounding |
| REF-TECH-014 | [SAM 3 README](https://github.com/facebookresearch/sam3/blob/2345a4ad109ac29c569da749c91d84f10dc08c40/README.md) and [SAM License](https://github.com/facebookresearch/sam3/blob/2345a4ad109ac29c569da749c91d84f10dc08c40/LICENSE), commit `2345a4ad109ac29c569da749c91d84f10dc08c40`; license dated 2025-11-19 | Text/visual-prompted segmentation returns masks, boxes and scores; official setup lists Python 3.12+, PyTorch 2.7+, CUDA GPU/CUDA 12.6+; checkpoint access is gated | Custom use/redistribution restrictions need review and specific acceptance; no assumed CPU/Mac or P&ID support. README also advertises SAM 3.1, which is not automatically the evaluated checkpoint |

The requested Meta project page returned an error during inspection; SAM claims
above come from the official repository and license. No hosted extraction API was
invoked, no documents were uploaded, and no license agreement was accepted.

## Review outcome

Primary evidence establishes a native DEXPI 2.0 example and a separately licensed legacy example collection. It does not yet establish a working native 2.0 toolchain. Dataset-level rights checks and public scan coverage remain open. [The decision register](LIONG-REG-001-decisions.md#open-questions-and-package-level-gates) holds the state of the DEXPI questions (GATE-001).

No new requirement or ontology adoption is approved by this register. The next review should decide the artifact set and bounded mapping candidates before implementation planning.
