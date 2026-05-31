---
id: FB-2026-05-31-002
timestamp: 2026-05-31T14:08:44Z
author: bob@example.com
type: missing-context
references:
  - spec_id: click-8.1.7
    claim_ref: "## Testing strategy"
scope: candidate-for-generic
status: applied
---

# Feedback Item FB-2026-05-31-002

## Feedback

The *Testing strategy* section enumerates the test files and notes the `runner` fixture, but it doesn't mention `tests/typing/` — a separate test surface that `pyright` runs against (per `tox.ini:24-28`). Missing this is a pattern I've seen on other Python libraries too: the canonical workflow inspects `tests/` and stops, missing `tests/typing/` (and analogues like `tests/integration/`, `tests/property/`, etc.) that are runner-specific.

For *this* repository, please mention `tests/typing/` and that it's exercised by `pyright tests/typing` (`tox.ini:28`).

For the canonical skill more broadly: the workflow could benefit from a step that explicitly looks for *non-pytest* test trees (typing, doctest, property, integration) so they're not silently dropped.

## Suggested action

1. **In this Repository Specification (now):** add `tests/typing/` to *Testing strategy*, citing `tox.ini:24-28`.
2. **Candidate for canonical (later):** consider a Skill Convergence proposal that adds, under *Repository Understanding Workflow* stage (c) "Inspect manifests, configs, tests, deployment files, and entrypoints", an explicit note to enumerate every `tests/*` subdirectory and not just the top-level test files.
