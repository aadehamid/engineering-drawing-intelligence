# DEC-070: A general delivery playbook for engineering-data-to-graph projects lives in this repository

Status: Decided
Date: 2026-10-13

## Context

The owner asked for a playbook that another team could follow on a similar
project: general guidelines, best practices, what worked and what did not, and
how validation is done. LIONG-011, the build runbook, gives LIONG's own build
order and is not reusable as written.

## Decision

`docs/delivery-playbook.md` is a general guide for any team turning engineering
source data into a validated graph. It is listed in the documentation index and
moves out of this repository when a second project starts.

- **General.** It holds no project-specific items. Worked examples from this
  project are allowed, described in plain words, with no pull request numbers,
  decision-record IDs, file paths or links into this repository.
- **Engineering practice only.** How work flows, such as pull requests, reviews
  and decision records, stays in the way-of-working standard, which the playbook
  links to.
- **First version.** Four sections, all marked Proposed: choosing and pinning a
  standard, vendoring files from an unreliable host, staged validation, and
  synthetic worlds with hidden answer keys. A dated appendix holds notes on DEXPI
  as of 2026-10, because those facts concern the standard, not this project.

## Alternatives considered

- A separate repository now. The playbook grows next to the evidence that
  proves it, and moving it later costs little.
- A skill in personal-agent-skills. Skills hold rules for agents; this playbook
  is for people.

## Owner's words

Asked in round 4 of the decision round on 2026-10-13, which put questions
Q17 to Q21 about the playbook.

The owner answered:

> I agree on all except the ones with additional comments belw:
>
> Q19: No project specific items should be in the playbook.It should be a general guideline for team to follow to do project similar to this.
>
> Q20: It should not be project specific

In round 5:

The owner answered:

> Q22: A worked exmaple from this project is okay. But we dont need a PR in the Playbook
> Q23: I agree with your recommendation

## Evidence

- Questions Q17, Q18, Q20, Q21, Q22 and Q23 of the round, and the owner's comment on Q19, which set the rule that the playbook holds no project-specific items.
- The owner's request is quoted in [DEC-064](DEC-064-four-stage-dexpi-validation.md).
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
