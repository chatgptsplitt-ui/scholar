"""Continuous page understanding and state modeling."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PageElement:
    selector: str
    role: str
    text: str
    visible: bool = True


@dataclass
class PageAction:
    selector: str
    label: str


@dataclass
class PageSnapshot:
    url: str
    elements: List[PageElement]


@dataclass
class PageState:
    snapshot: PageSnapshot
    available_actions: List[PageAction] = field(default_factory=list)
    form_fields: List[str] = field(default_factory=list)
    essay_prompts: List[PageElement] = field(default_factory=list)


class PageUnderstandingEngine:
    """Derives actionable insights from raw page snapshots."""

    def analyze(self, snapshot: PageSnapshot) -> PageState:
        actions = [
            PageAction(selector=element.selector, label=element.text)
            for element in snapshot.elements
            if element.visible and element.role in {"button", "link", "submit"} and element.text
        ]
        form_fields = [element.selector for element in snapshot.elements if element.role == "input" and element.visible]
        essay_prompts = [
            element
            for element in snapshot.elements
            if element.visible and element.role in {"textarea", "essay"} and "essay" in element.text.lower()
        ]
        return PageState(snapshot=snapshot, available_actions=actions, form_fields=form_fields, essay_prompts=essay_prompts)

    def has_review_summary(self, snapshot: PageSnapshot) -> bool:
        return any("review" in element.text.lower() for element in snapshot.elements if element.visible)
