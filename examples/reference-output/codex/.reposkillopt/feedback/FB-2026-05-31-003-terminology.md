---
id: FB-2026-05-31-003
timestamp: 2026-05-31T14:21:03Z
author: carol@example.com
type: terminology
references:
  - spec_id: click-8.1.7
    claim_ref: "## Domain model"
scope: repository-scoped
status: applied
---

# Feedback Item FB-2026-05-31-003

## Feedback

In Click's own documentation and in community usage, the term "**multi command**" is the umbrella term for any `BaseCommand` subclass that dispatches to subcommands — both `Group` and `CommandCollection`. The spec uses "Group" and "CommandCollection" without making clear that they share a common parent `MultiCommand`, which is the *concept* used in the public docs.

This is repository-specific vocabulary (Click's documentation says "multi command" in a way other CLI libraries do not). It belongs in the Repository Specification as a `**[human]**` note, but **must not** be promoted into the canonical skill — other libraries that the skill will be used against will have different (incompatible) ideas about what a "multi command" is.

## Suggested action

In `## Domain model`, add a `**[human]**` claim citing this Feedback Item that explains: Click uses "multi command" as the umbrella term for any `BaseCommand` that dispatches to subcommands; `Group` and `CommandCollection` are concrete `MultiCommand` subclasses; this is repo-specific vocabulary and should not be applied to other codebases.
