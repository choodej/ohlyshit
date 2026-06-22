"""CatalogService — heart of organ 'catalog'.

Embedded rules:
  - validate input first
  - duplicate label / id -> do NOT overwrite silently; return NEEDS_DECISION
    with choices (ask before create) + a recommended option
  - every outcome is logged via the Logger port

This domain imports no I/O (no telegram/db/clickup). It is testable on its own.
Fill in real logic here; keep ports/adapters thin.
"""
from __future__ import annotations

from datetime import datetime, timezone

from shared.ids import new_id
from shared.result import Choice, Result

from ..ports.logger import Logger
from ..ports.repository import Repository
from .entity import Item


class CatalogService:
    def __init__(self, repo: Repository, logger: Logger) -> None:
        self._repo = repo
        self._logger = logger

    def submit(self, label: str, source: str = "unknown") -> Result[Item]:
        label = (label or "").strip()

        # 1) validate
        if not (3 <= len(label) <= 64):
            self._logger.emit("catalog.rejected", label=label, source=source,
                              reason="invalid_label")
            return Result.reject("label must be 3-64 characters")

        # 2) duplicate -> ask before creating
        if self._repo.exists_label(label):
            self._logger.emit("catalog.needs_decision", label=label, source=source,
                              reason="duplicate_label")
            return Result.decide(
                question=f"'{label}' already exists. What do you want to do?",
                reason="duplicate_label",
                choices=[
                    Choice("use_existing", "Use the existing one", recommended=True),
                    Choice("suggest_alt", f"Create a variant like '{label}_2'"),
                    Choice("force_new", "Create a new one anyway (different id)"),
                    Choice("cancel", "Cancel"),
                ],
            )

        # 3) unique id (guard against storage-level collision)
        item_id = new_id("cat")
        guard = 0
        while self._repo.exists_id(item_id):
            item_id = new_id("cat")
            guard += 1
            if guard > 5:
                self._logger.emit("catalog.rejected", label=label, source=source,
                                  reason="id_collision_exhausted")
                return Result.reject("could not allocate a unique id; try again")

        # 4) create + log
        item = Item(
            id=item_id,
            label=label,
            source=source,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._repo.save(item)
        self._logger.emit("catalog.created", id=item.id, label=item.label, source=source)
        return Result.succeed(item)
