---
spec_id: <slug>
target_repository: <name>
target_repository_commit: <sha or tag>
source_spec: .reposkillopt/specs/repository-specification.md
skill_version: 0.1.0
adapter: <claude-code|codex|opencode|generic>
created: <YYYY-MM-DD>
status: draft
---

# Architecture View — <target_repository>

<!-- Built ON the Repository Specification. Every **[fact]** carries a resolvable `file:line`.
     C4-style levels. Mark unknowns **[unknown]**; never invent structure. -->

## Context
<!-- The system and the external actors/systems it talks to. Cite. -->

## Containers
<!-- Deployable/runtime units (service, worker, CLI, DB). One bullet each, cited. -->
- **[fact]** <container> — <responsibility> `path:line`.

## Components
<!-- Modules within containers. Every bullet MUST carry a citation (check_architecture_view). -->
- **[fact]** <component> — <role> `path:line`.

## Key sequences
<!-- 1+ end-to-end flows; cite at each hop. A mermaid sequenceDiagram is a visual aid (no citations). -->

## Dependency graph
<!-- Internal edges (A depends on B), each cited. mermaid `graph LR` visual + the cited edge list. -->
- **[fact]** <A> → <B> `path:line`.
