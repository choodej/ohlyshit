"""Adapter: เชื่อม inventory -> catalog ผ่าน contract (ProductGateway)

ไม่ import ภายในของ catalog เข้ามาใน domain; รับแค่ callable `lookup` ที่
composition root (app.py) เป็นคนเสียบให้ (เช่น catalog_repo.exists_label)
แบบนี้ inventory.domain ขึ้นกับ "interface" ไม่ใช่ตัว catalog ตรงๆ
"""
from __future__ import annotations

from typing import Callable

from ..ports.product_gateway import ProductGateway


class CatalogGateway(ProductGateway):
    def __init__(self, lookup: Callable[[str], bool]) -> None:
        self._lookup = lookup

    def exists(self, sku: str) -> bool:
        return bool(self._lookup(sku))
