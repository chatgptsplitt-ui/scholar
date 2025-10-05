"""Dynamic form interaction utilities."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Protocol

from .profiles import UserProfile
from .transparency import TransparencyLogger


class FormDriver(Protocol):
    async def fill(self, selector: str, value: str) -> None:
        ...

    async def select(self, selector: str, value: str) -> None:
        ...

    async def check(self, selector: str, checked: bool = True) -> None:
        ...

    async def focus(self, selector: str) -> None:
        ...

    async def evaluate_field_type(self, selector: str) -> str:
        ...


@dataclass
class FieldDescriptor:
    selector: str
    label: str
    field_type: str | None = None


@dataclass
class EssayPrompt:
    selector: str
    prompt: str
    word_limit: int | None = None


@dataclass
class FormPlan:
    fields: List[FieldDescriptor]
    essays: List[EssayPrompt]


class EssayGenerator:
    """Generates essay content from the profile."""

    def __init__(self, profile: UserProfile) -> None:
        self._profile = profile

    def generate(self, prompt: EssayPrompt) -> str:
        payload = self._profile.as_form_payload()
        base = (
            f"My name is {self._profile.name} and I am pursuing {payload.get('major', 'my studies')} at "
            f"{payload.get('school', 'my university')} with a GPA of {payload.get('gpa', 'N/A')}.")
        reflection = f"This opportunity aligns with my passion for {payload.get('major', 'learning')} because {prompt.prompt[:120]}"
        essay = f"{base} {reflection}"
        if prompt.word_limit:
            return " ".join(essay.split()[: prompt.word_limit])
        return essay


class FormInteractor:
    """Coordinates the filling of dynamic forms."""

    def __init__(self, driver: FormDriver, logger: TransparencyLogger) -> None:
        self._driver = driver
        self._logger = logger

    async def execute_plan(self, plan: FormPlan, profile: UserProfile) -> Dict[str, str]:
        results: Dict[str, str] = {}
        payload = profile.as_form_payload()
        essay_generator = EssayGenerator(profile)
        for field in plan.fields:
            value = payload.get(field.label.lower()) or payload.get(field.label)
            if value is None:
                continue
            await self._apply_field(field, value)
            results[field.selector] = str(value)
        for essay in plan.essays:
            content = essay_generator.generate(essay)
            await self._driver.focus(essay.selector)
            await self._driver.fill(essay.selector, content)
            await self._logger.log("Essay generated", selector=essay.selector, preview=content[:80])
            results[essay.selector] = content
        return results

    async def _apply_field(self, field: FieldDescriptor, value: str) -> None:
        field_type = field.field_type or await self._driver.evaluate_field_type(field.selector)
        await self._logger.log("Filling field", selector=field.selector, field_type=field_type, value=value)
        if field_type in {"text", "textarea", "email", "number"}:
            await self._driver.fill(field.selector, value)
        elif field_type == "select":
            await self._driver.select(field.selector, value)
        elif field_type in {"checkbox", "radio"}:
            await self._driver.check(field.selector, True)
        else:  # fallback
            await self._driver.fill(field.selector, value)
        await asyncio.sleep(0)
