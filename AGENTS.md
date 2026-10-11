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
2. Run the checks below and confirm they pass on `main`.

## Checks

Run these from the repository root before every push:

```sh
python3 scripts/bundle_docs.py --check
python3 scripts/check_docs.py
python3 scripts/test_doc_tools.py
```

The review archive in `docs/releases/` contains the root baseline files, every
`docs/*.md` file, and the three scripts. A change to any of them needs
`python3 scripts/bundle_docs.py` to rebuild the archive in the same commit.

## Decisions

The owner is Hamid (`aadehamid`). Decisions are proposals until his words are
recorded; [the decision register](docs/LIONG-REG-001-decisions.md) holds their state.

- Decision interviews use `/grill-with-docs`, which the owner starts.
- A question the owner skips in a decision round counts as agreement with the
  recommendation, and the record quotes the round. The owner's words are in
  DEC-014 of the decision register.
- A pull request merge alone does not approve draft proposals, unless the owner
  records that approval is the merge's intent and names its scope. A newer file is
  not more authoritative than an approved one.

## Terms

[GLOSSARY.md](GLOSSARY.md) owns project vocabulary. Use its terms exactly, and add a
term there when a decision resolves one.
