# Contract — Repository Specification (`.reposkillopt/specs/repository-specification.md`)

**Scope**: A Repository Specification produced by an agent following the canonical skill (or any adapter).
**Consumers**: Engineers reading the spec; reviewers scoring it via the rubric; future revisions of the same spec.

## Required front matter

```yaml
---
spec_id: <slug>
target_repository: <name>
target_repository_url: <url>            # optional if private
target_repository_commit: <sha or tag>
skill_version: <semver>
adapter: <claude-code|codex|opencode|generic>
created: <ISO date>
revised: <ISO date>
revision: <integer ≥ 1>
status: <draft|revised|superseded>
---
```

## Required sections (FR-005, in order)

1. `## Repository overview`
2. `## Technology stack`
3. `## Build and runtime commands`
4. `## Major entrypoints`
5. `## Architectural layers`
6. `## Core modules`
7. `## Domain model`
8. `## Data model`
9. `## External integrations`
10. `## Control-flow traces`
11. `## Data-flow traces`
12. `## Dependency map`
13. `## Configuration map`
14. `## Testing strategy`
15. `## Deployment assumptions`
16. `## Change-impact map`
17. `## Known risks`
18. `## Unknowns and unresolved questions`
19. `## Evidence index`

Optional appendix: `## Change log` (revision history).

## Claim and citation rules

- Every **major claim** (as defined in FR-008) MUST carry exactly one R10 prefix label: `**[fact]**`, `**[inference]**`, `**[unknown]**`, or `**[human]**`.
- Every `**[fact]**` claim MUST be immediately followed by at least one citation. Accepted citation forms:
  - `path/to/file.ext:line`
  - `path/to/file.ext:start-end`
  - `path/to/file.ext:Symbol`
  - `path/to/file.ext:Symbol:line`
  - `cmd: <executed command>` followed by `output: <verbatim output>` (for command-output evidence)
- `**[unknown]**` claims must also appear (or be listed by reference) under *Unknowns and unresolved questions* (FR-010).
- `**[human]**` claims MUST cite the originating Feedback Item id (e.g., `FB-2026-05-31-003`).
- The *Evidence index* MUST list every distinct citation appearing in the document, de-duplicated.

## Acceptance checklist

A Repository Specification passes when every item is true:

- [ ] Front matter present with all required keys and non-empty values.
- [ ] `skill_version` resolves to an existing canonical version.
- [ ] All 19 required sections are present, in order.
- [ ] No section is silently omitted (FR-005, SC-004); empty-by-design sections explicitly state "None known" or "Not applicable".
- [ ] Every major claim carries one of the four R10 labels (FR-008, SC-002 ≥ 90%).
- [ ] Every `**[fact]**` claim carries at least one citation in an accepted form (FR-009).
- [ ] At least 95% of `**[fact]**` citations resolve to an existing file in the target repository at the recorded commit (SC-003).
- [ ] `**[unknown]**` claims appear or are referenced under *Unknowns and unresolved questions*.
- [ ] `**[human]**` claims reference Feedback Item ids that exist under `.reposkillopt/feedback/`.
- [ ] *Evidence index* lists every distinct citation used in the document.
- [ ] On revision: prior `**[human]**` claims survive unless explicitly replaced; the change log records what changed.
- [ ] No claim presents a hypothesis as a fact (rubric: fact-vs-hypothesis distinction).
