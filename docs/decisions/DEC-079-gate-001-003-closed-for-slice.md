# DEC-079: GATE-001 and the slice's part of GATE-003 are closed

Status: Decided
Date: 2026-10-18

## Context

[DEC-055](DEC-055-slice-choices-close-gates-on-evidence.md) says GATE-001 closes when
a pull request lands its closure evidence: pinned artifacts, a license record, and
positive and negative round-trip fixtures. The slice's part of GATE-003 closes when a
pull request lands the dependency lock and the compatibility tests. The rest of
GATE-003 stays open.

That evidence reached `main` in pull requests #34 to #39, for the slice's supported
subset, and [the decision register](../LIONG-REG-001-decisions.md) lists where each
piece lives. Those pull requests left both gates open, so that a separate pull request
could close them. The night run's summary of 2026-10-14 asked the owner whether to
close them, and recommended closing both if the owner accepted the build choices in
DEC-074 to DEC-077.

## Decision

GATE-001 is closed, and so is the slice's part of GATE-003. The evidence covers the
slice's supported subset. The rest of GATE-003 stays open, as DEC-055 says, and so do
the other gates in the register. A DEXPI validity claim still names every stage that
ran ([DEC-072](DEC-072-claim-names-every-stage-that-ran.md)).

## Alternatives considered

- Keep both gates open until the owner approves DEC-074 to DEC-077 one by one. DEC-055
  ties closure to landed evidence, not to approval of the build choices, and the owner
  chose to close.

## Owner's words

Asked on 2026-10-18 as the first of three questions after the night run of 2026-10-14.
The second asked the owner to review DEC-077's three least-settled choices (DEC-078),
and the third proposed a retro. The first asked whether to close GATE-001 and the
slice's part of GATE-003, with the agent's recommendation to close both in a short pull request that cites the evidence on main, if the owner
accepted the DEC-074 to DEC-077 choices. In their next reply the owner approved the
three DEC-077 choices put to them (DEC-078); DEC-074 to DEC-076 were not put to them
one by one.

The owner answered:

> close

## Evidence

- `standards/dexpi/2.0.1`: the pinned XSD, models and reference P&ID, with their
  checksums and license record ([DEC-074](DEC-074-dexpi-2-0-1-pinned-files.md)).
- R0, R1 and R2's generated DEXPI files, which pass all four validation stages and
  regenerate byte for byte, and `fixtures/dexpi-negative/cases.json`, whose cases each
  plant one fault and fail in the stage they name
  ([DEC-077](DEC-077-dexpi-mapping.md)).
- The exact pins in `pyproject.toml` and `uv.lock`, and the Neo4j image pinned by
  digest ([DEC-076](DEC-076-graph-publication.md)).
- The compatibility tests that run the whole slice in CI: one run publishes through
  Neo4j, and another reads the loaded SQL Server backend.
