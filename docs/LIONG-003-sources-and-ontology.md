# LIONG-003 Sources and ontology

| Document control | Value |
| --- | --- |
| Status | Draft for review |
| Version | 0.1 |
| Inspection date | 2026-10-05 UTC |
| Dependencies | [LIONG-001 charter](LIONG-001-charter.md), [LIONG-002 users and requirements](LIONG-002-users-and-requirements.md) |
| Authority | Authoritative location for source eligibility and ontology mapping proposals, pending review |
| Vocabulary authority | [GLOSSARY.md](../GLOSSARY.md) |
| Evidence | [LIONG-REF-001 reference register](LIONG-REF-001-reference-register.md) |

## 1. Decision boundary

LIONG should assess the official DEXPI 2.0 reference example first, then use licensed legacy examples for drawing and migration tests. This is a Proposal, pending review. No dataset, ontology import, parser, or provider is selected by this document.

The approved requirements remain unchanged. The backend path requires an engineering backend database, DEXPI 2.0, and the graph. Reviewed flat PDFs and scans may enter the shared engineering model directly. The documented DEXPI subset must preserve the required engineering objects, identities, revisions, connectivity, and evidence. Publication and safety gates remain those in [REQUIREMENTS.md](../REQUIREMENTS.md).

All new selection rules, mapping details, and acceptance checks below are Proposals, pending review. Source observations report what was inspected; they do not approve adoption. Record parent proposals and their disposition in [LIONG-REG-001](LIONG-REG-001-decisions.md).

