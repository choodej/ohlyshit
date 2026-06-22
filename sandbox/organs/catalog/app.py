"""Composition root for organ 'catalog' — the only place wiring happens.

Run:
  python organs/catalog/app.py --demo
"""
from __future__ import annotations

import sys
from pathlib import Path

_SANDBOX = Path(__file__).resolve().parents[2]
if str(_SANDBOX) not in sys.path:
    sys.path.insert(0, str(_SANDBOX))

from shared.result import Result  # noqa: E402

from organs.catalog.adapters.demo_inbound import DemoInbound  # noqa: E402
from organs.catalog.adapters.jsonl_logger import JsonlLogger  # noqa: E402
from organs.catalog.adapters.jsonl_repository import JsonlRepository  # noqa: E402
from organs.catalog.domain.service import CatalogService  # noqa: E402
from organs.catalog.ports.inbound import Inbound, SubmitCommand  # noqa: E402

_DATA = _SANDBOX / "organs" / "catalog" / ".data"


def build_service() -> CatalogService:
    repo = JsonlRepository(_DATA / "catalog.jsonl")
    logger = JsonlLogger(_DATA / "catalog.log.jsonl")
    return CatalogService(repo, logger)


def make_handler(service: CatalogService):
    def handle(cmd: SubmitCommand) -> str:
        result: Result = service.submit(cmd.label, source=cmd.source)
        if result.ok:
            return f"OK id={result.value.id} label={result.value.label}"
        if result.needs_decision:
            lines = [f"DECIDE: {result.question}"]
            for c in result.choices:
                mark = " *(recommended)" if c.recommended else ""
                lines.append(f"  - [{c.key}] {c.label}{mark}")
            return "\n".join(lines)
        return f"REJECTED: {result.reason}"

    return handle


def run(inbound: Inbound) -> None:
    inbound.run(make_handler(build_service()))


if __name__ == "__main__":
    run(DemoInbound(["sample_one", "sample_one", "x"]))
