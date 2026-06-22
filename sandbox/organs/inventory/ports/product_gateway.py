"""Port: ทางที่ inventory ใช้ "ถาม" organ catalog ว่ามีสินค้านี้ไหม

inventory ไม่รู้จักภายในของ catalog เลย — คุยผ่าน interface นี้เท่านั้น (กฎข้อ 3)
ของจริงเสียบที่ adapters/catalog_gateway.py โดย composition root (app.py)
"""
from __future__ import annotations

from abc import abstractmethod

from shared.ports import Port


class ProductGateway(Port):
    @property
    def port_name(self) -> str:
        return "ProductGateway"

    @abstractmethod
    def exists(self, sku: str) -> bool:
        """สินค้านี้มีอยู่ใน catalog ไหม"""
        ...
