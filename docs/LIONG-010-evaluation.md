# LIONG-010: Evaluation and acceptance evidence

Status: Proposed draft v0.1. The requirements are user-approved; the fixtures, measurement protocol, controls, numerical gates, and workload below are proposed. Of its checks, only SCN-001's structured route and SCN-005's minimal invalid-reference rejection have run, on the visible R0 development fixture, and SCN-001's structured route also on W-SP's W0 (see "Current evidence"). No benchmarks, public-data annotation checks, or recovery drills have been executed.

## What acceptance means

Acceptance requires trustworthy connectivity, maintained approved history, and evidence-supported engineering use. A plausible graph picture or valid XML file does not establish these outcomes.

Use [synthetic data](LIONG-006-synthetic-data.md) for exact expected results and controlled failures. Use independently checked public drawings for extraction quality and review effort. Keep those evidence classes separate. [Users and requirements](LIONG-002-users-and-requirements.md) owns the requirement IDs; [interfaces and workflows](LIONG-008-interfaces-and-workflows.md) owns the user actions.

The approved use cases are UC-001 ingest backend and UC-002 review drawings under OUT-001; UC-003 reconcile/publish and UC-004 approve proposed under OUT-002; and UC-005 investigate asset/isolation and UC-006 export subgraph under OUT-003.

All expected artifacts below are future deliverables. The current documentation package can be checked for traceability, but that check cannot mark an implementation acceptance row as passed.

## Evaluation boundary and matching

Evaluate both required routes. The backend route must start with committed backend records, generate DEXPI 2.0, and then produce the graph. The flat route must start with P&ID files and retain automatic output before review. Both routes must project to the shared engineering comparison view.

Freeze source files, truth versions, predictions, review edits, and transformation versions before scoring. The evaluated processes must not read private canonical aliases or answer keys. Only a separate trusted scorer can resolve output identities against the private mapping after predictions are sealed. It must not send matching hints back to the extraction or review process.

Use one-to-one entity matching. In synthetic cases, the private manifest and source-local evidence establish permitted identity correspondences. In public cases, independently checked annotations and page regions establish them. A type mismatch is one false positive and one false negative, not a partial match. Duplicate predictions beyond the first permitted match are false positives.

Score an edge only when its endpoints match, its relationship type matches, and its direction matches where direction is established. Score undirected or unknown-direction source relations using the declared representation, without awarding credit for invented direction. An edge with an unmatched endpoint is a false positive. A missing endpoint also leaves each associated expected edge as a false negative. Parallel evidence for one relation does not create extra relations.

For R0, entity recall has 17 expected nodes as its denominator and edge recall has 31 expected edges. Precision uses the actual prediction counts, which may differ. Report engineering-only node recall with denominator 15 as a separate slice. Report FLOW recall with denominator 14, ON_SHEET with 15, INSTRUMENT_PARENT with 1, and CROSS_SHEET_REFERENCE with 1. State the slice on every result. Do not mix physical connectivity with contextual links.

## Metric definitions

Every result must show its raw numerator and denominator. `N/A` means the denominator is zero; it does not mean a perfect score or permission to omit a required fixture. Report the reason and relevant counts.

