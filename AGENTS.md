# Agent instructions

This repository holds the design package for LIONG's engineering drawing-to-graph
project. Start with [the documentation index](docs/LIONG-000-index.md), which owns
the reading order and which document is authoritative for what.

## Standing rules

- **Writing.** Before writing anything a person will read, load the `clear-writing`
  skill and follow it: every reply, status update, email, doc, README, commit and
  PR description, post, and any text the user asks to edit. It applies to subagents too.
- **Working on a repository.** Before changing anything, load the `way-of-working`
  skill and follow it: how decisions get recorded, the pull request every change
  goes through, the checks before each push, the independent review before a PR
  opens, watching an open PR until it merges, and the retro that improves the standard.

## Session start

1. Read this file, then check for open pull requests and watch each one to merge
   before starting unrelated work.
2. In a fresh clone, wire the pre-push hook once: `git config core.hooksPath scripts/hooks`.
   The checks need Python 3.12 and `uv`, which installs the locked dependencies in `uv.lock`.
3. Run `scripts/check.sh` and confirm it passes on `main`.

## Checks

`scripts/check.sh` runs every mechanical check. CI runs it on every pull request,
and the pre-push hook runs it before every push. It fails if any check changes a
tracked file, an untracked file that is not gitignored, the index, or git status.

The review archive in `docs/releases/` contains the root baseline files, every
`docs/*.md` and `docs/decisions/*.md` file, the three scripts, `pyproject.toml` and
`uv.lock`. A change to any
of them needs `uv run python scripts/bundle_docs.py` to rebuild the archive in the same
commit. The checks read Markdown with a CommonMark parser. Archived Markdown holds no
raw HTML outside code. Every relative link in it must point to another archived file
or to the archive itself, and no link target holds whitespace or a control character.

## Review

Reviewers apply [REVIEW_STANDARDS.md](REVIEW_STANDARDS.md) to every pull request,
alongside the way-of-working independent review.

## Figures and searches

Take every graph or document count a document quotes from
`uv run python scripts/liong_facts.py figures`, never from memory or a one-off script. Use its
`find` command for repo-wide searches; it matches text split across lines.

When you write a sentence that states a figure, register it in the tool's `CLAIMS` so
`check` verifies it; a number near "nodes" or "edges" that is not a figure goes in `EXEMPT`.
When a figure is missing, extend the tool and its tests.

## Decisions

The owner is Hamid (`aadehamid`). Decisions are proposals until his words are
recorded. [The decision register](docs/LIONG-REG-001-decisions.md) summarizes
approval state; [decision records](docs/decisions/README.md) hold one decision each,
with the owner's words quoted, in the format that index defines.

- Decision interviews use `/grill-with-docs`, which the owner starts.
- A question the owner skips in a decision round counts as agreement with the
  recommendation, and the record quotes the round
  ([DEC-014](docs/decisions/DEC-014-skipped-question-convention.md)).
- A pull request merge alone does not approve draft proposals, unless the owner
  records that approval is the merge's intent and names its scope. A newer file is
  not more authoritative than an approved one.

## Playbook

A pull request that settles an engineering practice updates
[the delivery playbook](docs/delivery-playbook.md) in the same pull request
([DEC-071](docs/decisions/DEC-071-playbook-grows-with-prs.md)). The playbook holds
no project-specific items: no pull request numbers, decision IDs or file paths
([DEC-070](docs/decisions/DEC-070-delivery-playbook.md)).

## Terms

[GLOSSARY.md](GLOSSARY.md) owns project vocabulary. Use its terms exactly, and add a
term there when a decision resolves one.
