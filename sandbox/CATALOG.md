# CATALOG — system index (auto-generated, do not edit by hand)

Organs: 3

## catalog — Product Catalog
- status: `slice-proven` | version: `0.1.0`
- path: `organs/catalog`
- purpose: ทะเบียนสินค้า: เพิ่มสินค้า (sku/label) + กันชื่อซ้ำ — เป็น upstream ของ inventory
- ports: Repository, Logger, Inbound
- depends on: (independent)

## inventory — Inventory (preview + replay)
- status: `slice-proven` | version: `0.1.0`
- path: `organs/inventory`
- purpose: ปรับสต็อกสินค้า: ตรวจกับ catalog ผ่าน contract, preview ก่อนเขียน, สถานะสร้างใหม่ได้จาก event log (replay)
- ports: ProductGateway, Logger
- depends on: catalog

## registry — สมัครสมาชิก (Registration)
- status: `slice-proven` | version: `0.1.0`
- path: `organs/registry`
- purpose: รับคำสั่งสมัครสมาชิกผ่านช่องทางใดก็ได้ ตรวจซ้ำ แล้วบันทึก + log
- ports: MemberRepository, Logger, Inbound
- depends on: (independent)
