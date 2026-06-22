"""Item entity for organ 'catalog' — pure OOP core (knows nothing about I/O).

Rename/extend this to match your real domain object.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: str
    label: str
    source: str
    created_at: str  # ISO8601

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "source": self.source,
            "created_at": self.created_at,
        }
