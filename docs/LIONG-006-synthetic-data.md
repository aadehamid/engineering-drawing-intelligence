# LIONG-006: Synthetic data and scenario specification

Status: Proposed draft v0.1. The requirements in [REQUIREMENTS.md](../REQUIREMENTS.md) are user-approved. All fixtures, example models, controls, seeds, limits, and acceptance proposals below remain proposals. This document specifies implementation work. It supplies neither generated datasets nor executed tests.

## Purpose and scope

Use two small synthetic canonical worlds, R0 for Autodesk and W-SP for SmartPlant (DEC-029 and DEC-035 in the [decision register](LIONG-REG-001-decisions.md)), each producing separate source representations. The representations of one world must describe the same physical system without sharing hidden answer keys with ingestion. This supports OUT-001 trustworthy connectivity, OUT-002 maintained approved history, and OUT-003 evidence-supported engineering use.

The facility context is a fictional LIONG demonstration in Lekki, Lagos State, Nigeria. No record represents an actual LIONG asset, drawing, approval, operating condition, or internal system. The example supports connectivity inspection, not engineering design or authorization to isolate equipment.

Read [sources and ontology](LIONG-003-sources-and-ontology.md), [domain model](LIONG-004-domain-model.md), and [data contracts](LIONG-005-data-contracts.md) alongside this specification. [Evaluation](LIONG-010-evaluation.md) defines the scoring rules and evidence required for these scenarios.

## Canonical world and separate representations

A canonical world defines engineering truth, including revisions and intended errors.
The R0 world and answer key below are visible development examples. They are not
private or suitable for blind evaluation. Fresh held-out worlds keep their truth
and scoring keys private. Produce these artifacts separately:

| Representation | Content and authority |
|---|---|
| Canonical truth and answer key | Exact relationships, scenario changes, permitted matches, and expected failures. R0 is a public development oracle. For fresh held-out worlds, only the generator and trusted scorer may read the private keys and truth. |
| Engineering backend | Source-local primary keys, equipment, valves, instruments, pipe segments, connection points, contextual tags, attributes, drawing appearances, revision records, and approval events. This is authoritative for the structured dataset. Two synthetic backends follow the documented storage patterns of SmartPlant P&ID and AutoCAD Plant 3D, using original names. Neither copies a vendor schema. |
| Flat P&IDs | Two sheets with symbols, tag text, established flow arrows, line connections, and reciprocal cross-sheet labels. They contain page/region evidence but no hidden object IDs. |
| Asset hierarchy | A separate register with its own record keys, facility context, location, asset type, and explicit cross-reference evidence. It validates engineering data without replacing connectivity. |
| Instrumentation register | Independent record keys, instrument tags, parent equipment, units, and required attributes. Deliberate conflicting versions support SCN-008. |
| Work orders and documents | Separately keyed records with target references, recorded status, and page/region references. A document mention is not a work-order target. |
| Measurements | Measurement identifiers, units, timestamps, readings, and explicit evidence for an equipment bridge. These are static or replayed records. |
| Management of Change records | Reason, affected assets, proposed revision, approval status, approval history, and links to technical ingestion records. The baseline needs no change record. |

The structured route is backend → DEXPI 2.0 → shared engineering model → graph. The flat route is P&ID → extraction → reviewer acceptance → shared engineering model → graph. The DEXPI subset and its mappings require separate verification; these fixtures do not claim DEXPI conformance.

For development route parity, generate a backend-authoritative dataset and a separate drawing-only dataset from R0. In the former, drawing differences become discrepancies. In the latter, reviewed extraction establishes the accepted baseline. Held-out parity requires fresh private worlds. A drawing must never silently replace the backend's authoritative relationships.

Production-like stable identities come from persisted identity assignments and declared source cross-references, not tag hashes or private truth keys. Persist mappings through renames and revisions. Match drawing appearances only when evidence supports the match. When evidence is ambiguous, retain unresolved candidates for review.

## Exact baseline R0

The following aliases are published development-fixture aliases, not source keys,
graph IDs, filenames, metadata, or extraction hints. Each generated representation
receives a separate source-local key space. R0 results establish regression behavior,
not blind extraction performance or hidden-truth isolation. A trusted scorer resolves
fresh held-out outputs only after the evaluated run is sealed.

The graph fixture contains 17 nodes: 15 engineering objects and two drawing documents. Drawing appearances are provenance records rather than extra nodes in this comparison view. A different storage layout must project to this view without dropping information.

