"""One-click submission and review management."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .transparency import TransparencyLogger


@dataclass
class SubmissionCandidate:
    opportunity_title: str
    application_url: str
    filled_fields: Dict[str, str]


@dataclass
class SubmissionDashboard:
    candidates: List[SubmissionCandidate] = field(default_factory=list)
    submitted: List[SubmissionCandidate] = field(default_factory=list)


class SubmissionManager:
    """Stores completed applications and handles explicit submissions."""

    def __init__(self, logger: TransparencyLogger) -> None:
        self._dashboard = SubmissionDashboard()
        self._logger = logger

    async def add_candidate(self, candidate: SubmissionCandidate) -> None:
        self._dashboard.candidates.append(candidate)
        await self._logger.log("Candidate ready for review", opportunity=candidate.opportunity_title)

    async def submit_all(self) -> List[SubmissionCandidate]:
        while self._dashboard.candidates:
            candidate = self._dashboard.candidates.pop(0)
            self._dashboard.submitted.append(candidate)
            await self._logger.log("Submitted application", opportunity=candidate.opportunity_title)
        return list(self._dashboard.submitted)

    @property
    def dashboard(self) -> SubmissionDashboard:
        return self._dashboard
