from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from core.db import UnitOfWork, create_db_engine


@pytest.fixture
def session_factory(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'nested' / 'test.db'}")
    yield sessionmaker(engine)
    engine.dispose()


def test_sqlite_pragmas_are_applied(session_factory: sessionmaker[Session]) -> None:
    with UnitOfWork(session_factory) as uow:

        def pragma(name: str) -> object:
            return uow.session.execute(text(f"PRAGMA {name}")).scalar()

        assert pragma("journal_mode") == "wal"
        assert pragma("foreign_keys") == 1
        assert pragma("busy_timeout") == 5000


def test_only_committed_work_persists(
    session_factory: sessionmaker[Session],
) -> None:
    with UnitOfWork(session_factory) as uow:
        uow.session.execute(text("CREATE TABLE t (v INTEGER)"))
        uow.session.execute(text("INSERT INTO t VALUES (1)"))
        uow.commit()

    with UnitOfWork(session_factory) as uow:
        uow.session.execute(text("INSERT INTO t VALUES (2)"))

    with pytest.raises(RuntimeError), UnitOfWork(session_factory) as uow:
        uow.session.execute(text("INSERT INTO t VALUES (3)"))
        raise RuntimeError

    with UnitOfWork(session_factory) as uow:
        assert uow.session.execute(text("SELECT v FROM t")).scalars().all() == [1]


def test_session_unavailable_outside_the_block(session_factory: sessionmaker[Session]) -> None:
    uow = UnitOfWork(session_factory)
    with pytest.raises(RuntimeError):
        _ = uow.session
