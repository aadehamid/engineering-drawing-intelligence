# DEC-088: A bounded PLM-RDL equipment mapping experiment precedes any vocabulary reuse

Status: Decided
Date: 2026-11-08

## Context

The reference register records POSC Caesar's PLM-RDL under
[REF-STD-012](../LIONG-REF-001-reference-register.md), with a downloadable,
license-stamped Turtle artifact (equipment module 0.9.1, CC BY-SA 4.0 stated in
the artifact), and reuse gates that an owner decision must close before any pin
or mapping lands. Following the 2026-11-08 TinyFish search that registered the
candidates, the agent recommended a bounded mapping experiment against the
PLM-RDL equipment terms as the strongest next step, and the owner approved the
recommendations.

## Decision

1. **An experiment, not an adoption.** The project pins
   `https://rds.posccaesar.org/ontology/plm/ont/equipment/0.9.1/plm-equipment.ttl`
   and its imports with SHA-256 hashes, and maps a bounded subset of its
   equipment terms against the equipment records the checks already validate
   (R0's and W-SP's). No graph entity in the published graph takes Brick,
   PLM-RDL, or any other external vocabulary as its class during the experiment.
2. **Read-only and self-contained.** Redistribution of the pinned file or of
   derived vocabulary is out of scope; CC BY-SA 4.0's share-alike applies only
   if a later adoption decision decides otherwise. The experiment writes no
   pipeline code into the checks; a mapping note and fixtures are its outputs.
3. **Evidence first.** The experiment's findings land in a reference-register
   note under REF-STD-012, and reuse then waits for its own owner decision. A
   merge of the experiment alone decides nothing.

## Alternatives considered

- Adopting PLM-RDL terms directly into the graph: rejected — no mapping evidence
  exists yet, and REF-STD-012's gates require a bounded mapping and an owner
  decision first.
- Doing nothing: rejected — the register would carry a strong candidate with no
  way to close or refute its mapping gate.
- Trying COPI's alignments instead: rejected for now — its claims are unverified
  ([DEC-089](DEC-089-registered-candidates-posture.md)), while REF-STD-012's
  artifact is pinned, hashed, and license-stamped.

## Owner's words

On 2026-11-08 (UTC), reviewing the agent's recommendations on the registered
ontology candidates and the PageIndex review:

The owner said:

> I like your recommendations. let us act on them.

## Evidence

- REF-STD-012: the inspected downloads, the pinned artifact candidate, its
  hashes, and the CC BY-SA 4.0 license triple recorded 2026-11-08.
- DEC-089: the posture for the other candidates, decided in the same owner
  message.
- The register's reuse-gate rules, which keep adoption closed until an owner
  decision.