| Alias | Type | Display tag or drawing name | Sheet |
|---|---|---|---|
| E1 | Equipment, supply vessel | TK-101 | S1 |
| E2 | Equipment, receiving vessel | TK-102 | S2 |
| V1 | Valve | XV-101 | S1 |
| VB | Valve, bypass branch | XV-102 | S1 |
| I1 | Instrument, pressure indication | PI-102 | S2 |
| J1, J2 | Connection point, branch junction | No display tag | S1 |
| X1 | Connection point, outgoing sheet reference | TO-S2/A | S1 |
| X2 | Connection point, incoming sheet reference | FROM-S1/A | S2 |
| P1, P2, P3, P4, P6 | Pipe segment | L-101-1, L-101-2, L-101-3, L-101-4, L-101-B | S1 |
| P5 | Pipe segment | L-101-5 | S2 |
| S1, S2 | Drawing document | DEMO-PID-001, DEMO-PID-002 | Self, not a membership edge |

All tags have context `DEMO-LEKKI/UNIT-A`. Pipe segments have nominal diameter `50 mm`. I1 has measurement unit `bar` and parent E2. Valve suitability and operating state are unknown. Pipe lengths, roughness, fluid properties, and operating pressure are absent. The generator must not fill these missing values.

The exact directed `FLOW` edge set is:

```text
E1 -> P1    P1 -> J1    J1 -> P2    P2 -> V1
V1 -> P3    P3 -> J2    J2 -> P4    P4 -> X1
X1 -> X2    X2 -> P5    P5 -> E2
J1 -> P6    P6 -> VB    VB -> J2
```

These 14 edges express object-level connectivity for comparison. Detailed DEXPI ports must preserve these connections when projected to this view. A line crossing without a junction is not a connection. Direction is present because each listed path has explicit source evidence.

The other 17 edges are:

```text
INSTRUMENT_PARENT: I1 -> E2
CROSS_SHEET_REFERENCE: X1 -> X2
ON_SHEET:
  E1,V1,VB,J1,J2,X1,P1,P2,P3,P4,P6 -> S1
  E2,I1,X2,P5 -> S2
```

Comma-separated sources above expand into one edge per source. The baseline therefore contains 31 edges. `CROSS_SHEET_REFERENCE` supplies document continuity evidence; it is not an additional flow path. `INSTRUMENT_PARENT` is contextual and does not create process flow. No reverse edges, self-membership edges, extra instrument flow edges, or inferred direct E1-to-E2 edge belong in R0.

Every node and edge needs source evidence and revision provenance. Each appearance records its document revision, page, region, and source-local identifier where available. Multiple evidence records do not create multiple physical objects or duplicate relationships.

## Revision and time rules

Except for the stated R0 → R1 → R2 sequence, scenarios start from fresh R0. Scenario branches cannot contaminate one another.

| Revision | Exact change in the engineering comparison view | Expected result |
|---|---|---|
| R0 | Baseline above | 17 nodes, 31 edges. |
| R1 | Rename E2 from TK-102 to TK-202; record synthetic MOC-1 | Same 17 identities and 31 edges. Keep the old tag's revision history. |
| R2 | From R1, delete VB and P6; remove `J1→P6`, `P6→VB`, `VB→J2`, and their two `ON_SHEET` edges; record MOC-2 | 15 nodes, 26 edges. No bypass branch remains. Retain deletion history. |
| Rbad | From R0, delete VB but leave `P6→VB` and `VB→J2`; record MOC-bad | Reject the entire revision for dangling endpoints. Published R0 stays at 17/31. |
| Proposal Q1 | From R0, make the R2 deletion as a proposal, with MOC-Q1 | Proposal view has 15/26. Approved R0 remains 17/31 until approval and validation succeed. |

The backend R0 fixture includes an explicit synthetic source-approval record.
The drawing-only R0 baseline has extraction acceptance and publication but
`engineering_decision=not_applicable`. Before using that drawing-only baseline
for SCN-006, a separate approver authorizes a baseline source revision and the
normal ingestion path publishes it. Review acceptance alone never supplies that
approval, and the earlier unapproved publication remains unchanged.

MOC objects and technical logs sit outside these engineering-view counts. Each modification's evidence must include them in its contextual view.

Keep the following times distinct:

| Field | Meaning |
|---|---|
| `source_recorded_at` | When the source committed the revision or recorded a correction. Source order uses explicit revision ancestry/sequence, not arrival time. |
| `effective_from`, `effective_to` | When the source asserts the information applies in engineering history. The end is exclusive. |
| `ingested_at` | When the ingestion process received or retrieved the source revision. |
| `published_at` | When the graph made the validated revision available as one complete published state. |

