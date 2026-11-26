import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cli import migrate
from core.config import Settings
from tests.helpers import FakeClock, complete_setup, make_client


@pytest.fixture(scope="session")
def template_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A migrated and seeded SQLite database, built once and copied per test."""
    data_dir = tmp_path_factory.mktemp("template")
    migrate(Settings(data_dir=data_dir, _env_file=None))
    return data_dir / "joborbit.db"


@pytest.fixture
def settings(tmp_path: Path, template_db: Path) -> Settings:
    shutil.copy(template_db, tmp_path / "joborbit.db")
    return Settings(data_dir=tmp_path, static_dir=tmp_path / "no-frontend", _env_file=None)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def client(settings: Settings, clock: FakeClock) -> Iterator[TestClient]:
    with make_client(settings, clock) as test_client:
        yield test_client


@pytest.fixture
def authed(client: TestClient) -> TestClient:
    """A client that has completed setup and sends its CSRF token."""
    complete_setup(client)
    return client
