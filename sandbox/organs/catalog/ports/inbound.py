"""Port: inbound channel for organ 'catalog' (Telegram / CLI / etc.).

Domain doesn't know any channel directly; an inbound adapter turns incoming
messages into a SubmitCommand.
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable

from shared.ports import Port


@dataclass(frozen=True)
class SubmitCommand:
    label: str
    source: str


class Inbound(Port):
    @property
    def port_name(self) -> str:
        return "Inbound"

    @abstractmethod
    def run(self, handle: Callable[[SubmitCommand], str]) -> None: ...