For the ordinary sequence, propose R0 effective at `2030-01-01T00:00:00Z`, recorded at 08:00, ingested at 08:01, and published at 08:02 that day. R1 uses the same times on January 2; R2 uses January 3. These are fixture times, not measured service times.

For a temporal correction, source revision C1 is recorded January 4 at 08:00 and changes R1's effective start to January 1 at 12:00. Its ingestion is 08:01 and publication is 08:02 on January 4. C1 cites MOC-1 and records the correction reason and approval. It does not rewrite the immutable R1 publication artifact.

A query for engineering time January 1 at 13:00, using knowledge available January 3, returns TK-102. The same engineering time, using knowledge available January 5, returns TK-202. A query pinned to published R0 always returns TK-102. Corrections must not manufacture an earlier publication time or erase the original assertion.

## Scenario catalogue

Every row specifies a proposed fixture, its expected result, and a result that must fail. SCN IDs are stable references for implementation and evaluation.

| ID | Fixture and action | Exact expected result | Counterexpected result |
|---|---|---|---|
| SCN-001 | Ingest backend R0 through generated DEXPI 2.0. Include every supported object, edge, attribute, and evidence record. | Published engineering view equals the 17-node/31-edge R0 set. Report the DEXPI subset and any unsupported fields explicitly. | Direct backend-to-graph loading presented as DEXPI evidence; XML validity used as proof of engineering fidelity. |
| SCN-002 | Render R0 as two flat sheets. Capture automatic output, then review it in a drawing-only dataset. Separately submit an altered drawing that omits `P6→VB` to the backend-authoritative dataset. | Reviewed drawing-only view equals R0 after source-supported matching. Altered drawing raises one connectivity discrepancy and leaves the backend-authoritative R0 unchanged. Automatic errors remain in the pre-review report. | Copies of backend keys hidden in the drawing; reviewer corrections reported as automatic accuracy; drawing overwrites backend connectivity. |
| SCN-003 | Publish R1, then R2, with MOC-1 and MOC-2. Repeat E2's appearance in an evidence attachment and retain links from SCN-011. | R1 has 17/31, R2 has 15/26. E2 retains its identity and linked work/measurement records. Repeated appearance adds evidence, not an asset. Deleted objects stay in historical snapshots. | Rename creates a new E2; deleted valve remains in current paths; old tag loses its history. |
| SCN-004 | On independent runs deliver R1 twice; omit its event then reconcile; deliver R2 before R1. | Each run converges to the latest complete authorized source state. Exact R2 set is 15/26 when R2 exists. Revision/content identity prevents duplicate publication effects. Old events cannot regress the current pointer. | Duplicate entities, silently skipped source revisions, or late R1 replaces published R2. |
| SCN-005 | Submit Rbad; also try R0 variants with V1's tag equal to VB's, a wrong equipment type, and a missing mandatory I1 unit. | Each variant fails its named mandatory check. No partial change becomes visible. R0 remains 17/31 with its original digest. | Valid rows publish while invalid rows are held; mandatory failures become optional warnings. |
| SCN-006 | Compare Q1 with R0. Record a review action without approver authority, then a distinct approver action. For a second run approve Q1 after R1 has published. Also exercise the concurrent-approval fixture below. | Review alone does not promote Q1. Approval on the current base permits validation and one complete publication. Stale-base approval blocks publication; rebase to R1, review the changed diff, and obtain renewed approval. | Proposal affects normal approved queries; approval bypasses validation; stale proposal overwrites R1's rename. |
| SCN-007 | Reconstruct R0, R1, R2 and apply temporal correction C1. | Each pinned snapshot has its stated set and original publication evidence. The two time-qualified tag queries above differ as specified. Every modification traces to its MOC and approval history. | Current tags leak into old snapshots; correction destroys earlier recorded knowledge; ingestion time stands in for effective time. |
| SCN-008 | Engineering R0 and asset hierarchy place I1 under E2; a separately emitted instrumentation register places it under E1. | One parent conflict blocks the source revision because parent consistency is mandatory. No `I1→E1` parent edge is published. Corrected register version requires a fresh complete validation. Missing optional instrument range is a reported gap only. | Latest arrival wins; extraction silently reparents I1; register keys masquerade as engineering IDs. |
| SCN-009 | Inspect E2 connectivity inside the declared E1-to-E2 boundary. Compare complete R0 with complete R2. | R0 has exactly two simple directed E1-to-E2 paths. They differ at J1-to-J2: `P2,V1,P3` versus `P6,VB`. Removing V1 alone leaves the VB route in R0. R2 has exactly one path. | V1 alone is reported to eliminate both routes; either state is declared safe to isolate. |
| SCN-010 | In a drawing-only R0 variant, remove both cross-sheet labels and the evidence for `X1→X2`. Retain both connector endpoints and flag their continuation as unknown. | A provisional view has 17 nodes and 29 edges after removing the FLOW and CROSS_SHEET_REFERENCE pair. It cannot replace the complete baseline while continuity is mandatory. The connectivity response is incomplete, not "no path". | Geometric proximity invents a cross-sheet connection; disconnected provisional paths are presented as proof of no physical route. |
| SCN-011 | Add the operational fixture below and process the ambiguous document mention. Rename E2 with R1. | Exactly five contextual nodes and four accepted contextual edges are added. One ambiguous mention stays unresolved. The bridge and work target keep the E2 identity after rename. | A tag mention creates a work target or process edge; ambiguous text links to both assets. |
| SCN-012 | Export E2's R0 upstream selection for the proposed pipe-network pressure-drop input assembly. | Export includes E1,E2,V1,VB,J1,J2,X1,X2,P1–P6 and all 14 FLOW edges, with identifiers, units, provenance, revision and selection criteria. Completeness is insufficient because physical inputs are missing. | Export claims an analysis-ready calculation input without missing lengths/fluid data; omits the bypass; runs or validates a hydraulic calculation. |
| SCN-013 | Exercise reviewer, maintenance/process engineer, and engineering-change approver actions, including a single person switching roles. Attempt an isolation authorization. | The proposed role controls deny unauthorized approval/publication actions and record the role actually used. No role can authorize real-world isolation. Every analysis result states its revision, boundary, evidence, and safety limit. | Reviewer acceptance counted as change approval; role audit absent; any UI/API result authorizes operation or provides a valve sequence. |
| SCN-014 | Interrupt processing at each recovery point listed below; replay and reconcile. | Source commits remain committed. Graph readers see one complete old or new snapshot. Recovery converges without duplicate effects and preserves rejected-revision evidence. | Source and graph described as one distributed transaction; partial graph visible; acknowledged event disappears permanently. |
| SCN-015 | Attempt to include a truth alias, answer key, sibling evaluation drawing, or world lineage mapping in an ingestion bundle or evaluated process. | A pre-run manifest check rejects the contaminated bundle. Sealed evaluation inputs contain no private truth material; trusted scoring happens afterward. Partition overlap and contamination counts are zero. | A model receives expected edges as a retrieval document; random sheet splitting puts S1 in training and S2 of the same world in evaluation. |
| SCN-016 | Run the bounded workload plan in LIONG-010 with R0-sized and scaled independent worlds. | Record exact workloads, resources, stage timings, errors and review effort. Every output still satisfies the semantic/control checks. Results remain unmeasured until execution. | A synthetic latency proposal is reported as a benchmark; better speed excuses missing edges or failed safety controls. |

