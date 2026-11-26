from pathlib import Path

import pytest

from core.clock import SystemClock
from core.config import Settings


def test_database_url_defaults_into_data_dir(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path, _env_file=None)
    assert settings.database_url == f"sqlite:///{tmp_path.resolve() / 'joborbit.db'}"


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBORBIT_PORT", "9001")
    monkeypatch.setenv("JOBORBIT_DATABASE_URL", "sqlite:///custom.db")
    settings = Settings(_env_file=None)
    assert settings.port == 9001
    assert settings.database_url == "sqlite:///custom.db"
    assert settings.host == "127.0.0.1"


def test_system_clock_returns_aware_utc() -> None:
    now = SystemClock().now()
    assert now.utcoffset() is not None
    assert now.utcoffset().total_seconds() == 0  # type: ignore[union-attr]
