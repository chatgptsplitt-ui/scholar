"""In-memory automation driver used for testing the automation pipeline."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .page_understanding import PageElement, PageSnapshot


@dataclass
class FakePage:
    url: str
    text: str
    links: List[Tuple[str, str]]
    elements: List[PageElement]
    form_values: Dict[str, str] = field(default_factory=dict)


class InMemoryDriver:
    """Implements all driver protocols using an in-memory representation."""

    def __init__(self, pages: Dict[str, FakePage], start_url: str) -> None:
        if start_url not in pages:
            raise ValueError("start_url must exist in pages")
        self._pages = pages
        self._current = pages[start_url]

    async def goto(self, url: str) -> None:
        await asyncio.sleep(0)
        if url not in self._pages:
            raise ValueError(f"Unknown URL: {url}")
        self._current = self._pages[url]

    async def extract_links(self) -> List[str]:
        await asyncio.sleep(0)
        return [target for _, target in self._current.links]

    async def extract_text(self) -> str:
        await asyncio.sleep(0)
        return self._current.text

    async def current_snapshot(self) -> PageSnapshot:
        await asyncio.sleep(0)
        return PageSnapshot(url=self._current.url, elements=list(self._current.elements))

    async def click(self, selector: str) -> None:
        await asyncio.sleep(0)
        for handle, target in self._current.links:
            if selector == handle or selector == target:
                await self.goto(target)
                return

    async def fill(self, selector: str, value: str) -> None:
        await asyncio.sleep(0)
        self._current.form_values[selector] = value

    async def select(self, selector: str, value: str) -> None:
        await self.fill(selector, value)

    async def check(self, selector: str, checked: bool = True) -> None:
        await self.fill(selector, "true" if checked else "false")

    async def focus(self, selector: str) -> None:
        await asyncio.sleep(0)

    async def evaluate_field_type(self, selector: str) -> str:
        await asyncio.sleep(0)
        for element in self._current.elements:
            if element.selector == selector:
                return element.role
        return "text"
