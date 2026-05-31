# Contract — Held-out Reference Set (`rubric/held-out-set.md`)

**Scope**: The commit-pinned repositories reserved for gating, and the disjointness rule that keeps the gate honest (FR-007, FR-008).
**Consumers**: The gate procedure; gate reports; the maintainer.

## Required front matter

```yaml
---
released_version: <semver — the released skill version these baselines describe>
revised: <ISO date>
---
```

## Required sections

1. `## Members` — a table, ≥2 rows:

   | repo | commit | ecosystem | baseline_sheet |
   |---|---|---|---|
   | `owner/name` | `tag-or-sha` | e.g. python / js | `rubric/scoring/<repo>-<ver>-baseline.md` |

2. `## Exclusions` — repos barred from the held-out set because they motivate proposals. MUST list `pallets/click` (it motivated `FB-2026-05-31-002`, `FB-2026-06-01-004` → `SP-2026-06-01-001`).

3. `## Disjointness rule` — restates FR-008: for any proposal being gated, no held-out member may appear in that proposal's `supporting_feedback` repositories; otherwise the gate is `HELD`.

## Rules

- ≥2 members (FR-007); every `commit` is a specific tag or SHA (no floating refs).
- Each member has a baseline scoring sheet for `released_version` on record (FR-007).
- The set MUST NOT contain `pallets/click` (the project's primary motivating repo).
- Cross-ecosystem members are preferred (stronger no-regression signal) but not required.
- When `released_version` changes (a proposal is accepted and bumps the version), baselines are recomputed and `released_version`/`revised` updated (FR-007 re-baseline).

## Acceptance checklist

- [ ] ≥2 members, each commit-pinned.
- [ ] `pallets/click` is in `## Exclusions`, not in `## Members`.
- [ ] Every member has a baseline sheet at the referenced path for `released_version`.
- [ ] Disjointness rule stated and matches FR-008.
- [ ] `released_version` equals the canonical skill `version`.
