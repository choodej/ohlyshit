"""Adapter: JSONL storage for organ 'catalog'. Swap for a DB later, same port."""
from __future__ import annotations

import json
from pathlib import Path

from ..domain.entity import Item
from ..ports.repository import Repository


class JsonlRepository(Repository):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, Item] = {}
        self._labels: set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        for line in self._path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            item = Item(**json.loads(line))
            self._index[item.id] = item
            self._labels.add(item.label.lower())

    def exists_id(self, item_id: str) -> bool:
        return item_id in self._index

    def exists_label(self, label: str) -> bool:
        return label.lower() in self._labels

    def save(self, item: Item) -> None:
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
        self._index[item.id] = item
        self._labels.add(item.label.lower())

    def get(self, item_id: str) -> Item | None:
        return self._index.get(item_id)
