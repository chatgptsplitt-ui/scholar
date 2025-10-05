"""High-level orchestration for the scholarship automation workflow."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, List

from .discovery import Opportunity, ScholarshipDiscoveryEngine
from .forms import EssayPrompt, FieldDescriptor, FormInteractor, FormPlan
from .navigation import ApplicationNavigator
from .profiles import UserProfile
from .submission import SubmissionCandidate, SubmissionManager
from .transparency import TransparencyLogger


@dataclass
class AutomationConfig:
    seeds: Iterable[str]
    max_depth: int = 2
    max_results: int = 10


class AutomationController:
    """Coordinates discovery, navigation, form filling, and submission."""

    def __init__(
        self,
        profile: UserProfile,
        discovery: ScholarshipDiscoveryEngine,
        navigator: ApplicationNavigator,
        form_interactor: FormInteractor,
        submissions: SubmissionManager,
        logger: TransparencyLogger,
    ) -> None:
        self._profile = profile
        self._discovery = discovery
        self._navigator = navigator
        self._forms = form_interactor
        self._submissions = submissions
        self._logger = logger

    async def run(self) -> List[SubmissionCandidate]:
        opportunities = await self._discovery.discover(self._profile)
        await self._logger.log("Discovery completed", count=len(opportunities))
        for opportunity in opportunities:
            await self._process_opportunity(opportunity)
        return self._submissions.dashboard.submitted

    async def _process_opportunity(self, opportunity: Opportunity) -> None:
        await self._logger.log("Processing opportunity", title=opportunity.title)
        decisions = await self._navigator.run_until_blocked()
        await self._logger.log("Navigation decisions", count=len(decisions))
        plan = await self._build_form_plan()
        filled = await self._forms.execute_plan(plan, self._profile)
        candidate = SubmissionCandidate(
            opportunity_title=opportunity.title,
            application_url=opportunity.url,
            filled_fields=filled,
        )
        await self._submissions.add_candidate(candidate)

    async def _build_form_plan(self) -> FormPlan:
        snapshot = await self._navigator.snapshot()
        understanding_state = self._navigator.understanding.analyze(snapshot)
        fields = [
            FieldDescriptor(
                selector=field.selector,
                label=self._normalize_label(field.label),
                field_type=field.field_type,
            )
            for field in understanding_state.form_fields
        ]
        essays = [
            EssayPrompt(selector=prompt.selector, prompt=prompt.text or "", word_limit=None)
            for prompt in understanding_state.essay_prompts
        ]
        return FormPlan(fields=fields, essays=essays)

    @staticmethod
    def _normalize_label(label: str) -> str:
        sanitized = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
        mapping = {
            "full_name": "name",
            "first_name": "name",
            "last_name": "name",
            "email_address": "email",
            "phone_number": "phone",
            "telephone": "phone",
            "mobile": "phone",
            "grade_point_average": "gpa",
            "field_of_study": "major",
            "area_of_study": "major",
            "university": "school",
            "college": "school",
        }
        return mapping.get(sanitized, sanitized or label)
