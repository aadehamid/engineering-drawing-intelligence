# DEC-069: bpmn2dexpi is recorded as a candidate validator and kept out of the slice

Status: Decided
Date: 2026-10-13

## Context

The staged validation proposal the owner shared named bpmn2dexpi. It is an
MIT-licensed TypeScript tool whose `--validate` option checks existing DEXPI files,
including Plant files, against the XSD and the information models. It targets
DEXPI 2.0, not 2.0.1.

## Decision

bpmn2dexpi is recorded as the only third-party DEXPI 2.0 validator found. It
stays out of the slice and is looked at again when it supports 2.0.1. Its 2.0
models could report false failures on 2.0.1 content.

## Alternatives considered

- Run it once by hand on R0's generated file and record the result with its 2.0
  caveat.
- Add it to CI. That brings Node into the checks for a cross-check that cannot be
  trusted on 2.0.1 yet.

## Owner's words

Asked in round 3 of the GATE-001 and GATE-003 decision round on 2026-10-13,
after the agent answered the owner's question about a staged DEXPI validation
proposal the owner had pasted in.

The owner answered:

> I am good. We probably should start a playbook as we build this out. So that we can start buinding out a generaal guidelien, best practices, what works and dont...how we do validation and so on  So that another team on anther project can execute the project with the playbook

## Evidence

- REF-STD-010 in LIONG-REF-001.
- Question Q16 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
