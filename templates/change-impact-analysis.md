---
target_repository: <name>
target_repository_commit: <sha>
target: <the proposed change / area>
created: <YYYY-MM-DD>
status: draft
---

# Change-Impact (blast-radius) Analysis — <target>

<!-- Given the target, what ripples. Every row carries a confidence label (high|medium|low) AND a
     citation (check_impact_analysis). Unresolvable impact → an [unknown] row with the reason. -->

## Affected modules
| Item | Why affected | Confidence | Evidence |
|------|--------------|------------|----------|
| <module> | <reason> | high | `path:line` |

## Affected tests
| Item | Why affected | Confidence | Evidence |
|------|--------------|------------|----------|

## Affected contracts / interfaces
| Item | Why affected | Confidence | Evidence |
|------|--------------|------------|----------|

## Affected call sites
| Item | Why affected | Confidence | Evidence |
|------|--------------|------------|----------|

## Unknowns
- **[unknown]** <impact that could not be statically resolved> — reason (dynamic dispatch, config-driven, …).