### Proposed extraction candidate subcases

These subcases extend SCN-002, SCN-009, SCN-010, SCN-015, and SCN-016 without changing their expected engineering results. The candidate assessment in [LIONG-007](LIONG-007-stack-and-architecture.md) does not select a product or authorize execution.

Use the same licensed inputs across eligible candidates: native PDFs, scans, dense drawings, crossings with and without junctions, tiny tags, cross-sheet continuations, and bypass paths. Preserve the R0/R2 and unknown-continuation expectations in SCN-009/010. Keep public drawings and synthetic variants separate, with frozen annotations for each variant.

Compare full-page and tiled inputs. Each render and tile retains the source page hash, source artifact identity, render transform, crop coordinates, scale, overlap, and tile-to-page transform. Freeze tile merging and duplicate suppression so overlapping evidence cannot create extra objects or edges. Do not replace visual topology assessment with an undeclared text-only LLM input.

Where technically eligible and separately authorized, pair the same extraction configuration with and without SAM3 segmentation. Record unsupported pairings rather than substituting another model. Segmentation supplies candidate regions, not verified engineering connectivity. SCN-002 retains raw and reviewed outputs; SCN-009/010 check bypasses and unsupported continuations; SCN-016 measures cost and runtime by cohort.

Extend SCN-015 with instruction-like text in drawings, parser responses, API prompts, logs, and caches. Deny attempts to change tools, approval rules, upload destinations, or access to truth. No answer key enters a provider request. Record sanitized denial evidence without copying protected canaries into provider-visible artifacts.

