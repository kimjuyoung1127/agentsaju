from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from saju_api import main as api_main
from saju_core.storage import SQLiteStorage


@pytest.fixture()
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture()
def chart_cases(fixture_dir: Path) -> list[dict[str, object]]:
    return json.loads((fixture_dir / "chart_cases.json").read_text(encoding="utf-8"))


@pytest.fixture()
def kasi_regression(fixture_dir: Path) -> dict[str, object]:
    return json.loads((fixture_dir / "kasi_regression.json").read_text(encoding="utf-8"))


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    api_main.storage = SQLiteStorage(tmp_path / "test.db")
    return TestClient(api_main.app)
