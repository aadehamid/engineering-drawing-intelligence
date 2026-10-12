# DEC-042: W-SP starts with only the SCN-001 equivalent

Status: Decided
Date: 2026-10-12

## Context

Asked as Q30 (Which scenarios W-SP gets) in round 5 of the synthetic-data interview,
after DEC-015 to DEC-035.

## Decision

The owner accepted the recommendation given with Q30:

> Yes. That's what MILESTONE-001b needs, and it avoids hand-writing 16 scenarios
> for a second plant before anything uses them.

## Alternatives considered

- Write expected results for all 16 scenarios for W-SP before anything uses them.

## Owner's words

Asked as Q30 in round 5 of the synthetic-data interview on 2026-10-12. Markdown
formatting is removed from the quotes below.

> LIONG-006 writes SCN-001 to SCN-016 for R0. W-SP is a new plant (Q24), so it has
> no expected results yet. Should W-SP start with only the SCN-001 equivalent: its
> SmartPlant-style backend goes through DEXPI into the graph and must match the
> W-SP world file exactly? Other scenarios would extend to W-SP only when a
> milestone needs them for SmartPlant, each with its own expected results in the
> W-SP world file.

The recommendation given with it:

> Yes. That's what MILESTONE-001b needs, and it avoids hand-writing 16 scenarios
> for a second plant before anything uses them.

The owner answered:

> Agree on all

The answer covered every question in round 5, Q30 to Q34.

## Evidence

- LIONG-006, SCN-001.