| Metric | Exact unit and denominator | Zero-denominator rule |
|---|---|---|
| Entity precision | Correct one-to-one entity matches / all predicted entities, including duplicates. Equivalently TP/(TP+FP). | No predicted entities: N/A. Still report missing expected entities. |
| Entity recall | Correct one-to-one entity matches / all expected entities in the frozen scoring scope. Equivalently TP/(TP+FN). | No expected entities: N/A. Still report extra predictions. |
| Edge precision | Correct matched relation instances / all predicted relation instances, including duplicates and invented direction. | No predicted edges: N/A. Still report missing expected edges. |
| Edge recall | Correct matched relation instances / all expected relation instances in the frozen scope. | No expected edges: N/A. Still report invented edges. |
| Supported source coverage | Supported source assertions faithfully represented with resolvable evidence / all supported source assertions in the source inventory. | No supported assertions: N/A; the route lacks evidence of supported coverage. |
| Source accounting coverage | Source assertions classified as faithfully represented, explicitly unsupported, or unresolved / all inventoried source assertions. Categories are mutually exclusive. | Empty inventory: N/A and an invalid run for a nonempty required source. |
| Unsupported relationship rate | Predicted accepted relationships without admissible source evidence or an approved, declared mapping rule / all predicted accepted relationships. This is an evidence metric, separate from correctness. | No accepted relationships: N/A, with raw unsupported count zero and recall still reported. |
| Evidence coverage | Published nodes and edges with resolvable source identity, revision, and evidence / all published nodes and edges. | Empty graph: N/A; cannot satisfy baseline acceptance. |
| Review edit rate | Source assertions changed, added, removed, or resolved by the reviewer / all expected assertions in the frozen review scope. Count each assertion once, and report edit types separately. | No expected assertions: N/A; still report edits made. |
| Review time per sheet | Active reviewer seconds / sheets reviewed. Pause time and extraction wait time are excluded and reported separately. | No reviewed sheets: N/A, not zero effort. |
| Residual error rate | Incorrect or missing assertions after review / expected assertions in the frozen review scope. Extra assertions count as errors too, so this ratio can exceed 1. | No expected assertions: N/A; report extra assertions as a count. |
| Publication success rate | Source revisions completely published / eligible committed source revisions submitted for that run. Deliberately invalid revisions are a separate rejection cohort. | No eligible revisions: N/A. Never count an expected rejection as a success or a failure of this rate. |

A source assertion is one inventoried entity existence/type fact, relationship fact, or attribute value with its evidence reference. Define the inventory before extraction. Score existence/type as one assertion, each relation once, and each attribute key/value/unit once. Do not inflate coverage with repeated text or multiple evidence links. Missing, null, and unknown are distinct declared values.

Report attribute exact-match counts by field and unit as well as entity/edge scores. For synthetic R0, contextual tags, pipe diameter values/units, I1's unit, revision references, and document evidence must match exactly. Semantic unit normalization is allowed only through a frozen, documented mapping. Missing physical inputs must remain missing.

An unsupported source feature and an unsupported output relationship are different. The former is source content outside the declared subset and needs a visible finding. The latter is an accepted output assertion without evidence and is a control failure. Neither can be hidden by removing items from the inventory after inspection.

### Automatic versus reviewed results

Save an immutable automatic output and score it before a reviewer sees it. After review, save a second output plus the action log and score again against the same truth version. Report TP/FP/FN and field errors for both. Do not call the post-review result automatic extraction accuracy.

To compare effort, time independent manual annotation and assisted review on matched drawing tasks. Use separate reviewers or a counterbalanced order to reduce memory effects. Report reviewer count, experience, task order, instructions, active time, unresolved items, and adjudication time. The relative effort change is `(manual active seconds - assisted active seconds) / manual active seconds` for the same task scope. If manual time is zero or no paired comparison exists, report N/A. A negative result means assisted review took longer.

Report total active seconds and seconds per sheet for each method, along with medians and ranges when enough tasks exist. Include startup/training time separately. Faster review cannot compensate for residual critical connectivity errors.

## Proposed extraction candidate comparison

Assess LiteParse, LlamaParse, Firecrawl Parse, Hugging Face Docling/Granite-Docling-258M, PaddleOCR-VL-1.6, Qwen3-VL-8B-Instruct, and optional SAM3 without selecting them. [LIONG-007](LIONG-007-stack-and-architecture.md) owns candidate details and gates. Sources are REF-TECH-008 through REF-TECH-014 in the [reference register](LIONG-REF-001-reference-register.md). This protocol grants no upload, paid-call, installation, or adoption permission.

