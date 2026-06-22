"""Composition root for organ 'inventory' — the only place wiring happens.

This is the example slice from RULES.md: catalog (contract) -> inventory preview
-> replay harness. The composition root is the ONLY place that knows both organs;
inventory's domain only ever sees the ProductGateway interface.

Run:
  python organs/inventory/app.py --demo
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_SANDBOX = Path(__file__).resolve().parents[2]
if str(_SANDBOX) not in sys.path:
    sys.path.insert(0, str(_SANDBOX))

from organs.catalog.adapters.jsonl_repository import JsonlRepository  # noqa: E402
from organs.inventory.adapters.catalog_gateway import CatalogGateway  # noqa: E402
from organs.inventory.adapters.jsonl_logger import JsonlLogger  # noqa: E402
from organs.inventory.domain.service import InventoryService  # noqa: E402

_DATA = _SANDBOX / "organs" / "inventory" / ".data"
_LOG = _DATA / "inventory.log.jsonl"


def build_service() -> InventoryService:
    # catalog is wired in ONLY here, as a lookup behind the ProductGateway port.
    catalog_repo = JsonlRepository(_SANDBOX / "organs" / "catalog" / ".data" / "catalog.jsonl")
    gateway = CatalogGateway(lookup=catalog_repo.exists_label)
    logger = JsonlLogger(_LOG)
    return InventoryService(gateway, logger)


def _demo() -> None:
    # seed the catalog so the products exist (normally done by the catalog organ)
    catalog_repo = JsonlRepository(_SANDBOX / "organs" / "catalog" / ".data" / "catalog.jsonl")
    from organs.catalog.domain.service import CatalogService
    from organs.catalog.adapters.jsonl_logger import JsonlLogger as CatLogger
    cat = CatalogService(catalog_repo, CatLogger(_SANDBOX / "organs" / "catalog" / ".data" / "catalog.log.jsonl"))
    for p in ("apple", "banana"):
        if not catalog_repo.exists_label(p):
            cat.submit(p, source="seed")

    if _LOG.exists():
        _LOG.unlink()                       # fresh demo run
    service = build_service()

    print("[demo] preview apple +10 (no write):",
          service.preview_adjust("apple", 10).value, "-> stored qty still",
          service.qty("apple"))
    print("[demo] commit apple +5  ->", service.adjust("apple", 5).value)
    print("[demo] commit banana +2 ->", service.adjust("banana", 2).value)
    over = service.adjust("apple", -99)     # would go negative -> asks
    print(f"[demo] commit apple -99 -> {over.outcome.value}: {over.question}")

    events = [json.loads(x) for x in _LOG.read_text(encoding="utf-8").splitlines()]
    print("[demo] replay log ->", InventoryService.replay(events),
          "(matches live state)")


if __name__ == "__main__":
    _demo()
