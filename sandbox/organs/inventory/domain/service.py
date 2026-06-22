"""InventoryService — ตัวอย่าง slice ที่โชว์ 3 แนวคิดของชุดนี้:

1) vertical slice ข้าม organ: ตรวจสินค้ากับ 'catalog' ผ่าน ProductGateway (contract)
2) preview-before-write: `preview_adjust` คำนวณผลลัพธ์ให้ดูก่อน "โดยไม่เขียนอะไรเลย"
   ถ้าจะทำให้สต็อกติดลบ -> คืน NEEDS_DECISION (ถามก่อน ไม่ทำมั่ว)
3) replay harness: สถานะสต็อกเป็นแค่ "ภาพฉาย" ของ event log (JSONL คือแหล่งความจริง)
   `replay(events)` สร้างสถานะกลับจาก log ได้ -> พิสูจน์ว่า log เชื่อถือได้

domain นี้ไม่ import I/O ใดๆ (ไม่รู้จัก JSONL/HTTP) — เทสได้เดี่ยว
"""
from __future__ import annotations

from shared.result import Choice, Result

from ..ports.logger import Logger
from ..ports.product_gateway import ProductGateway

ADJUSTED = "inventory.adjusted"


class InventoryService:
    def __init__(self, gateway: ProductGateway, logger: Logger,
                 stock: dict[str, int] | None = None) -> None:
        self._gateway = gateway
        self._logger = logger
        self._stock: dict[str, int] = dict(stock or {})

    def qty(self, sku: str) -> int:
        return self._stock.get(sku, 0)

    # --- preview: อ่านอย่างเดียว ไม่เขียน ไม่ log ------------------------- #
    def preview_adjust(self, sku: str, delta: int) -> Result[int]:
        if not self._gateway.exists(sku):
            return Result.reject(f"unknown product '{sku}' (not in catalog)")
        projected = self.qty(sku) + delta
        if projected < 0:
            return Result.decide(
                question=f"'{sku}' would go to {projected} (below zero). Proceed?",
                reason="would_go_negative",
                choices=[
                    Choice("cancel", "Cancel the adjustment", recommended=True),
                    Choice("clamp_zero", "Set it to 0 instead"),
                    Choice("force", "Allow negative stock anyway"),
                ],
            )
        return Result.succeed(projected)

    # --- commit: เขียน (ผ่าน log) เฉพาะเมื่อ preview ผ่าน ------------------ #
    def adjust(self, sku: str, delta: int, source: str = "unknown") -> Result[int]:
        preview = self.preview_adjust(sku, delta)
        if not preview.ok:
            return preview                       # reject / needs_decision -> ไม่เขียน
        projected = preview.value
        self._stock[sku] = projected
        self._logger.emit(ADJUSTED, sku=sku, delta=delta, qty=projected, source=source)
        return Result.succeed(projected)

    # --- replay harness: สร้างสถานะกลับจาก event log --------------------- #
    @staticmethod
    def replay(events: list[dict]) -> dict[str, int]:
        """fold เฉพาะ event 'inventory.adjusted' -> สถานะสต็อกล่าสุด"""
        stock: dict[str, int] = {}
        for ev in events:
            if ev.get("event") == ADJUSTED:
                stock[ev["sku"]] = ev["qty"]
        return stock