### Mandatory subcases for SCN-013, SCN-014, and SCN-015

SCN-013 must attempt self-assignment of the approver role, use of publisher
credentials by a human caller, direct graph mutation that bypasses the publisher,
consumer access to unpublished run findings and proposal comparisons, and
cross-dataset reads/writes. Deny each attempt without changing accepted state.
Record the principal, active role, action, target scope, denial, and before/after
publication digest. Test one valid action per authorized role as a positive control.

SCN-014 also restores into an empty environment from an independent backup, with
the original source storage unavailable. Verify checksums of artifacts and the
reconstructed R0/R1 publication sets, restore role/credential boundaries, and
repeat SCN-013 denial checks on the restored service. Produce a restore manifest,
snapshot digests, permission-test results, and measured recovery time and data
loss. A database-only restore without source evidence must fail the recovery gate.

SCN-015 uses fresh held-out worlds, not the published R0 oracle. Attempt truth
access through source bundles, file/storage reads, graph queries, application
logs, exports, caches, and restored copies under evaluated principals. Use marked
canary keys and an attempted-read audit without leaking the protected content into
the report. Deny all reads and verify no canary appears in accessible outputs.
Check sibling-world partition overlap separately. Contamination rejection alone
does not prove runtime isolation. Repeat the runtime access tests after restore.

In SCN-004, a full source snapshot may allow direct publication of R2 after validating its complete state and ancestry. The synthetic backends always supply full snapshots (DEC-037 in the [decision register](LIONG-REG-001-decisions.md)); the delta-only case below applies to other sources. Retain R1's source record and the fact that it was not published in that run. A delta-only source requires reconstruction of missing ancestors first. Historical queries must distinguish source revisions from states actually published.

Reusing a source revision ID with a different content digest is a source-integrity conflict, not a new idempotent delivery. Quarantine that input and retain the published state until the source supplies an explicit correction revision.

For the SCN-006 concurrent-approval fixture, create Q2 from R0 with only the R1 rename and its own MOC. Approve Q1 and Q2 against R0 before either publishes. Publish Q2 first. At Q1's publication boundary, compare its recorded base with the current approved revision in the same atomic operation that would advance the published pointer. Reject Q1 as stale. The current state has 17 nodes, 31 edges, and tag TK-202. Approval at an earlier time cannot bypass this final base check.

For SCN-009, the candidate valve cut set in complete R0 is `{V1, VB}` within the declared boundary. Removing either vertex alone leaves one E1-to-E2 route; removing both leaves none in this validated model. In complete R2 the candidate set is `{V1}`. These are graph counterfactuals, not instructions to operate valves. The same claim cannot be made in SCN-010 because continuity is unknown.

## Operational fixture for SCN-011

Extend R0 with exactly these five contextual nodes:

| Alias | Type and payload |
|---|---|
| W1 | Work order WO-DEMO-1, recorded status `open`, explicit source asset reference to E2 |
| D1 | Document NOTE-DEMO-1, page 1 region `[0.1,0.2,0.4,0.3]`, mentions E2 in facility/revision context |
| M1 | Measurement identifier PT-DEMO-1, unit `bar`, explicit equipment bridge to E2 |
| O1 | Measurement sample `2.0 bar`, observed at `2030-01-01T07:00:00Z` |
| D2 | Document NOTE-DEMO-2, page 1 region `[0.2,0.2,0.5,0.3]`, text "vessel", ambiguous between E1 and E2 |

Coordinates are normalized `[left,top,right,bottom]`. The exact accepted edges are `W1 TARGETS E2`, `D1 MENTIONS E2`, `M1 MEASURES_ASSET E2`, and `O1 SAMPLE_OF M1`. D2 has one unresolved matching finding with candidates E1 and E2, outside the accepted relationship set. D2 has no accepted asset edge. Combined with R0, this comparison view has 22 nodes and 35 edges.

The equipment bridge is the explicit `MEASURES_ASSET` relationship with matching evidence. A measurement's text tag alone is insufficient. Changing E2's display tag leaves that relationship unchanged.

## Recovery fixtures

