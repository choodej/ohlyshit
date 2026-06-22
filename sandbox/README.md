# sandbox

ที่เขียน/ทดลอง/พิสูจน์อวัยวะ ก่อนส่งเข้า `project/`

## โครงสร้าง (แม่แบบของทุกอวัยวะ)

```
sandbox/
  shared/                 # contract กลางที่ทุกอวัยวะใช้ร่วม
    result.py             # Result/Outcome — ปลอดภัย ไม่ throw มั่ว, รองรับ "ถามก่อนสร้าง"
    ids.py                # สร้าง id + ตรวจซ้ำ
    ports.py              # base Port (ABC)
    safety.py             # SafetyGate — กั้นทุก external write (dry-run + ขออนุมัติ)
  organs/
    registry/             # อวัยวะที่ 1 — สมัครสมาชิก
      domain/             # OOP core บริสุทธิ์ (ไม่รู้จัก telegram/db)
      ports/              # interface (ABC) ที่ domain ต้องการ
      adapters/           # ของจริง: jsonl, telegram, clickup
      tests/              # เทสว่าทำงานจริง
      app.py              # composition root — ต่อสายทุกชิ้นแล้วรัน slice
      manifest.json       # ข้อมูลอวัยวะ (graphify อ่านอันนี้)
  tools/
    graphify.py           # generate สารบัญ (CATALOG.md/graph.json/graph.mmd) + shadow detection
    token_compressor.py   # ย่อ context/state ให้ token น้อยลง (ไม่แตะ audit log)
```

## รัน

```bash
cd sandbox
python -m pip install -r requirements.txt      # pytest (+ python-telegram-bot ถ้าจะต่อจริง)
python -m pytest organs/registry/tests -q      # พิสูจน์อวัยวะทำงานจริง
python organs/registry/app.py --demo           # รัน slice แบบ demo (ไม่ต้องมี token)
python -m pytest -q                             # เทสทั้งหมด (organs + core utilities)
python tools/graphify.py                         # สร้างสารบัญ + ตรวจเงา (เพิ่ม --strict ให้ fail บน warning)
```

ต่อ Telegram จริง: ตั้ง `TELEGRAM_BOT_TOKEN` แล้ว `python organs/registry/app.py --telegram`

## เส้นตัวอย่างที่ 2: catalog → inventory (preview) → replay

โชว์แนวคิดครบชุดในเส้นเดียว (ดู RULES.md §8):
- `catalog` = ทะเบียนสินค้า (upstream)
- `inventory` ขึ้นกับ catalog **ผ่าน contract** (`ProductGateway`) ไม่แตะภายใน catalog
- `preview_adjust` = ดูผลลัพธ์ก่อน **โดยไม่เขียนอะไร**; ติดลบ → ถามก่อน (NEEDS_DECISION)
- **replay harness**: `InventoryService.replay(events)` สร้างสต็อกกลับจาก event log
  ล้วนๆ → พิสูจน์ว่า "log คือแหล่งความจริง, state เป็นแค่ภาพฉาย"

```bash
python organs/inventory/app.py            # เห็น preview -> commit -> ถามตอนติดลบ -> replay
python -m pytest organs/inventory -q      # 4 เทส รวม replay harness
python tools/graphify.py                  # เห็น edge inventory -> catalog ใน graph.mmd
```
