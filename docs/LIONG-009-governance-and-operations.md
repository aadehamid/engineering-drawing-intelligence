# LIONG-009: Governance and operations

Version: 0.1
Status: Draft. All new controls, role assignments, operational targets, and retention choices are Proposed, pending user review. No control is configured or tested.

## Scope and evidence boundary

This document proposes controls for a public/synthetic demonstration of LIONG's engineering information workflows. It follows the confirmed [requirements](../REQUIREMENTS.md), [glossary](../GLOSSARY.md), and [logical architecture](../ARCHITECTURE.md). LIONG is independent of PPC. PPC patterns do not confer authority or create a runtime dependency.

The accepted roles are engineering-data reviewer, maintenance or process engineer, and separate engineering-change approver. Extraction acceptance does not approve an engineering modification. Engineering approval does not authorize real-world isolation. One person may hold both reviewer and approver roles in the demonstration, with the active role recorded for each action.

Only public data with suitable permissions and clearly labeled synthetic data belong in this demonstration. No sensitive real facility data, production credentials, private maintenance records, or live operational feeds are permitted. Infrastructure availability never makes an engineering result safe to use operationally.

The [data contracts](LIONG-005-data-contracts.md) own field definitions. The [interface proposal](LIONG-008-interfaces-and-workflows.md) owns user interactions. Technology choices belong to the [stack and architecture](LIONG-007-stack-and-architecture.md). Verification belongs to the [evaluation plan](LIONG-010-evaluation.md) and [build runbook](LIONG-011-build-runbook.md). Unresolved choices belong in the [decision register](LIONG-REG-001-decisions.md).

## Roles and actions

The following permission model is Proposed. "Allow" means within an explicitly assigned dataset scope. Any action not granted is denied. A role name supplied by a browser, command-line flag, folder name, or request body does not establish authority.

| Role | Read published state | Submit source/candidate | Accept extraction | Propose modification | Approve engineering change | Activate snapshot | Administer runtime |
|---|---|---|---|---|---|---|---|
| Engineering-data reviewer | Allow | Allow | Allow | Allow | Deny | Deny | Deny |
| Maintenance or process engineer | Allow | Deny | Deny | Deny | Deny | Deny | Deny |
| Engineering-change approver | Allow | Deny | Deny | Deny | Allow | Deny | Deny |
| Ingestion worker | Allow as needed | Allow | Deny | Deny | Deny | Deny | Deny |
| Logical publisher | Allow as needed | Read validated candidates only | Deny | Deny | Deny | Allow after gates | Deny |
| Operator | Allow for diagnosis | Reconcile or replay existing inputs only | Deny | Deny | Deny | Deny | Allow scoped recovery |
| Access administrator | Deny unless separately assigned | Deny | Deny | Deny | Deny | Deny | Manage approved role assignments only |

Export permission is a separate scoped grant for reviewers, consumers, and approvers. It requires license checks for the selected material. Review evidence access is limited to reviewers and approvers, with operational diagnostic access limited to what an operator needs. Worker and publisher reads exclude held-out evaluation truth.

The access administrator records role assignments based on approval by a separately designated demonstration owner. Actors cannot approve their own escalation. A runtime administrator gains no engineering decision authority from infrastructure access. Any emergency infrastructure action records its actor, reason, scope, and effect, and cannot substitute for engineering approval.

The local demonstration may simulate roles to test workflow behavior. Such role switching must display "simulated authorization." It does not demonstrate production authentication, tamper resistance, or isolation from a machine owner. Before any hosted use, server-side identity verification, role assignment, and authorization tests are required. Service credentials are distinct from human identities.

## Source authority and publication controls

Each dataset declares its authoritative source and mandatory validation profile before ingestion. Backend-authoritative datasets require an approved backend revision and DEXPI conversion. Drawing evidence reports discrepancies instead of overwriting backend facts. Drawing-only datasets require extraction acceptance for their baseline and subsequent reviewed revisions.

The Proposed integrity model retains immutable SourceArtifact and SourceRevision records with content hashes. Stable Object identities have versioned assertions and facility/tag aliases. Each assertion retains its source record or drawing region. A tag rename does not break accepted work order or equipment bridge links. Unsupported or ambiguous material remains a finding.

