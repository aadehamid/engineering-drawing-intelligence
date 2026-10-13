# DEC-065: A DEXPI validity claim names only the stages that ran, never conformance or certification

Status: Decided
Date: 2026-10-13

## Context

No official DEXPI 2.0 validator or certification exists for 2.0. A claim
broader than the checks that ran would mislead a reader.

## Decision

A document or report claims only the stages that ran. With all four stages of
DEC-064 it reads: valid against the DEXPI 2.0.1 XSD and the 2.0.1 Core and Plant
models for the classes LIONG uses, and passes LIONG's rules. If stage 3 is not built
yet, it reads: passes the DEXPI 2.0.1 XML schema and LIONG's rules. No claim says
DEXPI-conformant or certified.

## Alternatives considered

- Round 2's single wording, valid against the DEXPI 2.0.1 XSD and LIONG's
  subset rules. Round 3 sharpened it to name each stage.

## Owner's words

Asked in round 3 of the GATE-001 and GATE-003 decision round on 2026-10-13,
after the agent answered the owner's question about a staged DEXPI validation
proposal the owner had pasted in.

The owner answered:

> I am good. We probably should start a playbook as we build this out. So that we can start buinding out a generaal guidelien, best practices, what works and dont...how we do validation and so on  So that another team on anther project can execute the project with the playbook

## Evidence

- Questions Q10 and Q15 of the round.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
