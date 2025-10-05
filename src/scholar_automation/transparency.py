"""Transparency, logging, and feedback utilities."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class TransparencyEvent:
    timestamp: datetime
    message: str
    context: dict[str, object] = field(default_factory=dict)


class TransparencyLogger:
    """Collects events describing automation actions."""

    def __init__(self) -> None:
        self._events: List[TransparencyEvent] = []
        self._queue: asyncio.Queue[TransparencyEvent] = asyncio.Queue()

    async def log(self, message: str, **context: object) -> None:
        event = TransparencyEvent(timestamp=datetime.utcnow(), message=message, context=context)
        self._events.append(event)
        await self._queue.put(event)

    async def stream(self):  # pragma: no cover - convenience generator
        while True:
            event = await self._queue.get()
            yield event

    @property
    def events(self) -> List[TransparencyEvent]:
        return list(self._events)
