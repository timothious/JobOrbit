"""`joborbit` command: database migrations, reference data, and the dev server."""

import argparse
import json
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import sessionmaker

from catalog.seed import seed_reference_data
from core.config import Settings, get_settings
from core.db import UnitOfWork, create_db_engine

ALEMBIC_INI = Path(__file__).parent / "alembic.ini"


def migrate(settings: Settings) -> None:
    """Upgrade the schema to the latest revision, then load reference data."""
    config = Config(ALEMBIC_INI)
    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
    command.upgrade(config, "head")

    engine = create_db_engine(settings.database_url)
    with UnitOfWork(sessionmaker(engine)) as uow:
        seed_reference_data(uow.session)
        uow.commit()
    engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(prog="joborbit")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("migrate", help="apply database migrations and load reference data")
    sub.add_parser("dev", help="migrate, then run the API with auto-reload")
    sub.add_parser("openapi", help="print the OpenAPI schema (used to generate frontend types)")
    args = parser.parse_args()

    import main_api

    settings = get_settings()
    if args.command == "openapi":
        print(json.dumps(main_api.create_app(settings).openapi(), indent=1))
        return

    migrate(settings)
    print("Database is up to date.", file=sys.stderr)
    if args.command == "dev":
        main_api.serve(settings, reload=True)
