"""Bounded skill-edit proposals and their application to skill text.

Mirrors the six edit kinds from the canonical Skill Convergence Loop. The apply
step is deterministic and testable. ADD/REPLACE/DELETE are concrete; SPECIALIZE and
GENERALIZE are narrowing/broadening REPLACEs; REORDER replaces a block with a reordered
one. Repository-scoped proposals are rejected up front (only `generic` is eligible).
"""
from __future__ import annotations

from dataclasses import dataclass, field

EDIT_KINDS = {"ADD", "REPLACE", "DELETE", "REORDER", "SPECIALIZE", "GENERALIZE", "NONE"}


class ProposalError(ValueError):
    pass


@dataclass
class Proposal:
    edit_kind: str
    target_section: str = ""
    anchor: str = ""              # existing text to locate (REPLACE/DELETE/REORDER/ADD-after)
    payload: str = ""            # new text (ADD/REPLACE/SPECIALIZE/GENERALIZE/REORDER)
    expected_effect: str = ""
    rationale: str = ""
    scope: str = "generic"
    bump_level: str = "minor"
    supporting_feedback: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Proposal":
        kind = str(d.get("edit_kind", "")).upper()
        if kind not in EDIT_KINDS:
            raise ProposalError(f"invalid edit_kind: {d.get('edit_kind')!r}")
        return cls(
            edit_kind=kind,
            target_section=d.get("target_section", ""),
            anchor=d.get("anchor", ""),
            payload=d.get("payload", ""),
            expected_effect=d.get("expected_effect", ""),
            rationale=d.get("rationale", ""),
            scope=d.get("scope", "generic"),
            bump_level=d.get("bump_level", "minor"),
            supporting_feedback=list(d.get("supporting_feedback", [])),
        )

    @property
    def is_terminal(self) -> bool:
        return self.edit_kind == "NONE"

    def eligible(self) -> bool:
        """Only generic, non-terminal proposals are gate-eligible."""
        return not self.is_terminal and self.scope == "generic"

    def apply(self, text: str) -> str:
        """Return a new skill text with this edit applied. Raises if the anchor is missing."""
        if self.edit_kind == "NONE":
            return text
        if self.edit_kind == "ADD":
            if self.anchor:
                if self.anchor not in text:
                    raise ProposalError("ADD anchor not found")
                return text.replace(self.anchor, self.anchor + self.payload, 1)
            return text + self.payload
        if self.edit_kind in ("REPLACE", "SPECIALIZE", "GENERALIZE", "REORDER"):
            if not self.anchor or self.anchor not in text:
                raise ProposalError(f"{self.edit_kind} anchor not found")
            return text.replace(self.anchor, self.payload, 1)
        if self.edit_kind == "DELETE":
            if not self.anchor or self.anchor not in text:
                raise ProposalError("DELETE anchor not found")
            return text.replace(self.anchor, "", 1)
        raise ProposalError(f"unhandled edit_kind: {self.edit_kind}")
