from pathlib import Path
from types import TracebackType
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

SQLITE_PRAGMAS = (
    "journal_mode=WAL",
    "synchronous=NORMAL",
    "foreign_keys=ON",
    "busy_timeout=5000",
    "temp_store=MEMORY",
    "cache_size=-65536",
)


def create_db_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    engine = create_engine(url)

    if url.get_backend_name() == "sqlite":
        if url.database:
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)

        @event.listens_for(engine, "connect")
        def _set_pragmas(dbapi_connection: Any, _record: Any) -> None:
            cursor = dbapi_connection.cursor()
            for pragma in SQLITE_PRAGMAS:
                cursor.execute(f"PRAGMA {pragma}")
            cursor.close()

    return engine


class UnitOfWork:
    """One database session per unit of work.

    Changes are persisted only by an explicit `commit()`; leaving the block without
    committing (or with an exception) rolls everything back.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork is not active; use it as a context manager.")
        return self._session

    def __enter__(self) -> "UnitOfWork":
        self._session = self._session_factory()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        session = self.session
        try:
            session.rollback()
        finally:
            session.close()
            self._session = None

    def commit(self) -> None:
        self.session.commit()
