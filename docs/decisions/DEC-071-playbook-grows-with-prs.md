# DEC-071: A pull request that settles an engineering practice updates the playbook in the same pull request

Status: Decided
Date: 2026-10-13

## Context

A playbook written after the fact loses the details. The owner asked for what
works and what does not, so each entry needs to say how sure it is.

## Decision

A pull request that settles an engineering practice updates
`docs/delivery-playbook.md` in the same pull request, and reviewers check that it
does. Each entry carries one status and says in general terms what the status
rests on:

- **Proven:** a merged test or a run shows that it works.
- **Proposed:** decided but not yet built.
- **Didn't work:** tried and dropped, with the reason.

The playbook does not cite pull requests. The link runs the other way: the
decision record or pull request that settles a practice names the playbook section
it updated.

## Alternatives considered

- Write the playbook in a retro at the end of the project. Lessons are lost by
  then.
- Link each entry to its pull request. The owner ruled that out.

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

- Question Q19 of the round, which proposed the same-pull-request update and the three statuses; the owner's comment on Q19 is recorded in DEC-070.
- Question Q22, which ruled out pull request references in the playbook.
- The agent then summarized Q1 to Q23 as one shared understanding, and the owner answered "works for me".
