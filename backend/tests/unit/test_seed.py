from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from catalog.models import Country, RegionMember, Skill
from catalog.seed import normalize_skill_name, seed_reference_data
from core.db import create_db_engine


def _session(db: Path) -> Session:
    return sessionmaker(create_db_engine(f"sqlite:///{db}"))()


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_seed_is_idempotent_and_keeps_user_data(template_db: Path, tmp_path: Path) -> None:
    db = tmp_path / "seed.db"
    db.write_bytes(template_db.read_bytes())
    with _session(db) as session:
        counts = (_count(session, Country), _count(session, RegionMember), _count(session, Skill))
        assert counts[0] == 249
        assert counts[2] >= 1000

        session.get_one(Country, "DE").english_status = "limited"
        session.add(Skill(name="My Niche Tool", normalized_name="my niche tool", is_system=False))
        session.commit()

        seed_reference_data(session)
        session.commit()

        assert (_count(session, Country), _count(session, RegionMember)) == counts[:2]
        assert _count(session, Skill) == counts[2] + 1
        assert session.get_one(Country, "DE").english_status == "limited"


def test_skill_names_are_normalized() -> None:
    assert normalize_skill_name("  Node.js ") == "node.js"
    assert normalize_skill_name("Machine_Learning   Ops") == "machine learning ops"
