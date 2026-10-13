# LIONG engineering information

Terms for representing engineering information and its approved changes.

## Language

**Engineering-data reviewer**:
The role responsible for checking extracted engineering information and
accepting drawing-derived results for publication.

**Maintenance or process engineer**:
The role that uses published engineering information to investigate
connectivity and candidate isolation boundaries.

**Engineering-change approver**:
The role responsible for approving a proposed engineering modification,
distinct from accepting extraction results or authorizing real-world isolation.

**Engineering object**:
An identifiable item in the engineering model, such as equipment, a valve,
an instrument, a pipe segment, or a connection point.

**Tag**:
A contextual engineering label associated with an object and applicable
revisions. A tag is not the object's stable identity.
_Avoid_: Asset identity, unique global identifier

**Drawing appearance**:
A representation of an engineering object in a particular drawing.
An object can have more than one drawing appearance.

**Authoritative source**:
The declared source that governs engineering information for a dataset.

**System of authoring**:
The system in which engineering information is created or edited.

**System of record**:
The system holding authoritative information for a declared scope.

**System of reference**:
A connected representation used for queries and analysis without replacing
the authority of its source records.

**P&ID data product**:
The validated set of engineering objects and relationships prepared for
publication, including their provenance, identifiers, revisions, and review status.

**Layer 0**:
The engineering objects and connectivity behind P&IDs that form the foundation
for connected domain information.

**Accepted baseline**:
The initial engineering state accepted for subsequent comparison and change.
For drawing-only datasets, it consists of reviewed extraction results.

**Approved state**:
An engineering state whose required approval has been recorded.
Approval and publication are distinct: an approved source revision can fail graph validation.

**Published state**:
An accepted graph state that has passed the required validation and review.

**Proposed state**:
A candidate engineering state based on a named approved revision, kept
separate from approved information until explicitly approved.

**Management of Change record**:
A record of an engineering modification's reason, affected assets,
proposed revision, approval status, and approval history.
_Avoid_: Ingestion log

**Equipment bridge**:
The relationships that connect operational measurement identifiers to
the engineering assets they describe.

**Canonical world**:
The complete engineering truth for one synthetic facility, including its
revisions and intended errors. Every source representation is derived from it.
_Avoid_: Ground truth dataset, master data

**Source representation**:
One view of a canonical world as a particular source presents it, such as the
engineering backend, a drawing set, or a register. Each has its own record keys.

**World lineage**:
The family of artifacts derived from one canonical world: every rendering, source
representation, revision, crop, and perturbation. The canonical world's truth is
not a member. Data is partitioned by whole lineage; splitting only pages, tags,
file names, revisions, or raster variants does not make data independent.

**Vendor-style backend**:
A source representation whose schema follows one authoring product's storage
patterns, using original names. The SmartPlant-style and Plant 3D-style backends
are the two in this project.

**Supported subset**:
The DEXPI classes and properties this project generates and reads. Anything
outside it is reported as unsupported, never dropped silently.