An approved source record commitment and graph publication are separate durability boundaries. For the synthetic backends, the loader that applies a snapshot commits the revision and a durable pending-event record together, writing the event to an outbox in a third, non-vendor schema of the same database (DEC-047 in the [decision register](LIONG-REG-001-decisions.md)). The vendor schemas hold only the data each application saves. A small worker can retry delivery; no distributed two-phase transaction is required.

| Interruption point | Required recovery observation |
|---|---|
| Before source commit | No committed revision or deliverable event exists. The graph remains R0. |
| After source commit, before event delivery | Source R1 exists with its pending event. Delivery retry or full reconciliation discovers it. Graph R0 remains available meanwhile. |
| After delivery, before durable candidate storage | Redelivery retrieves the immutable revision. It must not depend on a lost process buffer. |
| During DEXPI generation or mandatory validation | Keep graph R0. Retry from source and versioned transformation inputs. Preserve validation failure evidence where applicable. |
| After candidate validation, before graph publication | Candidate is staged but invisible to normal queries. Retry validates its base and commits all graph changes together. |
| During graph publication | Within one graph publication boundary, readers see the complete old or new snapshot. Use a transaction or atomically select an immutable validated snapshot. |
| After graph publication, before event acknowledgment | Redelivery finds the publication by source/revision/content identity. It records successful handling without another graph effect. |
| Lost event or out-of-order event | Reconciliation compares authoritative source revisions/digests with the publication ledger. It detects missing work and never rolls the published pointer backward. |

The implementation must record an event ID, source revision, payload digest, attempt, outcome, graph revision, and failure reason. These controls are proposed; [governance and operations](LIONG-009-governance-and-operations.md) and the [build runbook](LIONG-011-build-runbook.md) define their implementation and recovery evidence.

## Reproducibility and separation

Propose generator version `synthetic-v0.1`. R0 is hand-authored and has no seed; the generator turns it into source representations deterministically. Seeds apply only to worlds the generator creates procedurally, such as held-out worlds or scaled worlds for SCN-016, and integer seed `2701006` goes to the first of them (DEC-016 in the [decision register](LIONG-REG-001-decisions.md)). A seed alone is insufficient. A generation manifest must include the generator commit, runtime and dependency lock hashes, schema/mapping versions, rendering settings, input parameters, and SHA-256 of every emitted file. Hash exact file bytes. For graph comparisons, separately hash a canonical UTF-8 representation with sorted node/edge tuples and explicit nulls.

Record the authoritative source, scenario, revision ancestry, effective-time assertions, source-local keys, evidence file hashes, and licensing/synthetic declarations in each source manifest. Exclude private aliases and truth mappings from distributable manifests. Use distinct public bundle IDs and a private lineage map. Hash commitments to private files may be recorded by the evaluation custodian, but do not supply reconstructible keys or seeds for held-out worlds to the evaluated process.

The private manifest maps each world lineage to every rendering, source representation, revision, crop, and perturbation. Partition by this lineage before generating training, development, and hidden evaluation bundles. All siblings stay in one partition. Splitting only pages, tags, file names, revisions, or raster variants does not establish independence.

This documented world belongs to development and cannot establish hidden-test generalization. Generate fresh hidden world lineages with separately held seeds. Freeze split membership and hashes before model tuning. Audit shared source templates and public drawing families as possible sibling leakage. A trusted scorer may hold the answer key after sealing predictions; extraction, review assistance, retrieval, and evaluated application processes may not.

## Public data and open decisions

Public drawings provide a separate empirical check. Record source URL, publisher, retrieval date, file hash, drawing family, permission basis, license version, attribution duties, and redistribution restrictions. Public availability does not establish permission. Exclude a dataset from distribution or model use until its applicable terms are resolved.

An independent engineering-data reviewer must check public annotations without copying model output as truth. A second reviewer adjudicates disagreements, including uncertain connectivity. Keep ambiguity and unsupported content visible in the annotation schema. Do not mix public and synthetic accuracy in one headline number.

The source register must expose licensing gaps and absent sample categories rather than fill them with assumed rights. See [reference register](LIONG-REF-001-reference-register.md). PPC reference commit `01027a84be5d453cbb4e2ea091e4884729918b15`, documents PPC-005, PPC-016 and PPC-018, is documentation context only. It supplies no LIONG data rights, engineering truth, runtime dependency, or acceptance result.

Before implementation, resolve the supported DEXPI mapping, public corpus permissions, downstream input requirements, and fixture/control approvals in the [decision register](LIONG-REG-001-decisions.md). New decisions must not silently alter the approved requirements or the SCN identifiers.
