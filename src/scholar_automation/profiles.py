"""Profile management for scholarship automation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional


@dataclass(slots=True)
class UserProfile:
    """Represents the user whose information powers automation."""

    name: str
    email: str
    phone: Optional[str]
    gpa: Optional[float]
    major: Optional[str]
    school: Optional[str]
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_form_payload(self) -> Dict[str, str]:
        """Return a flattened mapping that can be used to fill generic forms."""
        payload: Dict[str, str] = {
            "name": self.name,
            "email": self.email,
        }
        if self.phone:
            payload["phone"] = self.phone
        if self.gpa is not None:
            payload["gpa"] = f"{self.gpa:.2f}"
        if self.major:
            payload["major"] = self.major
        if self.school:
            payload["school"] = self.school
        payload.update(self.metadata)
        return payload

    def matches_tags(self, tags: Iterable[str]) -> bool:
        """Return True when the profile matches the provided eligibility tags."""
        normalized_profile = {key.lower(): value.lower() for key, value in self.metadata.items()}
        normalized_profile.update({
            "major": (self.major or "").lower(),
            "school": (self.school or "").lower(),
        })
        for tag in tags:
            expected = tag.lower()
            if expected and expected not in normalized_profile.values():
                return False
        return True
