"""พิสูจน์ slice ตัวอย่าง: catalog(contract) -> inventory preview -> replay harness

ใช้ adapter จริง (JSONL log บน tmp) + fake gateway แทน catalog เพื่อโฟกัส behavior
"""
from __future__ import annotations

import json

from shared.result import Outcome

from organs.inventory.adapters.jsonl_logger import JsonlLogger
from organs.inventory.domain.service import InventoryService


class _FakeCatalog:
    """แทน organ catalog ผ่าน contract เดียวกัน (ProductGateway.exists)."""
    port_name = "ProductGateway"

    def __init__(self, known: set[str]) -> None:
        self._known = known

    def exists(self, sku: str) -> bool:
        return sku in self._known


def _service(tmp_path, known={"apple", "banana"}):
    logger = JsonlLogger(tmp_path / "inventory.log.jsonl")
    return InventoryService(_FakeCatalog(known), logger), logger


def test_unknown_product_rejected_via_contract(tmp_path):
    service, _ = _service(tmp_path)
    res = service.adjust("ghost", 5)
    assert res.outcome is Outcome.REJECTED          # catalog ไม่มี -> ไม่เขียน


def test_preview_does_not_write(tmp_path):
    service, _ = _service(tmp_path)
    res = service.preview_adjust("apple", 10)
    assert res.ok and res.value == 10
    assert service.qty("apple") == 0                 # preview ไม่แตะ state
    assert not (tmp_path / "inventory.log.jsonl").exists()   # ไม่มี log ถูกเขียน


def test_negative_asks_before_writing(tmp_path):
    service, _ = _service(tmp_path)
    service.adjust("apple", 3)
    res = service.adjust("apple", -10)               # จะติดลบ
    assert res.outcome is Outcome.NEEDS_DECISION
    assert any(c.recommended for c in res.choices)
    assert service.qty("apple") == 3                 # ของเดิมไม่ถูกแก้


def test_replay_reconstructs_live_state(tmp_path):
    """replay harness: เล่น event log ซ้ำ -> ได้สถานะเท่ากับของจริง"""
    service, _ = _service(tmp_path)
    service.adjust("apple", 5, source="t")
    service.adjust("banana", 2, source="t")
    service.adjust("apple", 3, source="t")           # apple -> 8

    events = [json.loads(x) for x in
              (tmp_path / "inventory.log.jsonl").read_text(encoding="utf-8").splitlines()]
    rebuilt = InventoryService.replay(events)

    assert rebuilt == {"apple": 8, "banana": 2}
    assert rebuilt["apple"] == service.qty("apple")  # log คือแหล่งความจริง
