# DEC-064: A DEXPI file is valid only when it passes four named validation stages and an exact round trip

Status: Decided
Date: 2026-10-13

## Context

No official DEXPI 2.0 validator exists, so the slice defines what valid means.
Round 2 proposed three checks. The owner then shared a staged validation proposal,
which separates the schema, the information models and project rules, and round 3
adopted it.

## Decision

A DEXPI file is valid only when it passes these four stages in order. Every
failure names its stage.

1. **Schema.** The file validates against the pinned DEXPI 2.0.1 XSD.
2. **References.** Every import maps to a pinned model file, and every
   file-local and named reference resolves.
3. **Model.** Against the pinned 2.0.1 Core and Plant models, for the classes
   LIONG writes: every class exists and is not abstract, every property is
   declared for its class with the right kind and data type, and every property
   has an allowed number of values.
4. **LIONG rules.** Rules that are LIONG's and not DEXPI's, such as unique tags,
   the answer key's equipment types and required units.

The file must also round-trip exactly: generate, parse and generate again, and the
two files match. Each SCN-005 negative fixture names the stage it must fail in. The
pull request that builds the validator proposes that mapping from the models'
required properties.

## Alternatives considered

- XSD validation alone. It checks the exchange format, not the engineering
  model.
- Round 2's three checks, with LIONG's subset rules in place of stages 2 to 4.
  They mixed DEXPI failures with LIONG's own rules.

## Owner's words

Asked in round 3 of the GATE-001 and GATE-003 decision round on 2026-10-13,
after the agent answered the owner's question about a staged DEXPI validation
proposal the owner had pasted in.

The owner answered:

> I am good. We probably should start a playbook as we build this out. So that we can start buinding out a generaal guidelien, best practices, what works and dont...how we do validation and so on  So that another team on anther project can execute the project with the playbook

## Evidence

- Questions Q10 and Q14 of the round.
- Round 2 answered by the owner with the words quoted in [DEC-061](DEC-061-dexpi-2-0-1.md).
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
