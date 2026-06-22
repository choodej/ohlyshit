"""Port: storage for organ 'catalog'. Domain needs only this interface."""
from __future__ import annotations

from abc import abstractmethod

from shared.ports import Port

from ..domain.entity import Item


class Repository(Port):
    @property
    def port_name(self) -> str:
        return "Repository"

    @abstractmethod
    def exists_id(self, item_id: str) -> bool: ...

    @abstractmethod
    def exists_label(self, label: str) -> bool: ...

    @abstractmethod
    def save(self, item: Item) -> None: ...

    @abstractmethod
    def get(self, item_id: str) -> Item | None: ...
