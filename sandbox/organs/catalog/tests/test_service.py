"""Smoke tests for organ 'catalog' — pass immediately after scaffolding.

Uses real JSONL adapters (no mocks) to prove the organ is wired correctly.
Extend these as you fill in real domain logic.
"""
from __future__ import annotations

import json

from shared.result import Outcome

from organs.catalog.adapters.jsonl_logger import JsonlLogger
from organs.catalog.adapters.jsonl_repository import JsonlRepository
from organs.catalog.domain.service import CatalogService


def _service(tmp_path):
    repo = JsonlRepository(tmp_path / "data.jsonl")
    logger = JsonlLogger(tmp_path / "log.jsonl")
    return CatalogService(repo, logger), repo


def test_submit_success_and_persisted(tmp_path):
    service, repo = _service(tmp_path)
    res = service.submit("hello_world", source="demo")
    assert res.ok
    assert res.value.id.startswith("cat_")
    assert repo.exists_label("hello_world")


def test_logging_happens(tmp_path):
    service, _ = _service(tmp_path)
    service.submit("logged_item", source="demo")
    events = [json.loads(x)["event"]
              for x in (tmp_path / "log.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "catalog.created" in events


def test_duplicate_asks_before_creating(tmp_path):
    service, _ = _service(tmp_path)
    service.submit("same_label", source="demo")
    res = service.submit("same_label", source="demo")
    assert res.outcome is Outcome.NEEDS_DECISION
    assert any(c.recommended for c in res.choices)
    lines = (tmp_path / "data.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1


def test_invalid_rejected(tmp_path):
    service, _ = _service(tmp_path)
    assert service.submit("x", source="demo").outcome is Outcome.REJECTED