A Publication is separately keyed by source revision, mapping version, validation profile, and review decision. It includes content hashes and a published graph snapshot ID. Re-running unchanged inputs returns the existing publication. Changing a transformation produces a new publication context while preserving the original source. Conflicting content under an existing revision or publication identity is quarantined.

One logical publisher owns activation. Implementation may serialize requests or use a conditional transaction, but it must prevent competing writers from bypassing gates. It stages a complete candidate and activates its snapshot atomically. Source approval and graph activation are separate operations, without a global transaction.

Before activation, the publisher rechecks source authority, content hashes, required review, mandatory validation, engineering approval where applicable, and the expected active baseline. Stale approvals or proposal baselines block promotion. Re-review replaces automatic merging. Direct graph editing is not an authoritative source change.

When activation fails, consumers retain access to the last published snapshot. They see source-to-graph lag and the pending or rejected revision. If the last published snapshot is corrupt or cannot be verified, queries fail closed instead of serving it as trustworthy.

## Evaluation isolation

Operational source data and evaluation truth have different permissions. Public origin does not make a held-out annotation appropriate for worker access.

| Material or operation | Proposed access |
|---|---|
| Public/synthetic source input and declared registers | Workers and reviewers receive only the inputs permitted by the benchmark protocol. |
| Synthetic scenario generation and expected graph creation | A generator identity writes input packages and separate truth packages. It does not perform extraction or review acceptance. |
| Held-out annotations, expected objects/relationships, and answer keys | Generator and scorer identities only. Worker, publisher, reviewer, consumer, and normal operator identities are denied. |
| Raw automatic output and reviewed output | Store separately. Reviewers may correct the reviewed copy, never overwrite the raw result used to measure automatic quality. |
| Scoring | A scorer identity reads the sealed outputs and protected truth. It emits approved aggregate metrics and finding summaries. |
| Evaluation release | A designated evaluation custodian authorizes which reports may leave the protected area and records the decision. |

Separate directories are an organizational convenience, not access controls. Proposed enforcement uses process identities and storage permissions or isolated execution environments. Generator/scorer credentials are not mounted in worker or reviewer execution contexts. Logs, error payloads, caches, exports, and backup restores preserve the same boundary.

If one person administers every local identity, the demonstration cannot prove isolation from that person. Evidence must state this limitation. A suspected truth leak invalidates the affected evaluation run. Quarantine the run and any results influenced by it, investigate access paths, and rerun with uncontaminated inputs and outputs. SCN-015 tests denied access, not merely separate path names.

## Intake, licensing, and credentials

Before admitting public material, the proposed intake record captures origin URL or repository revision, retrieval date, owner or publisher, usage terms, redistribution permissions, attribution requirements, and a content hash. Unclear rights block intake or redistribution until resolved. A public download link is not proof of permission.

Synthetic inputs record their generator version, scenario identifier, seed where used, and an explicit synthetic label. Generated work orders, measurement samples, and Management of Change records do not imply access to LIONG systems. Each package records licenses for source data and dependencies separately.

Credentials remain outside versioned files, export packages, screenshots, and logs. The proposed runtime reads secrets from a local secret mechanism or deployment secret store selected during implementation. A sanitized configuration example may name a variable but contains no value.

Each credential has one purpose and the least scope needed. The ingestion worker can read its approved source and write candidates. The publisher can read gate evidence and activate snapshots. A backup identity can write backup objects without gaining engineering approval authority. Evaluation truth credentials belong only to generator/scorer contexts. Remote access uses separate credentials for development, publication, and recovery where supported.

If a credential is exposed, stop the affected remote operation, revoke or rotate it, inspect access records, and assess affected artifacts before resuming. Redaction after a commit is not a substitute for revocation. No credential or paid service is required to review this documentation.

## Proposed extraction API and model controls

The user permits assessment of proprietary parser/model APIs, not document upload or spending. Candidates remain unselected; [LIONG-007](LIONG-007-stack-and-architecture.md) owns the candidate table and technology gates. SAM3 requires specific custom-license review before adoption. Dataset use permission and permission for third-party processing are separate records.

Before any remote request, obtain explicit authorization for the provider, endpoint, version/tier, named input set, permitted payload fields, processing region, and spend cap. Only approved public or synthetic pages, crops, and necessary metadata may leave the workspace. Exclude sensitive facility data, credentials, private answer keys, held-out annotations, and scoring hints. Public availability alone grants no upload permission.