LIONG is independent of PPC. The exceptions to the open-source condition are listed once, in [REQUIREMENTS.md](../REQUIREMENTS.md#context). This document authorizes no implementation, deployment, spending, or external submission of private data.

## 2. Source eligibility proposals

Public availability and permission to redistribute are separate findings. A public download is not a license. A software license does not automatically cover drawings bundled with the software.

Proposal: keep an eligibility record for each selected artifact, not just its website.

| Field | Proposed content |
| --- | --- |
| Origin | Publisher, exact URL, reference ID, release or commit, retrieval date, and content hash |
| Rights | License text location, applicable artifact scope, attribution, modification notices, third-party exclusions, and permitted distribution |
| Engineering scope | Declared authoritative source, facility context, source revision, encoding, supported objects, drawing coverage, and known omissions |
| Evaluation use | Structured fidelity test, drawing extraction test, migration test, or contextual reference |
| Provenance | Public original, transformation of a public original, or clearly labeled synthetic generation |
| Review | Eligibility decision, reviewer, unresolved rights or technical questions, and allowed uses |

Proposal: retain metadata and links while redistribution remains unresolved. Do not vendor an artifact with unclear terms. Derived annotations, crops, raster images, and converted XML need their own provenance and rights assessment. Synthetic degradation of a licensed vector drawing does not make the drawing independently created.

Public data and synthetic data serve different purposes. Public examples can expose format and extraction problems. Synthetic backend records provide controlled revisions, expected connectivity, tag renaming, ambiguity, bypasses, and rejected updates. Two synthetic backends follow the documented storage patterns of SmartPlant P&ID and AutoCAD Plant 3D, using original names. Neither copies a vendor schema. Importing a public DEXPI file alone cannot demonstrate backend-to-DEXPI generation.

## 3. DEXPI version and artifact findings

### 3.1 What was verified

The official 2.0 HTML specification identifies itself as **2.0.0**, released on 2025-10-10, under CC BY 4.0. The official specifications page says 2.0 first uses DEXPI XML for both specification models and instances. It incorporates the P&ID 1.4 plant model and an improved process model. These statements do not make older Proteus XML interchangeable with DEXPI XML. See REF-STD-001.

The downloaded 2.0 reference instance has a `Model` root. It imports `Core.xml` and `Plant.xml` from `https://data.dexpi.org/models/2.0.0/`. It contains `Object`, `Components`, `Data`, and reference structures. Its local object IDs support references within the file; those IDs do not by themselves establish LIONG identity across revisions.

The 2.0 XML documentation labels its schema download `DEXPI_XML_Schema_RC_1.xsd`, but the link resolves to `_static/DEXPI_XML_Schema.xsd`. That file declares schema version `1.0.0`. The schema version is not the engineering model version. The register records both the actual URL and inspected bytes' hash.

The legacy C01 reference example in the official GitLab training repository has a `PlantModel` root. Its directory is explicitly `dexpi 1.3`. The repository also contains a `dexpi 1.2` directory. Neither is a native DEXPI 2.0 fixture. See REF-DATA-002.

The current official landing page recommends DEXPI 2.0.1, released on 2026-09-30, as a fix release replacing 2.0. LIONG's target is now 2.0.1, at the specification repository's V2.0.1 tag ([DEC-061](decisions/DEC-061-dexpi-2-0-1.md)). The 2.0.0 findings above remain as inspected. No 2.0.1 schema or instance has been pinned or validated yet; GATE-001's pull request pins them by SHA-256.

### 3.2 Compatibility assessment

| Candidate | Inspected evidence | Proposed use and remaining gate |
| --- | --- | --- |
| DEXPI 2.0 official XML and schema | Native `Model`-root reference instance and XSD were fetched and parsed as XML. Model import URLs failed TLS hostname verification. | Selected at 2.0.1 for the slice (DEC-061). The GATE-001 pull request is to add pinned copies of the model files, and validation will never fetch them ([DEC-062](decisions/DEC-062-vendored-model-files.md)). LIONG will write its own generator and parser on lxml ([DEC-063](decisions/DEC-063-own-dexpi-generator-and-parser.md)). |
| DEXPI TrainingTestCases | Licensed legacy examples, including C01 XML/SVG and nozzle, off-page connector, and intersection cases | Use for legacy parsing and drawing assessment. Conversion requires an explicit mapping and loss report. Do not rename the format to 2.0. |
| pyDEXPI | Inspected README states DEXPI 1.3 support and a Proteus XML loader. Code license is AGPL-3.0-or-later. | Excluded for DEXPI 2.0 (DEC-063). At most a legacy research reference. |
| bpmn2dexpi | MIT-licensed TypeScript tool whose `--validate` option checks DEXPI 2.0 Process and Plant files against the XSD and the information models. Targets 2.0, not 2.0.1. See REF-STD-010. | Recorded, kept out of the slice, and looked at again when it supports 2.0.1 ([DEC-069](decisions/DEC-069-bpmn2dexpi-recorded-not-used.md)). |
| DEXPI GraphicBuilder | GitHub README declares migration to GitLab. Current GitLab implementation was not inspected. | Unverified renderer candidate. Confirm encoding, exact version, license, and output fidelity before selection. |
| Generic XML tooling | No LIONG DEXPI implementation exists in this assessment | XML parsing or XSD validation alone cannot validate engineering classes, imported models, connectivity, or the supported subset. |

### 3.3 Proposed format acceptance gates

1. Pin the engineering model release, serialization specification, exact XSD, example instance, and complete imported model set. Record hashes and licenses separately.
2. Identify an input's actual encoding before parsing. Report unknown versions and unsupported elements. Do not infer the encoding from `.xml` or a DEXPI product label.
3. Validate XML syntax and the selected schema. Then validate model references, class/property meaning, multiplicity, and subset constraints.
4. Generate native DEXPI from synthetic backend records. Compare expected equipment, valves, instruments, pipe segments, connection points, tags, attributes, drawing membership, and cross-sheet references.
5. Verify stable identity through source revisions and tag changes. Preserve source identity separately from exchange-file IDs.
6. Test equivalent engineering meaning across both ingestion paths. Preserve flow direction only where supported by source evidence.
7. For any legacy conversion or outward export, report unsupported information and test semantic round trips. Successful import is not proof of export completeness.

These are proposed test details for existing requirements. They do not assert full DEXPI compliance or replace human review.

For the slice, [DEC-064](decisions/DEC-064-four-stage-dexpi-validation.md) decides gate 3's validation as four named stages (schema, references, model, LIONG rules) plus an exact round trip, and [DEC-072](decisions/DEC-072-claim-names-every-stage-that-ran.md) limits each claim to the stages that ran and names each one. None of this is built yet. The parser will also read DEXPI's 2.0.1 reference P&ID ([DEC-066](decisions/DEC-066-reference-pid-parser-test.md)).

## 4. Dataset assessment

| Reference and candidate | Public availability and rights evidence | Useful coverage | Limits and proposed disposition |
| --- | --- | --- | --- |
| REF-DATA-001: DEXPI 2.0 reference P&ID | Official appendix links XML and a graphical SVG representation. Specification carries CC BY 4.0. XML was retrieved; SVG link was inspected, but SVG content was not assessed. | Native encoding example, paired model/drawing candidate, selected Plant model structures | Specification license is clear; confirm downloadable asset coverage and any separate notices before bundling. Import dependencies currently have a TLS access failure. Candidate first fixture, not accepted benchmark. |
| REF-DATA-002: DEXPI TrainingTestCases | Official GitLab repository is public. Root LICENSE is CC BY 4.0 at inspected commit. C01 folder contains XML, SVG, HTML, and PPTX. | Legacy engineering examples and paired drawing/model candidates; directory coverage includes nozzles, off-page connectors, and pipe intersections | Review selected files for third-party notices and content quality. Legacy exports are not guaranteed truth. Use independent annotations for evaluation. Candidate for reuse with attribution and changes recorded. |
| REF-DATA-003: project-authored synthetic corpus | No corpus created in this task. Rights depend on original authorship and any reused inputs. | Controlled backend records, revisions, operational records, negative tests, and known expected graphs | Proposal only. Document generation rules and expected results in LIONG-006. Do not imply that generated records describe actual LIONG systems. |

No field-scan or flat-PDF collection passed a content and license assessment in this inspection. SVG availability is not evidence of real scan quality. Proposal: retain this as an evaluation gap rather than claim public scan coverage. Rasterized or degraded public vectors can support controlled tests, but results must remain separate from genuine scanned-drawing evaluation.

Before evaluating a public example, inspect its annotation quality, symbol conventions, drawing completeness, and expected connections. Keep automatic extraction results separate from reviewed results. Numerical accuracy targets remain deferred until inspection and baseline measurement.

## 5. Ontology and vocabulary proposals

Use bounded references and explicit mappings before considering imports. External terms do not replace the authoritative project glossary. No mapping below asserts `owl:equivalentClass`, `owl:sameAs`, or equivalent relationship semantics.

| Reference and official URL | Role and bounded proposal | Mismatches and limits | Inspected version and license evidence; open gate |
| --- | --- | --- | --- |
| REF-STD-001: [DEXPI](https://dexpi.org/specification/2.0/html/) | Engineering exchange model for the mandatory backend path; explicit subset mappings to the shared engineering model | Serialization is not a provenance, approval, or stable-identity policy. Plant, process, and drawing representation must remain distinct. | 2.0.0 HTML and native XML/XSD inspected; specification CC BY 4.0. Target is 2.0.1 (DEC-061); artifact pins and dependency resolution remain open under GATE-001. |
| REF-STD-002: [QUDT](https://qudt.org/schema/qudt/) | Reference selected unit and quantity definitions for engineering attributes and measurement values | Matching dimensions alone does not establish the same physical meaning. Gauge/absolute pressure, temperature offsets, and measurement basis need explicit source context. | Live schema labels itself 3.5.2; CC BY 4.0 metadata and a UCUM rights notice inspected. Pin immutable unit vocabularies and assess embedded rights before reuse. |
| REF-STD-003: [PROV-O](https://www.w3.org/TR/2013/REC-prov-o-20130430/) | Candidate mapping for source artifacts, transformation activities, responsible agents, and derivation | Provenance does not prove correctness, engineering approval, or publication. It does not choose historical storage. | W3C Recommendation 2013-04-30. Document-use notice inspected; exact distributable ontology artifact and its license remain to be pinned. |
| REF-STD-004: [SOSA/SSN](https://www.w3.org/TR/2017/REC-vocab-ssn-20171019/) | Small observation subset connected through the equipment bridge | A reading, an observation activity, a sensor, and a feature of interest are different objects. A P&ID instrument tag alone does not establish all of them. | W3C/OGC Recommendation 2017-10-19. Live SOSA RDF declares W3C 2015 software/document and OGC software license links. Freeze matching RDF artifacts and dependency scope. |
| REF-STD-005: [Web Annotation](https://www.w3.org/TR/2017/REC-annotation-model-20170223/) | Reference body/target and selector patterns for drawing evidence and reviewer comments | A selected region is evidence location, not an engineering connection or truth judgment. PDF pages, raster coordinates, rotation, and crop transforms need local conventions. | W3C Recommendation 2017-02-23; document-use notice inspected. Pin vocabulary/context licenses before redistribution. |
| REF-STD-006: [IOF Core and Maintenance](https://spec.industrialontologies.org/portal/release/202603/) | Assess a small work-order and asset/process distinction; reference or map selected terms rather than adopt IOF as the foundation | BFO-based commitments and dependencies need review. The maintenance work-order definition has a stated restriction concerning supporting activities. | Release browser 202603 and work-order term inspected, both with MIT notice. Imported files and their licenses remain unverified. |
| REF-STD-007: [IDO/POSC Caesar](https://rds.posccaesar.org/) | Candidate reference for industrial asset and property classification only | Do not treat IDO, a reference data library, and ISO publications as the same licensed artifact. No exact term mapping verified. | Root and attempted core ontology URL returned HTTP 403. Version, definitions, artifact license, and dependency closure remain unverified. |

### 5.1 Checked term examples

These examples are Proposals, pending review, based on inspected definitions.

- QUDT defines `qudt:Unit` as a quantity value chosen as a scale for measuring quantities of the same kind or equivalent dimension. A selected unit reference could accompany a source value. The inspected `qudt:QuantityValue` description is sparse, so this document does not prescribe its full mapping.
- PROV-O defines starting-point entities, activities, and agents. A source revision artifact could be represented as a `prov:Entity`, with a transformation represented as a `prov:Activity`. Review the applicable axioms before adopting these mappings.
- SOSA defines `sosa:Observation` as an act that estimates or calculates a property's value. Keep the recorded result separate from that act. `sosa:phenomenonTime` concerns when the result applies; it is not necessarily the result production time.
- Web Annotation describes an annotation through related resources, usually a body and target. A reviewer comment could target a drawing region without changing the engineering object identified by the drawing appearance.
- IOF's `https://spec.industrialontologies.org/ontology/construct/MaintenanceWorkOrderRecord` describes a maintenance process. Its formal definition also requires the record to be input to a maintenance process. The source calls the definition provisional because it excludes work orders made only of supporting maintenance activities. Keep a LIONG work-order record separate from an executed activity; do not assert equivalence with this class.

No IDO term example is included because its definition could not be inspected.

### 5.2 Proposed mapping record and checks

Each mapping record should identify the local glossary concept, external term IRI, inspected definition, artifact version, mapping direction, and intended use. Record whether the relationship is a reference, a restricted translation, or an unresolved candidate. Include preconditions, information loss, evidence, reviewer, and test cases.

Keep these distinctions visible in tests:

- An engineering object differs from its tag and its drawing appearances.
- A work order targets equipment; a document can merely mention a tag.
- A measurement identifier reaches an asset through the equipment bridge, not text equality alone.
- A proposed engineering state differs from an approved state and a published state.
- Source derivation, extraction acceptance, engineering-change approval, and isolation authorization have different meanings.

Ontology alignment must not manufacture connectivity, resolve ambiguous asset matches, approve a revision, or establish that equipment is safe to isolate.

## 6. PPC reference boundary

REF-PPC-001 is pinned to `01027a84be5d453cbb4e2ea091e4884729918b15`. Its implementation directories contain `.gitkeep` placeholders. The inspected PPC-019 labels its ontology recommendations as proposed, with no adoption asserted.

Proposal: reuse the practices of separating source claims from project decisions, limiting ontology scope, and recording unresolved compatibility questions. Do not import PPC's EPM/ECE authority structure, runtime stack, or enterprise scope into LIONG. No PPC prose or licensed implementation is copied here. No repository license was found in the inspected pinned tree, so copying PPC material remains a rights gate.

## 7. Handoffs and open decisions

The linked documents are part of this draft package. Each handoff remains subject
to the destination document's review and implementation gates.

| Destination | Proposed handoff |
| --- | --- |
| [LIONG-000 index](LIONG-000-index.md) | Link this proposal and its evidence register. |
| [LIONG-004 domain model](LIONG-004-domain-model.md) | Review bounded term mappings and preserve glossary distinctions. |
| [LIONG-005 data contracts](LIONG-005-data-contracts.md) | Define selected DEXPI artifacts, mapping records, evidence locators, and unsupported-content reports. |
| [LIONG-006 synthetic data](LIONG-006-synthetic-data.md) | Define original synthetic fixtures and expected results. |
| [LIONG-007 stack and architecture](LIONG-007-stack-and-architecture.md) | Test native 2.0 compatibility and license fit before selecting adapters. |
| [LIONG-008 interfaces and workflows](LIONG-008-interfaces-and-workflows.md) | Expose evidence and unresolved matches without implying engineering authority. |
| [LIONG-009 governance and operations](LIONG-009-governance-and-operations.md) | Review source eligibility, notices, and approval responsibilities. |
| [LIONG-010 evaluation](LIONG-010-evaluation.md) | Separate synthetic fidelity, public extraction, and reviewed quality. |
| [LIONG-011 build runbook](LIONG-011-build-runbook.md) | Later document reproducible artifact acquisition after rights and compatibility gates pass. |

The blocking format questions are the exact 2.0-family release, trusted access to its imported models, and a tested native reader/writer. The public flat-PDF/scan corpus and IDO assessment remain open. These gaps limit adoption, not completion of this documentation review.