Use the paired fixtures in [LIONG-006](LIONG-006-synthetic-data.md#proposed-extraction-candidate-subcases) under SCN-002/009/010/015/016. Freeze identical eligible source inputs and scoring scope. Compare parsing quality (text, layout, tables, tags, and region coordinates) separately from engineering topology (ports, links, crossings, cross-sheet continuity, and bypasses). A successful parse cannot establish engineering correctness.

### Parser truth and matching

Before held-out inference, freeze an independently checked annotation manifest
containing source/page hashes, page dimensions and orientation, region IDs,
normalized block types, text-line strings, tag strings, boxes, table cells, and
explicit reading-order pairs where meaningful. A table cell includes its row,
column, row span, column span, and text. P&ID symbols have no assumed prose
reading order. Record annotation disagreements and adjudication before sealing
truth; exclude genuinely unscorable regions only through a predeclared scope rule.

Freeze each parser's adapter to a common representation before inspecting held-out
results. Define how native output becomes text lines, tags, tables, cells, and
figures, including the label map and any split/merge rules. The adapter may not use
expected text or gold boxes to repair predictions. A whole-page Markdown string
without locations cannot receive localization credit. Report full-page detection
separately from transcription of supplied crops.

Map predicted geometry through recorded render/crop/tile transforms into the
original unrotated page frame, then normalize x by page width and y by page height.
Represent boxes as `[left, top, right, bottom]` in `[0,1]`. Invalid or missing
geometry cannot match a located truth item. Deduplicate overlapping tile outputs
using frozen rules, not the answer key.

Proposed region matching uses the same page and normalized type with box
intersection-over-union (IoU) at least 0.50. Select a maximum-cardinality one-to-one
matching, maximize summed IoU among those matchings, then break ties by sorted
truth-region ID and stable prediction index. Do not use text similarity to select
geometry matches. The 0.50 threshold is a proposed scoring rule, not an acceptance
target or measured accuracy; freeze its approved value before comparison.

For ordinary text, use Unicode NFC and collapse whitespace runs to one space,
with leading/trailing whitespace removed. Preserve case, punctuation, numbers,
and symbols. For tags, use NFC and trim outer whitespace only; do not remove
hyphens or confuse `O` with `0`. Store both raw and normalized strings.

| Parser measure | Scoring unit and numerator/denominator |
| --- | --- |
| Layout localization precision/recall | One matched region is a TP; unmatched/duplicate predictions are FP and unmatched truth regions are FN. Report TP/predicted and TP/expected by block type, with the declared IoU threshold. |
| Region quality | Sum box IoU over matched region pairs / number of matched pairs. Always report alongside localization recall; missed regions must not disappear behind a high conditional IoU. |
| Character error rate | Sum Levenshtein edits for geometry-matched text lines, plus lengths of unmatched truth lines as deletions and unmatched predicted lines as insertions, divided by total normalized truth characters. Errors can exceed the denominator. |
| Tag transcription and detection | Report exact normalized text matches / geometry-matched tag pairs as conditional transcription accuracy. Separately report exact-text-and-geometry correct tags / all expected tags and / all predicted tags, so missed and invented tags remain visible. |
| Table structure | Within geometrically matched table regions, match cells one-to-one by exact row/column/span tuple. Duplicate cells count as FP. Report matched cells / predicted cells and / expected cells. All cells of unmatched tables count as FP or FN respectively. |
| Table content | Cells with correct structure and exact normalized text / all expected cells and / all predicted cells. Report structure and content separately; a plausible Markdown table is not automatically correct. |
| Reading order | Correct predicted directed order pairs / predicted pairs and / annotated pairs after matching their region endpoints. Unmatched endpoints cannot score as correct. Only explicitly annotated meaningful pairs are in scope. |

All zero denominators yield N/A with counts and a reason, never a perfect score.
For required features a parser cannot emit, report the limitation and missing
predictions; do not remove their truth items to improve the score. A corpus with
no tables cannot establish table capability. Retain per-page results and
micro-aggregated numerators/denominators, split by native PDF, scan, and drawing
condition. No composite parser score can offset a critical topology error.

For the optional SAM 3 ablation, use separately annotated symbol masks. Match
instances on page and declared symbol class with mask IoU at least 0.50, using
the same one-to-one tie-breaking rule. Report detection precision/recall and
conditional mean mask IoU, alongside topology and review effort. Missing mask
annotations mean mask quality is unmeasured, not established by box accuracy.
Refinement with a supplied human box or exemplar is a separate configuration
from automatic text-prompted detection.

### Inference configuration and engineering scoring

Freeze prompts, model/checkpoint and provider versions, service tiers, decoding settings, seeds where supported, render/tile transforms, merge rules, and segmentation settings. Compare each eligible extraction configuration with and without SAM3; disclose unsupported pairings. Retain full-page context alongside tiles and declare which visual inputs each model receives. Text-only topology inference must be a separately labeled experiment, never a silent substitute.

Use the existing matching and denominator definitions. Report hallucinated edges as false-positive counts and edge-precision errors, distinct from the unsupported-relationship evidence metric. Report port/entity and link/edge TP/FP/FN on a frozen annotated slice, with recall denominators from expected items and precision denominators from predictions. Do not add port nodes to the R0 17/31 comparison view. List missed bypasses, false junctions, invented cross-sheet links, and unknown-continuation errors separately as critical findings. Raw model scores are not calibrated engineering certainty.

Score automatic and reviewed outputs separately and measure review effort with the paired method above. Repeat live inference at least three times with fixed configuration and report all output differences, not just the best run. Separately replay captured responses offline to test downstream determinism. Replay does not measure fresh model/provider nondeterminism. Retain request, response, intermediate artifact, and output hashes subject to the governance boundary.

Report end-to-end cost alongside quality: successful, retried, rejected, and indeterminate calls; billed units; GPU time; hosting; storage; and reviewer time. Record actual charges or unavailable billing evidence, authorized caps, quotas, throttling, and recovery delays. Do not assume free tiers, low review effort, or zero cost for failed requests. Self-hosted and hosted parser results are separate configurations, with no presumed parity.

## Proposed acceptance gates

For controlled synthetic cases, propose exact matching after required review: entity and edge precision/recall equal 1.0, supported source coverage equal 1.0, and evidence coverage equal 1.0. All expected attributes and scenario-specific sets must match. R0 must produce exactly 17 nodes and 31 edges, not merely those totals with different contents.

Propose zero unsupported accepted relationships, zero private truth leaks, zero prohibited role actions succeeding, zero partial publications, and zero proposed-state leakage into approved queries. Intentional corrupt inputs must produce their exact expected rejection or uncertainty result. An expected failure is not a missing test.

No numeric public-data accuracy target is approved or proposed here. First inspect licensed data, freeze independently checked annotations, and measure a baseline by symbol, connection, document condition, and ambiguity class. Then propose empirical targets with sample sizes, error costs, and review capacity. Record the accepted targets before running a fresh held-out evaluation. Repeated tuning on the held-out corpus invalidates that corpus as independent evidence.

Review all critical failures separately. A missed bypass, invented cross-sheet flow, unsupported isolation claim, lost approved history, wrong equipment bridge, partial revision, or leaked answer key blocks acceptance regardless of average precision. Report the affected object/revision and remediation evidence. A summary percentage cannot waive a critical failure.

## Acceptance matrix

Component responsibilities are logical responsibilities, not selected products or separate services. The [stack and architecture](LIONG-007-stack-and-architecture.md) may implement several in one small application. SCN-001's structured route and SCN-005's minimal invalid-reference rejection have run on the visible R0 development fixture, as "Current evidence" below describes. All other checks have status **Not executed**.

| Requirement and outcome/use case | Scenarios | Expected artifact and acceptance observation | Component responsibility |
|---|---|---|---|
| REQ-001 backend DEXPI; OUT-001 / UC-001 | SCN-001 | Backend snapshot, generated DEXPI, subset validation report, normalized graph diff showing exact R0. Direct backend loading does not satisfy the route. | Backend adapter, DEXPI writer/parser |
| REQ-002 flat validation; OUT-001 / UC-002 | SCN-002 | Original sheets, automatic prediction set, review actions, reviewed graph, and route-parity report. Reviewed R0 equals 17/31. | Drawing extractor, review workflow, shared model |
| REQ-003 source authority; OUT-001 / UC-001, UC-002 | SCN-002, SCN-008 | Dataset authority declaration and discrepancy report. Altered drawing cannot replace backend flow; conflicting register cannot silently reparent I1. | Source registry, validation |
| REQ-004 fidelity; OUT-001 / UC-001, UC-002 | SCN-001, SCN-002, SCN-010 | Exact object/edge/attribute diff, evidence inventory, unsupported-content report, direction checks. Unknown continuation remains unknown. | Shared model, DEXPI mapping, drawing extraction |
| REQ-005 stable identity; OUT-002 / UC-003 | SCN-003, SCN-011 | Identity mapping history and before/after graph diff. E2's ID and operational links survive rename; deletions remove only the stated current objects/edges. | Identity mapping, publication |
| REQ-006 crossregister validation; OUT-001 / UC-001, UC-002 | SCN-005, SCN-008 | Mandatory-check report for tag, type, parent, unit, and optional gaps. Invalid complete revisions are rejected. | Asset/instrument adapters, validation |
| REQ-007 event/reconciliation/idempotence; OUT-002 / UC-003 | SCN-004, SCN-014 | Delivery log, source revision inventory, reconciliation diff, publication ledger. Duplicate/missed/out-of-order cases converge without regression or duplicates. | Source event writer, worker, reconciler |
| REQ-008 atomic publish; OUT-002 / UC-003 | SCN-005, SCN-014 | Failure-point trace and reader observations. Every observed state is the complete old or new snapshot; rejected Rbad leaves R0 unchanged. | Candidate validator, graph publisher |
| REQ-009 proposed/approved authority; OUT-002 / UC-004 | SCN-006, SCN-013 | Separate proposal/current query outputs, role audit and stale-base rejection. Review alone cannot approve; approval still requires validation. | Proposal workflow, role controls, publisher |
| REQ-010 history and MOC; OUT-002 / UC-003, UC-004 | SCN-003, SCN-007 | Reconstructed snapshot digests, source/publication history, time-qualified query results and MOC links. C1 preserves original publications. | Revision store, history query, MOC adapter |
| REQ-011 work/document/measurement links; OUT-003 / UC-005 | SCN-011 | Five-node/four-edge contextual diff, work status, document regions, static reading and unresolved-match finding. No asset link for the ambiguous mention. | Context adapters, equipment bridge, asset explorer |
| REQ-012 isolation boundaries; OUT-003 / UC-005 | SCN-009, SCN-010, SCN-013 | Two-path R0 result, one-path R2 result, incomplete-continuity result, graph revision and evidence. No valve sequence or safe-isolation authorization. | Connectivity query, application response |
| REQ-013 export completeness; OUT-003 / UC-006 | SCN-012 | Selection manifest, 14 engineering nodes and 14 FLOW edges, evidence attachments, missing-input report. Calculation readiness is false. | Exporter, completeness checker |
| REQ-014 provenance and permissions; all outcomes | SCN-001, SCN-002, SCN-015 | Source manifests, synthetic declarations and separate public licensing register. Unresolved rights block intended use/distribution. | Fixture generator, source register, dataset custodian |
| REQ-015 truth/key isolation; all outcomes | SCN-015 | Partition/lineage audit, sealed prediction hashes and rejected contamination attempts. Zero leaked private keys, answers, or sibling worlds. | Dataset custodian, execution boundary, trusted scorer |
| REQ-016 evaluation definitions; all outcomes | SCN-001–SCN-016 | Run report with raw counts, denominator definitions, N/A reasons, pre/post review results and unmeasured limits. Critical failures listed individually. | Evaluation harness, report owner |
| REQ-017 access/audit/recovery; OUT-002 / UC-003, UC-004; OUT-003 / UC-005 | SCN-006, SCN-013, SCN-014 | Allowed/denied actions including self-escalation and publisher bypass; independent-backup restore manifest, snapshot digests, post-restore permission tests, and measured recovery limitations. Source commit and graph publish remain separate. | Role controls, audit store, recovery runner |
| REQ-018 package traceability; all outcomes | SCN-001–SCN-016 | Requirement-to-scenario-to-artifact index with versions and known gaps. Documentation evidence is separated from implementation evidence. | Documentation/report owner |

The proposed role matrix allows the reviewer to accept drawing extraction, the maintenance/process engineer to inspect/export permitted published information, and the engineering-change approver to approve modifications. The publisher is a validated system action, not a human bypass. One person may use both reviewer and approver roles, but each action records the active role. No role has real isolation authority.

SCN-013 through SCN-015 include all mandatory subcases in
[LIONG-006](LIONG-006-synthetic-data.md#mandatory-subcases-for-scn-013-scn-014-and-scn-015).
SCN-015 acceptance requires denied reads and no protected canary content through
logs, exports, caches, and restored copies, not only a clean input manifest.
R0 is a visible development oracle; only fresh held-out worlds support blind
evaluation or hidden-truth isolation claims.

## Export input contract for SCN-012

Propose a pipe-network pressure-drop input assembly as the named downstream example, subject to source/tool inspection and approval. It demonstrates preparation only. Selecting this candidate here does not implement a calculation or claim engineering validity.

Select all process objects on upstream E1-to-E2 paths in R0. The output contains 14 engineering nodes, excluding I1, plus all 14 FLOW edges. Supply ON_SHEET and CROSS_SHEET_REFERENCE evidence through referenced document attachments or explicit provenance records. Do not create dangling exported graph edges to omitted documents.

The proposed input inventory has five required categories: complete selected topology, segment geometry, fluid properties, operating boundary conditions, and valve pressure-loss data. For this fixture, only topology is complete. Diameter is present for all six segments; length and roughness are missing for all six. Density and viscosity are missing, equipment boundary pressures/flow conditions are missing, and coefficients/positions are missing for both valves.

Report each missing field against each affected object, available units, selection criteria, source/graph revisions, and mapping versions. Do not collapse these gaps into a single readiness score. DEXPI export is a separate capability and requires its own subset/completeness validation. Never label a general JSON graph export as valid DEXPI.

## Workload and performance boundary

SCN-016 is a proposed measurement protocol, not a performance result or service-level promise. The simple local baseline proposes four logical CPU cores, 16 GiB RAM, SSD storage, and no GPU. This baseline does not exclude GPU extraction candidates. Use separate GPU and hosted cohorts, including the official CUDA-based SAM3 route if authorized. Record actual CPU/GPU hardware, memory, drivers, runtime, model versions, provider limits, OS, container limits, graph engine, and cache state. Report cohort-specific performance; do not attribute differences across unlike hardware or provider limits solely to model quality.

| Workload | Exact unit and proposed size | Measurement boundary |
|---|---|---|
| Baseline ingestion | One two-sheet R0 world, 15 engineering objects, 17 total comparison nodes, 31 edges | Source retrieval to complete publication; separate DEXPI generation, parsing, validation, and graph publication times |
| Flat extraction | The two sheets, each rendered at 300 dpi on 297 × 210 mm pages; record actual pixel dimensions | File decode to immutable automatic predictions; reviewer time excluded from extraction latency |
| Scaled ingestion | 100 disjoint R0-sized worlds: 200 sheets, 1,500 engineering objects, 1,700 total comparison nodes, 3,100 edges | One world/revision per publication unit; do not create one facility-wide transaction |
| Update replay | For each of the 100 worlds, R0/R1/R2 plus duplicate R1, followed by one full reconciliation; separate runs omit R1 or deliver R2 first | Commit-to-publication lag, processing time, attempt count, duplicates, rejected revisions and final graph digest |
| Query run | Single caller, 100 repetitions each of asset lookup, R0 path query, R0/R2 diff, and SCN-012 export | Request accepted to complete response; report cold first call separately from warm calls |
| Recovery run | Each SCN-014 interruption on one R0→R1 transition | Fault-to-correct-publication time plus source/graph state and audit evidence |

Use namespaces that keep the 100 worlds disjoint. After R2 in every world, the exact engineering comparison total is 1,500 nodes and 2,600 edges. Contextual records are excluded unless the run manifest explicitly adds them.

Report wall-clock duration, CPU time where available, peak resident memory, disk bytes, output counts, and failures per stage. Report median, p95, and maximum only with the sample count and percentile method. Use nearest-rank p95 for the proposed 100-query runs. No latency, throughput, or memory gate is claimed before baseline measurement.

Run each small ingestion at least three times under the same declared cache condition and retain all results. These proposed repetitions estimate local variability, not production capacity. Single-caller local runs do not support concurrency, multi-site, availability, or real-time telemetry claims. Safety and exactness gates still apply to every workload size.

## Run artifacts and report format

A future run bundle must contain:

1. A run manifest with source bundle hashes, hidden split commitment, scenario revision, generator/configuration versions, and the actual machine limits.
2. Frozen inputs, automatic output, reviewed output where required, and their SHA-256 digests.
3. A source inventory and exact normalized node/edge/attribute differences, including unsupported content and unresolved matches.
4. DEXPI generation/validation evidence for the backend route, plus review acceptance evidence for the flat route.
5. Source event, reconciliation, publication, role, and recovery records with timestamps and linked MOC identifiers.
6. Per-scenario results and the requirement matrix, using `pass`, `fail`, `blocked`, or `not executed`, with a reason and artifact path for each.
7. Raw scoring counts, automatic/post-review comparisons, public-data slices, critical failures, and measured workload results.

Keep the private answer key outside the evaluated run bundle. The report may publish aggregate scores and sanitized failure explanations after scoring. Record which artifacts may be redistributed and which remain restricted by data permissions.

The report header must state the tested revision, source authority, graph revision, data class, review status, and evaluation scope. A synthetic run cannot certify public extraction quality. A static reading cannot demonstrate a live telemetry integration. A paper recovery design cannot demonstrate recovery.

## Current evidence and implementation handoff

MILESTONE-001's structured slice runs in `scripts/check.sh` and CI. `scripts/run_slice.py` takes R0, R1 and R2 from the Plant 3D-style backend through DEXPI and Neo4j. Each published graph matches the answer key exactly: 17 nodes and 31 edges for R0 and R1, 15 and 26 for R2. It rejects Rbad before publication with the key's reason, "FLOW P6->VB has missing endpoint VB". With `--backend sps`, the same script takes W-SP's W0 from the SmartPlant-style backend through DEXPI. In CI, one run publishes the snapshot's graph to Neo4j, and the published graph matches W-SP's answer key exactly; another reads the loaded SQL Server backend, and its parsed graph matches the answer key exactly. The cross-sheet query returns TO-S2/B on DEMO-PID-101 continuing to FROM-S1/B on DEMO-PID-102, with the two sheet-link rows as evidence. That covers SCN-001's structured route on the visible development fixture and on W-SP's baseline, and SCN-005's minimal invalid-reference rejection, not held-out or public data. All other scenario checks are not executed. No public accuracy, review-time saving, DEXPI conformance, hardware performance, security enforcement, or recovery result has been measured.

Implementation should first generate and inspect R0, verify the selected DEXPI subset, and establish a working source-to-graph comparison. Then add failure fixtures and role/history controls before measuring public extraction or workload performance. Preserve the same denominators and scenario IDs through that work.

Track unresolved model, source, control, and threshold choices in [decisions](LIONG-REG-001-decisions.md). Link implementation tasks and execution steps through the [build runbook](LIONG-011-build-runbook.md), rather than presenting these proposed artifacts as existing tests.