Inspect provider retention, deletion, training use, data regions, subprocessors, and request/log/cache terms before authorization. Record the reviewed terms and date. A provider, version, tier, or terms change requires renewed gate review. Do not assume a hosted parser has the same behavior, license, or data boundary as its self-hosted counterpart.

Treat all document, API prompt, response, log, and cache content as untrusted data. Prompt injection cannot change tools, system or approval instructions, credentials, or allowed destinations. Parse responses into constrained candidate records and validate their evidence. No provider response can directly publish or approve an engineering change. The existing logical publisher and review gates retain authority.

Use scoped secrets outside tracked files and redact authorization headers and credentials from artifacts. Enforce an explicitly authorized spend ceiling, bounded retries, concurrency, and provider quotas before admitting calls. Count retries and rejected calls in the cost record, including unknown billing outcomes. Pause admission when authorization, budget, or quota evidence is unavailable.

Record input/configuration hashes, request identities, attempt outcomes, and response hashes for rate-limit recovery and unknown outcomes. Reuse captured responses only under their exact recorded context; do not assume providers support idempotency or make retries free. A disabled route fails explicitly unless an approved fallback is configured and named in the result. No silent provider, model, privacy, or quality downgrade is permitted.

These are proposed runtime controls, not configured safeguards. Assess them under SCN-015 and SCN-016, with recovery using the existing publication controls. Captured-response offline replay is separate from live inference and does not prove hosted availability or repeatability.

## Storage, retention, and disposal

The Proposed default is durable local storage for the demonstration record. Temporary process memory or a disposable notebook session is not the sole copy. Storage paths, database choices, encryption, backup destinations, and capacity remain implementation decisions. A local path name does not establish permission or durability.

Remote storage is optional. Cloudflare services and Databricks Free Edition are permitted exceptions to the open-source condition, not mandatory dependencies. SQL Server, hosted on an Azure SQL Database free-offer database, is a further exception: both synthetic vendor-style backends run on it (DEC-027). No service has been provisioned. Verify current terms, free-tier limits, deletion behavior, export capability, credential scopes, and recovery behavior before selecting either.

In particular, do not assume an R2 bucket or a Databricks Free Edition workspace guarantees retention, backup, version history, or recovery. Provider availability and a free-tier label supply no evidence of those controls. Retain an independently recoverable copy of required records.

The following lifecycle choices are Proposed. They are not statutory periods or claims about Nigerian regulatory obligations.

| Record class | Proposed retention and deletion rule |
|---|---|
| Immutable sources, revisions, publication manifests, transformation versions, validation evidence, review/approval decisions, and published snapshots | Retain for the demonstration's active lifetime and its agreed handoff period. Do not delete evidence needed to reconstruct a published state. The owner must approve an archival or disposal plan before closing the demonstration. |
| Management of Change history, object changes, tag provenance, and audit records | Retain with the publications they explain. A withdrawn approval or superseded tag remains historical evidence. |
| Evaluation input packages, protected truth, raw/reviewed outputs, and scoring configuration | Retain through reproducibility review and handoff under their original permission boundaries. Disposal requires evaluation custodian approval. |
| Quarantined or rejected candidates | Retain until findings are resolved and a reviewer/operator has preserved the failure evidence. Then delete bulky intermediates only if reconstruction and incident review remain possible. |
| Rebuildable caches and temporary renders | Delete after the owning run completes and necessary evidence is durable. Do not classify source regions, reviewed corrections, or manifests as disposable caches. |
| Export copies | Use an owner-approved expiry for hosted download copies. Retain the manifest, selection, snapshot reference, and completeness report with the publication record. |
| Backup copies | Keep at least one verified independent copy of the retained record. Frequency, copy count, encryption, and rotation require a capacity and restore test before adoption. |

No numeric retention duration is established in this draft. Pending that decision, there is no automatic purge of durable evidence. An operator checks free space before large runs and stops admission when capacity threatens record integrity. Retention approval must include backup copies and protected truth, not only primary storage.

If license withdrawal or unintended sensitive content requires deletion, quarantine the material and block affected distribution first. The owner determines the permitted removal scope. Record the deletion and its effect on reproducibility without retaining prohibited content in the audit entry. Do not claim full historical reconstruction after required source evidence has been removed.

## Audit and operational status

