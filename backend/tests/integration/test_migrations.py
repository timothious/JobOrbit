import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from cli import ALEMBIC_INI

# Set to run the same checks on PostgreSQL, e.g. the dev database from deploy/postgres.compose.yml:
# postgresql+psycopg://joborbit:joborbit@127.0.0.1:55432/joborbit
POSTGRES_URL = os.environ.get("JOBORBIT_TEST_POSTGRES_URL")


def _config(url: str) -> Config:
    config = Config(ALEMBIC_INI)
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return config


@pytest.fixture(params=["sqlite", "postgresql"])
def database_url(request: pytest.FixtureRequest, tmp_path: Path) -> str:
    if request.param == "sqlite":
        return f"sqlite:///{tmp_path / 'migrations.db'}"
    if not POSTGRES_URL:
        pytest.skip("JOBORBIT_TEST_POSTGRES_URL not set")
    command.downgrade(_config(POSTGRES_URL), "base")  # start from an empty schema
    return POSTGRES_URL


def _tables(url: str) -> set[str]:
    engine = create_engine(url)
    try:
        return set(inspect(engine).get_table_names()) - {"alembic_version"}
    finally:
        engine.dispose()


def test_upgrade_downgrade_upgrade(database_url: str) -> None:
    config = _config(database_url)
    command.upgrade(config, "head")
    assert {
        "countries",
        "skills",
        "auth_sessions",
        "job_sources",
        "sync_logs",
        "user_profile",
    } <= _tables(database_url)

    command.downgrade(config, "base")  # every revision must be reversible
    assert _tables(database_url) == set()
    command.upgrade(config, "head")


def test_models_match_migrations(database_url: str) -> None:
    config = _config(database_url)
    command.upgrade(config, "head")
    command.check(config)  # raises if models and migrations have drifted


def test_one_active_sync_per_source(database_url: str) -> None:
    command.upgrade(_config(database_url), "head")
    engine = create_engine(database_url)
    insert_log = text(
        "INSERT INTO sync_logs (source_id, trigger, status, queued_at, http_requests, attempts,"
        " records_fetched, records_valid, records_invalid, jobs_created, jobs_updated, jobs_unchanged,"
        " duplicates_merged, jobs_marked_stale, jobs_expired, errors)"
        " VALUES (1, 'manual', :status, CURRENT_TIMESTAMP, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '[]')"
    )
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO job_sources (id, key, adapter_type, display_name, enabled, config,"
                    " credential_env_keys, fetch_interval_minutes, snapshot_mode, stale_after_hours,"
                    " expire_after_days, priority, coverage_countries, requires_link_back, health_status,"
                    " consecutive_failures, backoff_multiplier)"
                    " VALUES (1, 'remoteok', 'remoteok', 'RemoteOK', false, '{}', '[]', 60, 'full', 72, 7, 1,"
                    " '[]', true, 'never_run', 0, 1)"
                )
            )
            conn.execute(insert_log, {"status": "success"})
            conn.execute(insert_log, {"status": "queued"})
        with pytest.raises(Exception, match="(?i)unique"), engine.begin() as conn:
            conn.execute(insert_log, {"status": "running"})
    finally:
        engine.dispose()
