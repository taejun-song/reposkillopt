---
id: FB-2026-05-31-001
timestamp: 2026-05-31T13:55:12Z
author: alice@example.com
type: correction
references:
  - spec_id: click-8.1.7
    claim_ref: "## Major entrypoints — public-API surface bullet for click.command"
scope: repository-scoped
status: applied
---

# Feedback Item FB-2026-05-31-001

## Feedback

The spec describes `click.command` as if the decorator factory itself is the entrypoint. In practice, the *user-facing* entrypoint is the resulting `Command` instance: after decoration, `foo = click.command()(foo)` makes `foo` callable as a CLI. The line citation in the spec (`decorators.py:171`) is correct for the factory definition, but the entrypoint section conflates two things — the decorator factory and the `Command` it produces.

It would also help to point at one example where a real entrypoint is wired up. `tests/test_basic.py` at line ~8 (`test_basic_functionality`) is the smallest example: a `@click.command def cli(): …` followed by `runner.invoke(cli, ...)`. That is what users actually do.

## Suggested action

In `## Major entrypoints`, distinguish:
- **Decorator factory** (`click.command` at `decorators.py:171`) — the function the user calls to *create* a Command.
- **Invocable Command instance** — what the user actually invokes; the decorator returns one (`decorators.py:241-249`).

And add a one-line pointer to `tests/test_basic.py:8-23` as the canonical smallest example of the full flow.