The Proposed audit record includes actor/service identity, active role, dataset scope, action, timestamp, request ID, run ID, referenced source and candidate hashes, decision IDs, snapshot IDs, outcome, and reason. Where applicable, include the expected and observed baseline. Secrets and protected truth never appear in the record.

Audit records append rather than replace prior decisions. Restrict write access to the application operation that emits the event. Hash verification and independent backup can detect some alteration; neither proves tamper resistance against an administrator controlling all local copies.

Status categories remain separate:

| Category | Proposed statuses and meaning |
|---|---|
| Technical run | Queued, running, succeeded, failed, or quarantined. A successful parse is not publication. |
| Validation | Pending, passed, or failed, with the profile version and mandatory versus optional findings. |
| Extraction review | Required/pending, accepted, rejected, or not required under the declared source path. |
| Engineering decision | Pending, approved, rejected, revoked, or not applicable to the initial baseline import. |
| Publication | Not requested, blocked, staged, or published, with a separate indication that a published snapshot is no longer active. |

A decision applies to exact reviewed content. Later revocation blocks pending promotion and records the reason. If revocation concerns an already published snapshot, the operator flags the snapshot and follows the incident procedure. Historical records are not rewritten to suggest approval never existed.

## Failure, quarantine, and recovery

Unknown authority, changed bytes under an immutable identity, failed mandatory checks, conflicting idempotency keys, stale approvals, and inaccessible gate evidence block publication. Quarantine preserves the input reference and findings. It never "repairs" source meaning or falls back to a less strict validation profile.

Proposed recovery proceeds as follows:

1. Identify the affected dataset and stop new publication attempts for that scope.
2. Record the incident, failing stage, last known verified snapshot, and outstanding source revisions.
3. Verify immutable source hashes, manifests, versioned mappings, profiles, and decision records.
4. Restore a backup into an isolated recovery environment with the original permission boundaries.
5. Verify the restored snapshot and reconstruct a selected historical publication from retained inputs.
6. Replay missed events or reconcile source inventory using existing revision and publication identities.
7. Compare object and relationship counts, identities, hashes, and gate outcomes with the retained evidence.
8. Resume activation only after the operator records verification and all normal publication gates still pass.

A crash before activation leaves a staged snapshot that normal readers cannot see. A crash after activation but before the caller receives a response must be resolved from the durable publication record. Repeating the request returns the published result rather than creating a second publication. Publication metadata and the active pointer must commit together.

Recovery does not fabricate new engineering approval. Rebuilding the exact historical state may reuse its historical evidence. Publishing changed content requires current review and approval. Moving the active pointer back is an explicit, audited recovery decision and must not falsely describe the old source as current.

Backups must include source artifacts, metadata, mapping/profile versions, audit and decision records, manifests, and the information needed to reconstruct snapshots. Include protected evaluation material only in a separately authorized backup scope. A database-only copy without evidence is insufficient.

Restore exercises must test denied access as well as data recovery. Record what was restored, which hashes matched, what remained unavailable, and elapsed recovery time. Recovery time and acceptable data-loss objectives remain Proposed choices to establish after measurement; no recovery guarantee is claimed.

## Proposed operational measures

These measures are definitions, not observed results or service-level commitments. Report each over a named demonstration run window with UTC start/end timestamps and dataset scope. If a window has no eligible events, report "not applicable" rather than zero percent.

