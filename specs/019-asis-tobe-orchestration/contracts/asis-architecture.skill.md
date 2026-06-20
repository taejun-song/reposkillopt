# Contract — `repo-architecture` skill (as-is)

- **Activation**: architecture-mapping / dependency-coupling-assessment / "what would change if we…".
  Vendor-neutral (description-only); MUST NOT name any coding-agent runtime in normative content.
- **Prerequisite**: a Repository Specification. If absent, the skill states the prerequisite and
  points to `repo-skillopt`; it MUST NOT fabricate an architecture.
- **Produces**: an **Architecture View** (`.reposkillopt/architecture/architecture-view.md`) and, on a
  named target, a **Change-Impact Analysis** (`.reposkillopt/impact/change-impact-analysis.md`), per
  `templates/architecture-view.md` and `templates/change-impact-analysis.md`.
- **Discipline**: R10 labels; every `[fact]` cites a resolvable `file:line`; every impact row carries a
  confidence label; unknowns `[unknown]` with reason — never silently dropped.
- **Deterministic checks** (gate): `check_architecture_view`, `check_impact_analysis` pass.
- **Rubric**: architectural correctness, evidence grounding, blast-radius completeness, confidence
  calibration, unknown honesty, level coherence (0–3 each).
- **Feedback**: corrections → Feedback Items applied in place; only candidate-for-generic patterns →
  gated Skill Edit Proposal. Mirrored to 4 adapters; carries `version:`/`canonical_version:`.
