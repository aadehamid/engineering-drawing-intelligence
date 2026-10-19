# DEC-087: The slice runner takes the backend as a parameter, and CI runs W-SP through SQL Server and Neo4j beside R0

Status: Decided
Date: 2026-10-19

## Context

MILESTONE-001b must run W-SP end to end as MILESTONE-001 runs R0
([DEC-042](DEC-042-w-sp-scn-001-first.md)): extraction from SQL Server or the snapshot
folder, DEXPI generation and validation, publication of one immutable Neo4j snapshot
([DEC-076](DEC-076-graph-publication.md)), the cross-sheet query with its evidence, and
the exact comparison with the answer key ([DEC-059](DEC-059-exact-answer-key-comparison.md)),
in `scripts/check.sh` and CI. [DEC-060](DEC-060-plain-python-orchestration.md) has one
script chain the steps. `scripts/run_slice.py` chained them for the Plant 3D-style
backend only. The agent decided how W-SP joins it during the MILESTONE-001b night run,
under the owner's delegation in [DEC-080](DEC-080-milestone-001b-night-delegation.md).
The owner can reverse it.

## Decision

1. **A parameter, not a second script.** `scripts/run_slice.py` takes
   `--backend p3d|sps`, with p3d the default so that R0's command is unchanged. Each
   backend names its extractor and its snapshot folder, `fixtures/p3d-r0` or
   `fixtures/sps-wsp`; every later step is the same code for both. An unknown backend
   is a usage error.
2. **The records name their origin.** A database run records
   `sqlserver:<database>/sps`, and a snapshot run `snapshot:fixtures/sps-wsp/W0`, as
   R0's runs name theirs.
3. **CI runs W-SP as it runs R0.** `scripts/test_run_slice.py`, which `scripts/check.sh`
   runs, takes W0 from the snapshot and scores it against W-SP's answer key; publishes
   it to Neo4j and checks the receipt and the cross-sheet query, TO-S2/B on
   DEMO-PID-101 to FROM-S1/B on DEMO-PID-102 with the two sheet-link rows as evidence;
   and loads W0 into a throwaway SQL Server database and runs the slice from it. The
   last two need the servers, so `scripts/require_ci_services.sh` keeps them from
   skipping in CI, as for R0.

## Alternatives considered

- A separate `run_slice_sps.py`. It would copy the steps that DEXPI makes the same for
  both backends, and the copies could drift apart.
- Choosing the backend from the revision name. R0's and W-SP's revision names do not
  overlap today, but nothing keeps them apart, and the command would hide which
  backend it reads.

## Owner's words

Given on 2026-10-19 (UTC) and recorded in
[DEC-080](DEC-080-milestone-001b-night-delegation.md): the owner chose the option the
agent offered for deciding this run's open questions.

The owner answered:

> Yes, decide for me

## Evidence

- `scripts/test_run_slice.py`: W0 matches W-SP's answer key exactly from the snapshot,
  from the command with `--backend sps`, after publication to Neo4j, and from SQL
  Server; the query returns the one cross-sheet pair with its evidence. Against SQL
  Server 2022 and Neo4j Community 2026.09.0 on 2026-10-19, none of these tests skipped.
- R0's slice tests pass unchanged.
