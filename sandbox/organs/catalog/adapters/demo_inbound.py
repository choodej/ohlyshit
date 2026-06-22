"""Adapter: in-memory inbound channel — drive the slice without any external service.

Proves the wiring works. Replace/add a real channel (e.g. Telegram) behind the
same Inbound port when ready.
"""
from __future__ import annotations

from typing import Callable, Iterable

from ..ports.inbound import Inbound, SubmitCommand


class DemoInbound(Inbound):
    def __init__(self, labels: Iterable[str]) -> None:
        self._labels = list(labels)

    def run(self, handle: Callable[[SubmitCommand], str]) -> None:
        for label in self._labels:
            reply = handle(SubmitCommand(label=label, source="demo"))
            print(f"[demo] submit {label!r} -> {reply}")
