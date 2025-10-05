"""Scholarship discovery engine."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable, List, Protocol

from .profiles import UserProfile
from .transparency import TransparencyLogger


class PageDriver(Protocol):
    """Protocol describing the subset of browser automation APIs we need."""

    async def goto(self, url: str) -> None:
        ...

    async def extract_links(self) -> List[str]:
        ...

    async def extract_text(self) -> str:
        ...


@dataclass
class Opportunity:
    """Represents a scholarship opportunity discovered on the web."""

    title: str
    url: str
    eligibility_tags: List[str]
    estimated_time_minutes: int

    def is_profile_match(self, profile: UserProfile) -> bool:
        return profile.matches_tags(self.eligibility_tags)


class ScholarshipDiscoveryEngine:
    """Discovers scholarship opportunities starting from seed URLs."""

    def __init__(
        self,
        driver: PageDriver,
        logger: TransparencyLogger,
        seeds: Iterable[str],
        *,
        max_depth: int = 2,
        max_results: int = 25,
    ) -> None:
        self._driver = driver
        self._logger = logger
        self._seeds = tuple(seeds)
        self._max_depth = max_depth
        self._max_results = max_results

    async def discover(self, profile: UserProfile) -> List[Opportunity]:
        """Explore the web to find scholarship opportunities."""
        discovered: List[Opportunity] = []
        seen_urls = set()
        queue = asyncio.Queue[tuple[str, int]]()
        for seed in self._seeds:
            await queue.put((seed, 0))

        while not queue.empty() and len(discovered) < self._max_results:
            url, depth = await queue.get()
            if url in seen_urls or depth > self._max_depth:
                continue
            seen_urls.add(url)
            await self._logger.log(f"Visiting {url}")
            await self._driver.goto(url)
            raw_text = await self._driver.extract_text()
            opportunity = self._parse_opportunity(url, raw_text)
            if opportunity and opportunity.is_profile_match(profile):
                await self._logger.log(f"Discovered matching opportunity: {opportunity.title}")
                discovered.append(opportunity)
            for link in await self._driver.extract_links():
                if link not in seen_urls:
                    await queue.put((link, depth + 1))
        return discovered

    def _parse_opportunity(self, url: str, raw_text: str) -> Opportunity | None:
        """Parse a scholarship opportunity from unstructured text."""
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        if not lines:
            return None
        title = lines[0]
        tags = [
            word.strip(".,:;!?")
            for line in lines[1:5]
            for word in line.split()
            if word.isalpha() and len(word) > 2
        ][:5]
        estimated_time = max(10, min(60, len(lines) // 2 * 5))
        return Opportunity(title=title, url=url, eligibility_tags=tags, estimated_time_minutes=estimated_time)
