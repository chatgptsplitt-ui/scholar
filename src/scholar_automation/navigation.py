"""Adaptive multi-step navigation logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from .page_understanding import PageUnderstandingEngine, PageSnapshot
from .transparency import TransparencyLogger


class NavigableDriver(Protocol):
    async def click(self, selector: str) -> None:
        ...

    async def current_snapshot(self) -> PageSnapshot:
        ...


@dataclass
class NavigationDecision:
    action: str
    selector: str
    reason: str


class ApplicationNavigator:
    """Responsible for traversing complex multi-step application flows."""

    def __init__(self, driver: NavigableDriver, understanding: PageUnderstandingEngine, logger: TransparencyLogger) -> None:
        self._driver = driver
        self._understanding = understanding
        self._logger = logger

    @property
    def understanding(self) -> PageUnderstandingEngine:
        return self._understanding

    async def snapshot(self) -> PageSnapshot:
        return await self._driver.current_snapshot()

    async def advance(self) -> NavigationDecision | None:
        """Advance the application to the next step if possible."""
        snapshot = await self._driver.current_snapshot()
        state = self._understanding.analyze(snapshot)
        for action in state.available_actions:
            await self._logger.log("Navigating", action=action.label)
            await self._driver.click(action.selector)
            return NavigationDecision(action="click", selector=action.selector, reason=action.label)
        await self._logger.log("Navigation paused", reason="No actionable elements found")
        return None

    async def run_until_blocked(self, max_steps: int = 20) -> List[NavigationDecision]:
        decisions: List[NavigationDecision] = []
        for _ in range(max_steps):
            decision = await self.advance()
            if decision is None:
                break
            decisions.append(decision)
        return decisions
