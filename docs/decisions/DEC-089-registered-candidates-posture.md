# DEC-089: The registered ontology candidates stay references, and the PageIndex demo is bounded to the synthetic fixtures

Status: Decided
Date: 2026-11-08

## Context

The 2026-11-08 reference-search round registered candidates
[REF-STD-012](../LIONG-REF-001-reference-register.md) through
[REF-STD-016](../LIONG-REF-001-reference-register.md); the technology round
added the PageIndex Page Search API with the steel-shop-drawing example
([REF-TECH-030](../LIONG-REF-001-reference-register.md)). The agent recommended
postures for the candidates that did not become the
[PLM-RDL mapping experiment](DEC-088-plm-rdl-mapping-experiment.md), and the
owner approved the recommendations.

## Decision

1. **CCO stays a reference.** REF-STD-013's decision question stands open:
   whether CCO with BFO serves this project as an upper or bridge layer, or as
   a reference only. Until the owner answers it, this record starts no
   alignment work.
2. **COPI stays on watch.** Its CC BY 4.0 license is recorded, but its ISO
   15926-4/CFIHOS/DEXPI alignment claims remain unverified. It is a source of
   mapping ideas for DEC-088's experiment, not a vocabulary to consume.
3. **OntoCAPE and PREMIS remain background references.** No experiment, mapping,
   or artifact pinning is owed to them.
4. **A PageIndex demo, bounded to the synthetic fixtures.** One trial of the
   Page Search API, within about one hour, answers a page-relevance question
   over a synthetic drawing set with the service's free credit, so the evidence
   stays synthetic. Nothing internal goes to the service, nothing is built on
   it, and — as this record's addition beyond the quoted recommendation — its
   terms, privacy, upload, and retention conditions are reviewed before any
   second use.
5. **No adoption is approved.** This decision approves postures and one demo
   only; every registered candidate keeps its reuse gates.

## Alternatives considered

- Starting a BFO/CCO alignment now: rejected — the CCO role question REF-STD-013
  records (upper or bridge layer, or reference only) is an owner decision this
  record leaves open, and starting an alignment would bypass that gate.
- Using COPI as the mapping's starting point: rejected — its alignment claims
  are unverified against artifacts.
- Treating the PageSearch demo as a capability to build on: rejected —
  REF-TECH-030 records a hosted service whose accuracy for P&IDs is unmeasured
  and whose terms are not read.

## Owner's words

On 2026-11-08 (UTC), after the reference-register round, the agent recommended, in
its own words in the session:

1. On CCO and BFO: "keep CCO as reference reading; revisit only when the
   shared-release question is settled. If that decision does land and wants a
   BFO-based upper layer, CCO is then the obvious candidate."
2. On COPI: "watch, don't adopt ... Its real near-term value is a source of
   mapping ideas for the PLM-RDL experiment."
3. On OntoCAPE and PREMIS: "leave as recorded."
4. On PageIndex: "a one-hour trial against the synthetic fixtures with the $5
   free credit would produce an honest 'does it find the right pages in a
   drawing set' data point. But it's a hosted third-party service — drawings only go up
   in synthetic, nothing-internal form, per the corpus rules, and its retention
   terms are unread. I wouldn't build anything on it yet."

The owner answered:

> I like your recommendations. let us act on them.

## Evidence

- REF-STD-012 through REF-STD-016 and REF-TECH-030: the candidates, their
  licenses, and their reuse gates as registered 2026-11-08.
- REF-STD-005 and REF-STD-004: the evidence-locator and measurement frames the
  demo and candidates relate to.
- DEC-088: the separate experiment decision approved in the same message.