| Measure | Definition and denominator | Proposed response |
|---|---|---|
| Request error rate | Failed application responses divided by all completed requests in the window, separated by operation and `400`, `403`, `409`, `422`, and `503`. Exclude asynchronous run failures from this denominator and report them separately. | Investigate authority denials, conflicts, and unavailable dependencies by category. Do not combine validation failures with infrastructure failure. |
| Run failure rate | Failed or quarantined terminal runs divided by all terminal runs completed in the window, separated by ingestion path and failure stage. Report pending runs separately. | Investigate repeated stage failures and retain their evidence. |
| Publication latency | For each published revision, elapsed time from source event or drawing submission receipt to activation. Report sample count, median, p95, and maximum for publications completed in the window. | Report review wait separately. Do not hide slow pending revisions by reporting completed latency alone. |
| Processing and review wait | Per completed run, measure worker execution time and time awaiting required human decisions. Report sample count and distribution separately for backend and drawing paths. | Distinguish resource delay from evidence or approval delay. |
| Source backlog | At window end, count known eligible source revisions lacking a terminal disposition, grouped by stage and dataset. Report the age of the oldest pending revision from receipt time. | Reconcile inventory and identify blocked work. |
| Source-to-graph lag | At window end, identify the newest known approved source revision and active published source revision for each scope. Report elapsed time since the unpublished approved revision was observed. | Warn consumers when the graph is behind. Do not subtract arbitrary revision strings as if numeric. |
| Mandatory validation rejection rate | Unique candidate contexts with at least one failed mandatory check divided by all unique candidate contexts completing validation in the window. Separate mapping/profile versions and avoid counting retries twice. | Diagnose mappings, source quality, and cross-register conflicts. |
| Replay correctness | Duplicate/replayed requests that reuse the correct recorded outcome divided by all intentional duplicate/replay requests in a named SCN-014 test window. Also report any duplicate objects or publications. | Any duplicate publication or partial activation blocks the demonstration gate. |
| Audit completeness | Mutating operations with all required audit references divided by all mutating operations attempted in a named test window, including denials. | Missing decision or publication evidence blocks acceptance. |
| Backup and restore evidence | At the checkpoint, report age of the latest independently verified backup and elapsed restore duration with counts of checked and mismatched artifacts. | Missing required backup evidence or mismatched hashes blocks recovery readiness. |

Numeric alert thresholds and latency targets require a measured baseline and user review. They remain unset. Proposed immediate blocking conditions are failed mandatory validation, suspected evaluation leakage, unauthorized writes, corrupt evidence, and incomplete snapshot activation. Extraction precision, recall, and manual-review effort belong in LIONG-010, separate from service error rates.

## Proposed operational gates

Every gate below is pending implementation and verification. A gate ID labels required evidence, not a test that has passed.

| Gate | Evidence needed before claiming readiness | Traceability |
|---|---|---|
| GATE-OPS-001: Authorization | SCN-013 denies reviewer-only engineering approval, consumer writes, publisher gate bypass, and self-escalation. A dual-role actor leaves separate role-specific decisions. Simulated authorization is labeled. | REQ-003, REQ-009, REQ-017 |
| GATE-OPS-002: Intake and provenance | Demonstrate license admission, immutable hash verification, rejected altered revision bytes, source locators, and contextual tag history. | REQ-004, REQ-005, REQ-014 |
| GATE-OPS-003: Publication integrity | Show whole-revision validation, single logical publisher enforcement, stale-baseline denial, and readers seeing only complete snapshots during activation. | REQ-006, REQ-008, REQ-009 |
| GATE-OPS-004: Replay and reconciliation | SCN-014 covers duplicate events, missed events, retry after unknown outcome, and crashes before/after activation without duplicates or false success. | REQ-007, REQ-008, REQ-017 |
| GATE-OPS-005: Evaluation isolation | SCN-015 proves worker/reviewer denial of truth through storage, logs, exports, caches, and restored copies. Raw and reviewed outputs remain distinct. | REQ-015, REQ-016 |
| GATE-OPS-006: Recovery | Restore an independent copy, verify hashes and permissions, reconstruct a historical snapshot, and report measured loss and elapsed time without an unsupported guarantee. | REQ-010, REQ-017 |
| GATE-OPS-007: Audit and observations | Join a source event to its run, findings, review, approval where required, publication, and export. Produce measures with denominators and time windows. | REQ-016, REQ-017, REQ-018 |
| GATE-OPS-008: Consumer safety | Show pinned snapshots, approved/proposed separation, explicit unknown connectivity, and no real-world isolation authorization or operating sequence. | REQ-009, REQ-011, REQ-012, REQ-013 |
| GATE-OPS-009: Storage and retention | Approve a retention lifecycle and backup scope. Verify any optional provider's current terms and recovery/export behavior before relying on it. | REQ-014, REQ-017, REQ-018 |
| GATE-OPS-010: Reproducible handoff | Package source/license manifests, contract and mapping versions, validation profiles, decisions, snapshots, evaluation evidence, and recovery instructions without secrets or unauthorized truth. | REQ-001, REQ-002, REQ-018 |

Before implementation, user review must settle the authorization mechanism, role-assignment owner, evaluation custodian, storage and backup scope, retention lifecycle, and incident decision process. The runbook should reference these gate IDs and attach evidence rather than report the controls as present by default.
