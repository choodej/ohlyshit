"""Port: logging for organ 'inventory' (backed by local JSONL, or external summary)."""
from __future__ import annotations

from abc import abstractmethod

from shared.ports import Port


class Logger(Port):
    @property
    def port_name(self) -> str:
        return "Logger"

    @abstractmethod
    def emit(self, event: str, **fields) -> None: ...
