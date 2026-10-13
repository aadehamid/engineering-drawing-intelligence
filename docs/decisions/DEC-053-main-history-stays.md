# DEC-053: Main's history stays as it is, with four commits authored by a test identity

Status: Decided
Date: 2026-10-13

## Context

Four commits on `main` carry the author "Test <test@example.com>": `e677c09`,
`8eaf105`, `a1fb19d` and `a9a993f`. A test identity leaked into a commit during
the night run of 2026-10-13. The content of all four is correct. Fixing the author
means rewriting the history of `main`, a protected branch, which the night run
left to the owner as a stop.

## Decision

The four commits stay on `main` as they are. Nobody rewrites `main`'s history to
change their author.

## Alternatives considered

- Rewrite `main` to give the four commits the owner's identity. Every clone and
  every recorded commit hash after `e677c09` would change, and the gain is only
  the author line.

## Owner's words

Asked as the first of three questions after the handoff of 2026-10-13: "Rewrite
main's history, or leave it?"

The owner answered:

> leave it

## Evidence

- `git log -1 --format='%an <%ae>' e677c09` prints `Test <test@example.com>`, and
  the same holds for `8eaf105`, `a1fb19d` and `a9a993f`.
